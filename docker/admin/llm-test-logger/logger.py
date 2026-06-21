#!/usr/bin/env python3
"""Ejecuta una llamada de prueba al gateway OpenClaw (perfil admin o empleado) y registra input/output/latencia."""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any

import httpx
from dotenv import load_dotenv

from oc import Tracker

# docker/admin/llm-test-logger/logger.py -> raíz del repo en parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[3]


def _paths_for_profile(profile: str) -> tuple[Path, Path]:
    if profile == "empleado":
        return (
            _REPO_ROOT / "docker" / "empleado" / ".env",
            _REPO_ROOT / "workspace-empleado" / ".llm-test-runs.jsonl",
        )
    return (
        _REPO_ROOT / "docker" / "admin" / ".env",
        _REPO_ROOT / "workspace-admin" / ".llm-test-runs.jsonl",
    )


def _load_env(env_file: Path) -> None:
    if env_file.is_file():
        load_dotenv(env_file, override=False)


def _resolve_gateway(profile: str) -> tuple[str, str, str]:
    """URL y token del gateway según perfil y variables ya cargadas en os.environ."""
    if profile == "empleado":
        base = (os.getenv("OPENCLAW_EMPLEADO_BASE_URL") or "").strip().rstrip("/")
        token = (
            (os.getenv("OPENCLAW_EMPLEADO_GATEWAY_TOKEN") or "").strip()
            or (os.getenv("OPENCLAW_GATEWAY_TOKEN") or "").strip()
        )
        agent_id = (os.getenv("OPENCLAW_EMPLEADO_AGENT_ID") or "main").strip() or "main"
    else:
        base = (os.getenv("OPENCLAW_ADMIN_BASE_URL") or "").strip().rstrip("/")
        token = (
            (os.getenv("OPENCLAW_ADMIN_GATEWAY_TOKEN") or "").strip()
            or (os.getenv("OPENCLAW_GATEWAY_TOKEN") or "").strip()
        )
        agent_id = (os.getenv("OPENCLAW_ADMIN_AGENT_ID") or "main").strip() or "main"

    if not base:
        port = (os.getenv("OPENCLAW_HOST_PORT") or "18789").strip()
        if port.isdigit():
            base = f"http://127.0.0.1:{port}"
    return base, token, agent_id


def _extract_usage(data: dict) -> dict[str, Any]:
    usage = data.get("usage") or {}
    if not isinstance(usage, dict):
        return {}
    out: dict[str, Any] = {}
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        val = usage.get(key)
        if val is not None:
            try:
                out[key] = int(val)
            except (TypeError, ValueError):
                pass
    model = data.get("model")
    if isinstance(model, str) and model.strip():
        out["model"] = model.strip()
    return out


def _chat_completion(
    *,
    base_url: str,
    token: str,
    agent_id: str,
    user_message: str,
    timeout: float,
    profile: str,
) -> tuple[str, dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": agent_id,
    }
    payload = {
        "model": "openclaw",
        "user": f"llm-test-logger:{profile}",
        "messages": [{"role": "user", "content": user_message}],
    }
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    usage = _extract_usage(data)
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("Respuesta sin choices.")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip(), usage
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
        if parts:
            return "\n".join(parts), usage
    raise RuntimeError("No se pudo extraer texto de la respuesta.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prueba LLM (admin|empleado) + Tracker JSONL.",
    )
    parser.add_argument(
        "--profile",
        choices=("admin", "empleado"),
        default=os.getenv("OPENCLAW_LLM_TEST_PROFILE", "admin"),
        help="Perfil de gateway y fichero .env (admin|empleado).",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Texto del prompt (o variables OPENCLAW_LLM_TEST_PROMPT, OPENCLAW_*_LLM_TEST_PROMPT en .env).",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Ruta del JSONL (por defecto workspace-<perfil>/.llm-test-runs.jsonl).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("OPENCLAW_LLM_TEST_TIMEOUT", os.getenv("OPENCLAW_ADMIN_LLM_TEST_TIMEOUT", "600"))),
    )
    args = parser.parse_args()

    env_path, default_log = _paths_for_profile(args.profile)
    _load_env(env_path)

    prompt = (args.prompt or "").strip()
    if not prompt:
        prompt = (
            (os.getenv("OPENCLAW_LLM_TEST_PROMPT") or "").strip()
            or (
                (os.getenv("OPENCLAW_EMPLEADO_LLM_TEST_PROMPT") or "").strip()
                if args.profile == "empleado"
                else (os.getenv("OPENCLAW_ADMIN_LLM_TEST_PROMPT") or "").strip()
            )
        )
    if not prompt:
        print(
            "Indica el prompt como argumento o una variable OPENCLAW_LLM_TEST_PROMPT / "
            "OPENCLAW_ADMIN_LLM_TEST_PROMPT / OPENCLAW_EMPLEADO_LLM_TEST_PROMPT en el .env del perfil.",
            file=sys.stderr,
        )
        return 2
    args.prompt = prompt

    log_path = args.log
    if log_path is None:
        raw = os.getenv("OPENCLAW_LLM_TEST_LOG") or (
            os.getenv("OPENCLAW_EMPLEADO_LLM_TEST_LOG")
            if args.profile == "empleado"
            else os.getenv("OPENCLAW_ADMIN_LLM_TEST_LOG")
        )
        log_path = Path(raw) if raw else default_log

    base_url, token, agent_id = _resolve_gateway(args.profile)
    if not base_url or not token:
        print(
            "Falta token o URL del gateway.\n"
            f"- Edita {env_path}: OPENCLAW_GATEWAY_TOKEN (y OPENCLAW_HOST_PORT).\n"
            f"- Opcional: OPENCLAW_{args.profile.upper()}_BASE_URL y OPENCLAW_{args.profile.upper()}_GATEWAY_TOKEN.",
            file=sys.stderr,
        )
        return 2

    tracker = Tracker(log_path)
    t0 = time.perf_counter()
    try:
        output, usage = _chat_completion(
            base_url=base_url,
            token=token,
            agent_id=agent_id,
            user_message=args.prompt,
            timeout=args.timeout,
            profile=args.profile,
        )
    except Exception as exc:  # noqa: BLE001 — script CLI
        latency = time.perf_counter() - t0
        tracker.record_run(
            input_text=args.prompt,
            output_text=f"<error: {exc!r}>",
            latency_seconds=latency,
            source="cli",
            workspace=args.profile,
            extra={"ok": False, "profile": args.profile},
        )
        print(str(exc), file=sys.stderr)
        return 1
    latency = time.perf_counter() - t0
    tracker.record_run(
        input_text=args.prompt,
        output_text=output,
        latency_seconds=latency,
        source="cli",
        workspace=args.profile,
        model=usage.get("model") or "gpt-5.4",
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
        extra={"ok": True, "profile": args.profile, **usage},
    )
    print("Registro completado. Revisa el panel de OpenClaw.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
