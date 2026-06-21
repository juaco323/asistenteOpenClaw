from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from app.workspace_policy import WorkspaceFilePolicy, load_workspace_policies


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
    host_home: Path
    admin_llm_test_log_path: Path | None
    workspace_policies: dict[str, WorkspaceFilePolicy]
    workspace_passwords: dict[str, str]
    auth_max_attempts: int
    auth_lockout_seconds: int
    llm_metrics_exporter_url: str | None
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

    def get_policy(self, workspace: str) -> WorkspaceFilePolicy:
        try:
            return self.workspace_policies[workspace]
        except KeyError as exc:
            raise RuntimeError(f"No file policy configured for workspace {workspace!r}.") from exc

    def read_roots_for(self, workspace: str) -> list[Path]:
        return list(self.get_policy(workspace).read_roots)

    def write_roots_for(self, workspace: str) -> list[Path]:
        return list(self.get_policy(workspace).write_roots)

    def deny_roots_for(self, workspace: str) -> list[Path]:
        return list(self.get_policy(workspace).deny_roots)


WORKSPACE_LABELS = {
    "admin": "Administrador",
    "empleado": "Empleado",
}

DEFAULT_WORKSPACE_PASSWORDS = {
    "admin": "Admin1234*",
    "empleado": "Empleado1234*",
}

MAX_WORKSPACE_PASSWORD_ATTEMPTS_DEFAULT = 5


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

    timeout = float(os.getenv("OPENCLAW_REQUEST_TIMEOUT_SECONDS", "600").strip())
    sync_telegram_commands = _parse_bool(
        os.getenv("SYNC_TELEGRAM_COMMANDS", "true"),
        default=True,
    )

    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    host_home = Path(os.getenv("TELEGRAM_HOST_HOME", "/home/joaquin")).expanduser()

    _llm_log_raw = os.getenv("TELEGRAM_ADMIN_LLM_TEST_LOG_PATH", "").strip()
    admin_llm_test_log_path = Path(_llm_log_raw) if _llm_log_raw else None

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

    workspace_policies = load_workspace_policies(host_home)
    workspace_passwords = {
        "admin": os.getenv(
            "TELEGRAM_ADMIN_PASSWORD",
            DEFAULT_WORKSPACE_PASSWORDS["admin"],
        ),
        "empleado": os.getenv(
            "TELEGRAM_EMPLEADO_PASSWORD",
            DEFAULT_WORKSPACE_PASSWORDS["empleado"],
        ),
    }
    auth_max_attempts = int(
        os.getenv("TELEGRAM_AUTH_MAX_ATTEMPTS", str(MAX_WORKSPACE_PASSWORD_ATTEMPTS_DEFAULT)).strip()
    )
    auth_lockout_seconds = int(
        os.getenv("TELEGRAM_AUTH_LOCKOUT_SECONDS", "900").strip()
    )
    _exporter_raw = os.getenv("LLM_METRICS_EXPORTER_URL", "").strip()
    llm_metrics_exporter_url = _exporter_raw or None

    return Settings(
        telegram_bot_token=telegram_bot_token,
        allowed_user_ids=allowed_user_ids,
        allowed_usernames=allowed_usernames,
        openclaw_mode=openclaw_mode,
        openclaw_request_timeout_seconds=timeout,
        sync_telegram_commands=sync_telegram_commands,
        data_dir=data_dir,
        host_home=host_home,
        admin_llm_test_log_path=admin_llm_test_log_path,
        workspace_policies=workspace_policies,
        workspace_passwords=workspace_passwords,
        auth_max_attempts=auth_max_attempts,
        auth_lockout_seconds=auth_lockout_seconds,
        llm_metrics_exporter_url=llm_metrics_exporter_url,
        default_workspace=default_workspace,
        workspaces=workspaces,
    )
