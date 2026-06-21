from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

LOGGER = logging.getLogger(__name__)
_lock = threading.Lock()


def _metrics_log_path(data_dir: Path) -> Path:
    return data_dir / "llm-metrics.jsonl"


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False) + "\n"
    with _lock:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)


def record_llm_call(
    *,
    data_dir: Path,
    workspace: str,
    source: str,
    latency_seconds: float,
    ok: bool,
    model: str | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    input_preview: str = "",
    exporter_url: str | None = None,
) -> None:
    row: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "workspace": workspace,
        "source": source,
        "latency_seconds": round(float(latency_seconds), 6),
        "model": model or "gpt-5.4",
        "input": input_preview[:500],
        "output": "",
        "extra": {"ok": ok},
    }
    if prompt_tokens is not None:
        row["prompt_tokens"] = int(prompt_tokens)
    if completion_tokens is not None:
        row["completion_tokens"] = int(completion_tokens)
    if total_tokens is not None:
        row["total_tokens"] = int(total_tokens)

    _append_jsonl(_metrics_log_path(data_dir), row)

    if not exporter_url:
        return
    try:
        with httpx.Client(timeout=2.0) as client:
            client.post(exporter_url.rstrip("/") + "/v1/record", json=row)
    except Exception as exc:  # pragma: no cover
        LOGGER.debug("No se pudo enviar métrica al exporter: %s", exc)


def extract_usage_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    usage = payload.get("usage") or {}
    out: dict[str, Any] = {}
    if isinstance(usage, dict):
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            val = usage.get(key)
            if val is not None:
                try:
                    out[key] = int(val)
                except (TypeError, ValueError):
                    pass
    model = payload.get("model")
    if isinstance(model, str) and model.strip():
        out["model"] = model.strip()
    return out
