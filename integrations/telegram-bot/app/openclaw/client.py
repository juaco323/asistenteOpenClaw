from __future__ import annotations

from typing import Protocol

from app.config import Settings

from .http_client import GatewayOpenClawClient
from .mock_client import MockOpenClawClient


class OpenClawClient(Protocol):
    async def chat(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
        message: str,
    ) -> str:
        ...

    async def list_reminders(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
    ) -> str:
        ...

    async def create_reminder(
        self,
        *,
        workspace: str,
        user_id: int,
        username: str | None,
        content: str,
    ) -> str:
        ...

    async def healthcheck(self, *, workspace: str) -> str:
        ...


def build_openclaw_client(settings: Settings) -> OpenClawClient:
    if settings.openclaw_mode == "gateway":
        return GatewayOpenClawClient(
            workspaces=settings.workspaces,
            timeout_seconds=settings.openclaw_request_timeout_seconds,
        )
    return MockOpenClawClient(storage_path=settings.data_dir / "mock_reminders.json")
