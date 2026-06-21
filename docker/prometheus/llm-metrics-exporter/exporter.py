#!/usr/bin/env python3
"""Exportador Prometheus: latencia y tokens GPT desde JSONL de OpenClaw."""

from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

LATENCY = Histogram(
    "openclaw_llm_request_latency_seconds",
    "Latencia de extremo a extremo (gateway → respuesta)",
    ["workspace", "source", "model", "status"],
    buckets=(0.5, 1, 2, 5, 10, 20, 40, 60, 120, 300, 600),
)
REQUESTS = Counter(
    "openclaw_llm_requests_total",
    "Total de llamadas LLM registradas",
    ["workspace", "source", "model", "status"],
)
TOKENS = Counter(
    "openclaw_llm_tokens_total",
    "Tokens consumidos (prompt + completion)",
    ["workspace", "source", "model", "token_type"],
)

_seen: set[str] = set()
_lock = threading.Lock()


def _jsonl_paths() -> list[Path]:
    raw = os.getenv("LLM_METRICS_JSONL_PATHS", "").strip()
    if raw:
        return [Path(p.strip()) for p in raw.split(",") if p.strip()]
    repo = Path(os.getenv("OPENCLAW_REPO", "/repo"))
    paths = [
        repo / "workspace-admin" / ".llm-test-runs.jsonl",
        repo / "workspace-empleado" / ".llm-test-runs.jsonl",
        repo / "integrations" / "telegram-bot" / "data" / "llm-metrics.jsonl",
    ]
    extra = os.getenv("LLM_METRICS_EXTRA_JSONL", "").strip()
    if extra:
        paths.append(Path(extra))
    return paths


def _row_key(row: dict[str, Any]) -> str:
    return "|".join(
        str(row.get(k, ""))
        for k in ("ts", "source", "workspace", "latency_seconds", "input")
    )


def _ingest_row(row: dict[str, Any]) -> None:
    key = _row_key(row)
    with _lock:
        if key in _seen:
            return
        _seen.add(key)

    extra = row.get("extra") or {}
    if not isinstance(extra, dict):
        extra = {}

    workspace = str(row.get("workspace") or extra.get("profile") or "unknown")
    source = str(row.get("source") or "unknown")
    model = str(row.get("model") or extra.get("model") or "gpt-5.4")
    ok = extra.get("ok", True)
    status = "ok" if ok else "error"

    latency = float(row.get("latency_seconds") or 0)
    if latency > 0:
        LATENCY.labels(workspace, source, model, status).observe(latency)
    REQUESTS.labels(workspace, source, model, status).inc()

    for token_type, field in (
        ("prompt", "prompt_tokens"),
        ("completion", "completion_tokens"),
    ):
        val = row.get(field)
        if val is None:
            val = extra.get(field)
        if val is not None:
            try:
                TOKENS.labels(workspace, source, model, token_type).inc(int(val))
            except (TypeError, ValueError):
                pass


def _scan_jsonl_files() -> None:
    for path in _jsonl_paths():
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                _ingest_row(row)


def _background_scanner(interval: float) -> None:
    while True:
        _scan_jsonl_files()
        time.sleep(interval)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return
        if self.path.rstrip("/") == "/metrics":
            _scan_jsonl_files()
            payload = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/v1/record":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            row = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        if isinstance(row, dict):
            _ingest_row(row)
            persist = os.getenv("LLM_METRICS_PERSIST_PATH", "").strip()
            if persist:
                path = Path(persist)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        self.send_response(204)
        self.end_headers()


def main() -> None:
    port = int(os.getenv("LLM_METRICS_PORT", "9092"))
    interval = float(os.getenv("LLM_METRICS_SCAN_INTERVAL", "15"))
    thread = threading.Thread(target=_background_scanner, args=(interval,), daemon=True)
    thread.start()
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"llm-metrics-exporter listening on :{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
