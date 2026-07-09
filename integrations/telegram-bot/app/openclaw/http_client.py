from __future__ import annotations

import base64
import time
from pathlib import Path
from typing import Any

import httpx

from app.config import WorkspaceSettings
from app.llm_metrics import extract_usage_from_payload, record_llm_call
from app.workspace_policy import WorkspaceFilePolicy
from app.telegram_context import build_telegram_system_message

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
_IMAGE_MIME: dict[str, str] = {
    "jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp",
}


def _is_image_path(path: Path) -> bool:
    return path.suffix.lower() in _IMAGE_EXTENSIONS


def _build_user_content(message: str, image_path: Path | None) -> str | list:
    if image_path is None or not _is_image_path(image_path):
        return message
    try:
        data = base64.b64encode(image_path.read_bytes()).decode()
        mime = _IMAGE_MIME.get(image_path.suffix.lower().lstrip("."), "jpeg")
    except OSError:
        return message
    return [
        {"type": "text", "text": message},
        {"type": "image_url", "image_url": {"url": f"data:image/{mime};base64,{data}"}},
    ]


class GatewayOpenClawClient:
    def __init__(
        self,
        *,
        workspaces: dict[str, WorkspaceSettings],
        workspace_policies: dict[str, WorkspaceFilePolicy],
        timeout_seconds: float,
        metrics_data_dir: Path | None = None,
        metrics_exporter_url: str | None = None,
    ) -> None:
        self._workspaces = workspaces
        self._workspace_policies = workspace_policies
        self._metrics_data_dir = metrics_data_dir
        self._metrics_exporter_url = metrics_exporter_url
        self._client = httpx.AsyncClient(
            timeout=timeout_seconds,
            headers={"Content-Type": "application/json"},
        )

    async def chat(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
        message: str,
        chat_id: int | None = None,
        admin_validated: bool = False,
        image_path: Path | None = None,
    ) -> str:
        workspace_settings = self._get_workspace(workspace)
        policy = self._get_policy(workspace)
        telegram_chat_id = chat_id if chat_id is not None else user_id
        system_message = build_telegram_system_message(
            workspace=workspace,
            workspace_label=workspace_settings.label,
            chat_id=telegram_chat_id,
            user_id=user_id,
            username=username,
            policy=policy,
            admin_validated=admin_validated,
        )
        user_content = _build_user_content(message, image_path)
        return await self._send_chat_completion(
            workspace=workspace,
            user_id=user_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content},
            ],
        )

    async def list_reminders(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
    ) -> str:
        return await self._send_chat_completion(
            workspace=workspace,
            user_id=user_id,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Responde siempre en espanol, de forma concreta y profesional. "
                        "Si el entorno soporta recordatorios o tareas programadas, revisalos "
                        "y resume solo los activos del usuario. Si no existen o no se pueden "
                        "consultar desde este entorno, dilo claramente y no inventes datos."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Lista mis recordatorios activos en este workspace. "
                        f"Mi identificador externo es telegram:{user_id}. "
                        f"Mi usuario es {username or 'sin_username'}."
                    ),
                },
            ],
        )

    async def create_reminder(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
        content: str,
    ) -> str:
        return await self._send_chat_completion(
            workspace=workspace,
            user_id=user_id,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Responde siempre en espanol, de forma concreta y profesional. "
                        "Si el entorno soporta crear recordatorios o tareas programadas, hazlo. "
                        "Si no puedes persistir el recordatorio desde este entorno, di exactamente "
                        "que falta y no confirmes una creacion inexistente."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Quiero crear este recordatorio o tarea en este workspace:\n\n"
                        f"{content}\n\n"
                        f"Mi identificador externo es telegram:{user_id}. "
                        f"Mi usuario es {username or 'sin_username'}."
                    ),
                },
            ],
        )

    async def healthcheck(self, *, workspace: str) -> str:
        workspace_settings = self._get_workspace(workspace)
        response = await self._client.get(f"{workspace_settings.base_url}/healthz")
        response.raise_for_status()
        body = response.text.strip() or "ok"
        return f"{workspace_settings.label}: OK ({body})"

    async def _send_chat_completion(
        self,
        *,
        workspace: str,
        user_id: int,
        messages: list[dict[str, str]],
        source: str = "telegram",
    ) -> str:
        workspace_settings = self._get_workspace(workspace)
        user_preview = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str):
                    user_preview = content
                break
        t0 = time.perf_counter()
        ok = True
        usage: dict[str, Any] = {}
        try:
            response = await self._client.post(
                f"{workspace_settings.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {workspace_settings.gateway_token}",
                    "x-openclaw-agent-id": workspace_settings.agent_id,
                },
                json={
                    "model": "openclaw",
                    "user": f"telegram:{workspace}:{user_id}",
                    "messages": messages,
                },
            )

            if response.status_code in {401, 403}:
                raise RuntimeError(
                    f"{workspace_settings.label}: token invalido o sin permisos. "
                    "Revisa OPENCLAW_*_GATEWAY_TOKEN."
                )
            if response.status_code == 404:
                raise RuntimeError(
                    f"{workspace_settings.label}: falta habilitar /v1/chat/completions "
                    "en la configuracion del gateway."
                )
            if response.status_code >= 500:
                raise RuntimeError(
                    f"{workspace_settings.label}: el gateway devolvio HTTP "
                    f"{response.status_code}. {self._upstream_error_message(response)}"
                )
            response.raise_for_status()
            payload = response.json()
            usage = extract_usage_from_payload(payload)
            return self._extract_response_text(payload)
        except Exception:
            ok = False
            raise
        finally:
            if self._metrics_data_dir is not None:
                latency = time.perf_counter() - t0
                record_llm_call(
                    data_dir=self._metrics_data_dir,
                    workspace=workspace,
                    source=source,
                    latency_seconds=latency,
                    ok=ok,
                    model=usage.get("model"),
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                    input_preview=user_preview,
                    exporter_url=self._metrics_exporter_url,
                )

    @staticmethod
    def _upstream_error_message(response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            text = response.text.strip()
            return f"Detalle: {text[:300]}" if text else "Sin detalle en el cuerpo de la respuesta."
        error = body.get("error") if isinstance(body, dict) else None
        message = error.get("message") if isinstance(error, dict) else None
        if isinstance(message, str) and message.strip():
            return f"Mensaje del proveedor del modelo: {message.strip()}"
        return f"Cuerpo de la respuesta: {str(body)[:300]}"

    def _get_policy(self, workspace: str) -> WorkspaceFilePolicy:
        try:
            return self._workspace_policies[workspace]
        except KeyError as exc:
            raise RuntimeError(f"No file policy for workspace {workspace!r}.") from exc

    def _get_workspace(self, workspace: str) -> WorkspaceSettings:
        try:
            return self._workspaces[workspace]
        except KeyError as exc:
            available = ", ".join(self._workspaces.keys()) or "none"
            raise RuntimeError(
                f"Workspace {workspace!r} no configurado. Disponibles: {available}."
            ) from exc

    @staticmethod
    def _extract_response_text(payload: Any) -> str:
        if not isinstance(payload, dict):
            raise RuntimeError("OpenClaw devolvio una respuesta no valida.")

        choices = payload.get("choices", [])
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("OpenClaw no devolvio choices en la respuesta.")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise RuntimeError("OpenClaw devolvio un choice invalido.")

        message = first_choice.get("message", {})
        if not isinstance(message, dict):
            raise RuntimeError("OpenClaw devolvio un mensaje invalido.")

        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        text_parts.append(text.strip())
            if text_parts:
                return "\n".join(text_parts)

        raise RuntimeError("OpenClaw no devolvio texto util en la respuesta.")
