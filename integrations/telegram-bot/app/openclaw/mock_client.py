from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class MockOpenClawClient:
    def __init__(self, *, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

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
        identity = username or f"user-{user_id}"
        return (
            f"[{workspace}] OpenClaw aun no esta conectado. "
            f"Recibi el mensaje de {identity}: '{message}'. "
            "Cuando cambies a OPENCLAW_MODE=gateway, este comando enviara el texto al agente real."
        )

    async def list_reminders(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
    ) -> str:
        all_reminders = self._load_all()
        items = all_reminders.get(workspace, {}).get(str(user_id), [])
        if not items:
            return f"No hay recordatorios cargados en el workspace {workspace}."

        lines = [f"Recordatorios en {workspace}:"]
        for index, reminder in enumerate(items, start=1):
            lines.append(f"{index}. {reminder['content']} [{reminder['status']}]")
        return "\n".join(lines)

    async def create_reminder(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
        content: str,
    ) -> str:
        reminder = {
            "id": str(uuid4()),
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        all_reminders = self._load_all()
        workspace_items = all_reminders.setdefault(workspace, {})
        user_items = workspace_items.setdefault(str(user_id), [])
        user_items.append(reminder)
        self._save_all(all_reminders)
        return (
            f"Recordatorio creado en {workspace}.\n"
            f"- id: {reminder['id']}\n"
            f"- contenido: {reminder['content']}"
        )

    async def healthcheck(self, *, workspace: str) -> str:
        return f"{workspace}: modo mock activo"

    def _load_all(self) -> dict[str, dict[str, list[dict[str, str]]]]:
        if not self.storage_path.exists():
            return {}
        raw = self.storage_path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}

    def _save_all(self, data: dict[str, dict[str, list[dict[str, str]]]]) -> None:
        self.storage_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
