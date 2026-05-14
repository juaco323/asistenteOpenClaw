from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "workspace-file-policy.yaml"


@dataclass(frozen=True)
class WorkspaceFilePolicy:
    name: str
    read_roots: tuple[Path, ...]
    write_roots: tuple[Path, ...]
    deny_roots: tuple[Path, ...]
    delete_forbidden_roots: tuple[Path, ...]
    delete_allowed: bool
    default_create_dir: Path


def _resolve_paths(host_home: Path, entries: list[str]) -> tuple[Path, ...]:
    resolved: list[Path] = []
    for entry in entries:
        raw = entry.strip()
        if not raw:
            continue
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = host_home / raw
        resolved.append(path)
    return tuple(resolved)


def _env_path_list(env_key: str) -> list[str] | None:
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return None
    return [item.strip() for item in raw.split(",") if item.strip()]


def _load_workspace_policy(workspace: str, host_home: Path, raw: dict) -> WorkspaceFilePolicy:
    section = raw.get(workspace, {})
    if not isinstance(section, dict):
        raise RuntimeError(f"Invalid policy section for workspace {workspace!r}.")

    read_env = _env_path_list(f"TELEGRAM_{workspace.upper()}_READ_ROOTS")
    write_env = _env_path_list(f"TELEGRAM_{workspace.upper()}_WRITE_ROOTS")
    deny_env = _env_path_list(f"TELEGRAM_{workspace.upper()}_DENY_ROOTS")
    legacy_env = _env_path_list(f"TELEGRAM_{workspace.upper()}_FILE_ROOTS")

    read_entries = read_env or legacy_env or list(section.get("read_roots", []))
    write_entries = write_env or list(section.get("write_roots", read_entries))
    deny_entries = deny_env or list(section.get("deny_roots", []))
    delete_forbidden_entries = list(section.get("delete_forbidden_roots", deny_entries))
    delete_allowed = bool(section.get("delete_allowed", False))

    default_raw = os.getenv(
        f"TELEGRAM_{workspace.upper()}_DEFAULT_CREATE_DIR",
        str(section.get("default_create_dir", "Documentos")),
    ).strip()
    default_path = Path(default_raw).expanduser()
    if not default_path.is_absolute():
        default_path = host_home / default_raw

    return WorkspaceFilePolicy(
        name=workspace,
        read_roots=_resolve_paths(host_home, read_entries),
        write_roots=_resolve_paths(host_home, write_entries),
        deny_roots=_resolve_paths(host_home, deny_entries),
        delete_forbidden_roots=_resolve_paths(host_home, delete_forbidden_entries),
        delete_allowed=delete_allowed,
        default_create_dir=default_path,
    )


def load_workspace_policies(host_home: Path) -> dict[str, WorkspaceFilePolicy]:
    if not POLICY_PATH.is_file():
        raise RuntimeError(f"Missing workspace file policy: {POLICY_PATH}")
    raw = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"Invalid workspace file policy format: {POLICY_PATH}")
    return {
        workspace: _load_workspace_policy(workspace, host_home, raw)
        for workspace in ("admin", "empleado")
    }
