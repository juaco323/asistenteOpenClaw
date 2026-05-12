from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


def _parse_bool(value: str, *, default: bool) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return default
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"Invalid boolean value: {value!r}")


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class WorkspaceSettings:
    name: str
    label: str
    base_url: str
    gateway_token: str
    agent_id: str


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    allowed_user_ids: set[int]
    allowed_usernames: set[str]
    openclaw_mode: str
    openclaw_request_timeout_seconds: float
    sync_telegram_commands: bool
    data_dir: Path
    default_workspace: str | None
    workspaces: dict[str, WorkspaceSettings]

    def workspace_names(self) -> list[str]:
        return list(self.workspaces.keys())

    def get_workspace(self, name: str) -> WorkspaceSettings:
        try:
            return self.workspaces[name]
        except KeyError as exc:
            available = ", ".join(self.workspace_names()) or "none"
            raise RuntimeError(
                f"Unknown workspace {name!r}. Configured workspaces: {available}."
            ) from exc


WORKSPACE_LABELS = {
    "admin": "Administrador",
    "empleado": "Empleado",
}


def _load_workspace_settings(workspace_name: str) -> WorkspaceSettings | None:
    prefix = f"OPENCLAW_{workspace_name.upper()}_"
    base_url = os.getenv(f"{prefix}BASE_URL", "").strip().rstrip("/")
    gateway_token = os.getenv(f"{prefix}GATEWAY_TOKEN", "").strip()
    agent_id = os.getenv(f"{prefix}AGENT_ID", "main").strip() or "main"

    if not base_url and not gateway_token:
        return None
    if not base_url or not gateway_token:
        raise RuntimeError(
            f"{prefix}BASE_URL and {prefix}GATEWAY_TOKEN must both be set."
        )

    return WorkspaceSettings(
        name=workspace_name,
        label=WORKSPACE_LABELS[workspace_name],
        base_url=base_url,
        gateway_token=gateway_token,
        agent_id=agent_id,
    )


def load_settings() -> Settings:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not telegram_bot_token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN.")

    raw_ids = _parse_csv(os.getenv("TELEGRAM_ALLOWED_USER_IDS", ""))
    allowed_user_ids: set[int] = set()
    for raw_id in raw_ids:
        try:
            allowed_user_ids.add(int(raw_id))
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid TELEGRAM_ALLOWED_USER_IDS entry (must be integers): {raw_id!r}"
            ) from exc
    allowed_usernames = {
        username.lower()
        for username in _parse_csv(os.getenv("TELEGRAM_ALLOWED_USERNAMES", ""))
    }

    openclaw_mode = os.getenv("OPENCLAW_MODE", "mock").strip().lower() or "mock"
    if openclaw_mode not in {"mock", "gateway"}:
        raise RuntimeError("OPENCLAW_MODE must be either 'mock' or 'gateway'.")

    timeout = float(os.getenv("OPENCLAW_REQUEST_TIMEOUT_SECONDS", "20").strip())
    sync_telegram_commands = _parse_bool(
        os.getenv("SYNC_TELEGRAM_COMMANDS", "true"),
        default=True,
    )

    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    workspaces = {
        workspace_name: workspace
        for workspace_name in ("admin", "empleado")
        if (workspace := _load_workspace_settings(workspace_name)) is not None
    }

    default_workspace = (
        os.getenv("OPENCLAW_DEFAULT_WORKSPACE", "").strip().lower() or None
    )
    if default_workspace and default_workspace not in {"admin", "empleado"}:
        raise RuntimeError("OPENCLAW_DEFAULT_WORKSPACE must be 'admin' or 'empleado'.")

    if openclaw_mode == "gateway":
        if not workspaces:
            raise RuntimeError(
                "OPENCLAW_MODE=gateway requires at least one configured workspace."
            )
        if default_workspace and default_workspace not in workspaces:
            raise RuntimeError(
                "OPENCLAW_DEFAULT_WORKSPACE must reference a configured workspace."
            )

    return Settings(
        telegram_bot_token=telegram_bot_token,
        allowed_user_ids=allowed_user_ids,
        allowed_usernames=allowed_usernames,
        openclaw_mode=openclaw_mode,
        openclaw_request_timeout_seconds=timeout,
        sync_telegram_commands=sync_telegram_commands,
        data_dir=data_dir,
        default_workspace=default_workspace,
        workspaces=workspaces,
    )
