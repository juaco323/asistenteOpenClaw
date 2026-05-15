"""Tracker local para pruebas LLM (workspace admin). No confundir con el paquete PyPI `openclaw`."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = ["Tracker"]


class Tracker:
    """Registro silencioso en JSONL: input, output, latencia y marca temporal."""

    def __init__(self, log_path: Path) -> None:
        self._path = log_path.resolve()
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record_run(
        self,
        *,
        input_text: str,
        output_text: str,
        latency_seconds: float,
        source: str = "cli",
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
        with self._lock:
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line)
