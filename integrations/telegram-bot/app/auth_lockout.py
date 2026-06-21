from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LockoutStatus:
    locked: bool
    seconds_remaining: int
    attempts: int
    max_attempts: int


class AuthLockoutStore:
    """Bloqueo persistente tras intentos fallidos de contraseña de perfil (Telegram)."""

    def __init__(
        self,
        path: Path,
        *,
        max_attempts: int,
        lockout_seconds: int,
    ) -> None:
        self._path = path
        self._max_attempts = max(1, max_attempts)
        self._lockout_seconds = max(60, lockout_seconds)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return raw if isinstance(raw, dict) else {}

    def _save(self, data: dict[str, Any]) -> None:
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self._path)

    def _key(self, user_id: int) -> str:
        return str(user_id)

    def status(self, user_id: int) -> LockoutStatus:
        data = self._load()
        entry = data.get(self._key(user_id), {})
        if not isinstance(entry, dict):
            entry = {}
        attempts = int(entry.get("attempts", 0))
        locked_until = float(entry.get("locked_until", 0))
        now = time.time()
        if locked_until > now:
            return LockoutStatus(
                locked=True,
                seconds_remaining=int(locked_until - now) + 1,
                attempts=attempts,
                max_attempts=self._max_attempts,
            )
        return LockoutStatus(
            locked=False,
            seconds_remaining=0,
            attempts=attempts,
            max_attempts=self._max_attempts,
        )

    def ensure_can_attempt(self, user_id: int) -> LockoutStatus:
        status = self.status(user_id)
        if status.locked:
            return status
        return status

    def record_failure(self, user_id: int) -> LockoutStatus:
        data = self._load()
        key = self._key(user_id)
        entry = data.get(key, {})
        if not isinstance(entry, dict):
            entry = {}
        attempts = int(entry.get("attempts", 0)) + 1
        now = time.time()
        if attempts >= self._max_attempts:
            entry = {
                "attempts": attempts,
                "locked_until": now + self._lockout_seconds,
                "last_failure": now,
            }
        else:
            entry = {
                "attempts": attempts,
                "locked_until": 0,
                "last_failure": now,
            }
        data[key] = entry
        self._save(data)
        return self.status(user_id)

    def clear_user(self, user_id: int) -> None:
        data = self._load()
        key = self._key(user_id)
        if key in data:
            del data[key]
            self._save(data)

    def reset_attempts(self, user_id: int) -> None:
        """Reinicia contador al iniciar un nuevo flujo /workspace (sin quitar lockout activo)."""
        data = self._load()
        key = self._key(user_id)
        entry = data.get(key, {})
        if not isinstance(entry, dict):
            entry = {}
        locked_until = float(entry.get("locked_until", 0))
        now = time.time()
        if locked_until > now:
            return
        if key in data:
            del data[key]
            self._save(data)
