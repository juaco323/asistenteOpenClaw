#!/usr/bin/env python3
"""Panel HTTP de solo lectura para el histórico JSONL de pruebas LLM (admin o empleado)."""

from __future__ import annotations

import json
import os
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.environ.get("LLM_TEST_LOG_PATH", "/workspace/.llm-test-runs.jsonl"))
PAGE_TITLE = os.environ.get("LLM_TEST_PANEL_TITLE", "Histórico de pruebas LLM (workspace admin)")


def read_runs(limit: int = 500) -> list[dict]:
    if not ROOT.is_file():
        return []
    lines = ROOT.read_text(encoding="utf-8").splitlines()
    parsed: list[dict] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(parsed))


def _index_html() -> str:
    title = escape(PAGE_TITLE)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
body{{font-family:system-ui,sans-serif;margin:1.5rem;background:#0f1419;color:#e6edf3;}}
h1{{font-size:1.25rem;}}
table{{border-collapse:collapse;width:100%;font-size:0.85rem;}}
th,td{{border:1px solid #30363d;padding:0.45rem 0.5rem;vertical-align:top;}}
th{{background:#161b22;text-align:left;}}
.muted{{color:#8b949e;font-size:0.9rem;}}
.lat{{white-space:nowrap;color:#58a6ff;}}
pre{{white-space:pre-wrap;margin:0;max-height:14rem;overflow:auto;font-size:0.8rem;}}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="muted">Lee el JSONL generado por <code>oc.Tracker</code> (script <code>logger.py</code>). El Control UI
principal del gateway OpenClaw sigue en el puerto configurado en <code>OPENCLAW_HOST_PORT</code>.</p>
<table>
<thead><tr>
<th>Fecha (UTC)</th><th>Origen</th><th>Latencia (s)</th><th>Prompt</th><th>Respuesta</th>
</tr></thead>
<tbody id="rows"></tbody>
</table>
<script>
function tdText(text) {{
  const td = document.createElement('td');
  const pre = document.createElement('pre');
  pre.textContent = text == null ? '' : String(text);
  td.appendChild(pre);
  return td;
}}
function tdPlain(text) {{
  const td = document.createElement('td');
  td.textContent = text == null ? '' : String(text);
  return td;
}}
fetch('/api/runs')
  .then((r) => r.json())
  .then((rows) => {{
    const tb = document.getElementById('rows');
    for (const row of rows) {{
      const tr = document.createElement('tr');
      tr.appendChild(tdPlain(row.ts));
      tr.appendChild(tdPlain(row.source));
      const lat = document.createElement('td');
      lat.className = 'lat';
      lat.textContent = row.latency_seconds == null ? '' : String(row.latency_seconds);
      tr.appendChild(lat);
      tr.appendChild(tdText(row.input));
      tr.appendChild(tdText(row.output));
      tb.appendChild(tr);
    }}
  }});
</script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, _format: str, *_args) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            body = _index_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/runs":
            raw = json.dumps(read_runs()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        self.send_error(404)


def main() -> None:
    host = os.environ.get("LLM_TEST_PANEL_BIND", "0.0.0.0")
    port = int(os.environ.get("LLM_TEST_PANEL_PORT", "8080"))
    httpd = ThreadingHTTPServer((host, port), _Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
