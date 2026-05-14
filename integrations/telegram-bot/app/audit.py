from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def append_file_audit(
    *,
    audit_path: Path,
    user_id: int,
    workspace: str,
    action: str,
    requested: str,
    resolved: str | None,
    allowed: bool,
) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "workspace": workspace,
        "action": action,
        "requested": requested,
        "resolved": resolved,
        "allowed": allowed,
    }
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
