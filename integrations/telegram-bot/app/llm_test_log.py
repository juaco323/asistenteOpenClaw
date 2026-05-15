"""Registro JSONL de pruebas LLM (mismo esquema que docker/admin/llm-test-logger/oc.Tracker)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()


def append_llm_test_run(
    log_path: Path,
    *,
    input_text: str,
    output_text: str,
    latency_seconds: float,
    source: str = "telegram",
    extra: dict[str, Any] | None = None,
) -> None:
    row: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "source": source,
        "latency_seconds": round(float(latency_seconds), 6),
        "input": input_text,
        "output": output_text,
    }
    if extra:
        row["extra"] = extra
    line = json.dumps(row, ensure_ascii=False) + "\n"
    resolved = log_path.resolve()
    with _LOCK:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        with resolved.open("a", encoding="utf-8") as handle:
            handle.write(line)
