#!/usr/bin/env python3
"""Exportador node_exporter-compatible con métricas simuladas.

Expone en /metrics las mismas series que consulta
docker/grafana/dashboards/openclaw-monitoreo-completo.json
(node_cpu_seconds_total, node_memory_*, node_load1), con valores
sintéticos que varían en el tiempo. El uso de RAM simulado se mantiene
siempre por debajo de 3 GiB.
"""

import http.server
import math
import random
import time

TOTAL_BYTES = 8 * 1024 ** 3  # host simulado de 8 GiB
RAM_CAP_BYTES = 3 * 1024 ** 3

_start = time.time()
_last_ts = _start
_idle_total = 0.0
_iowait_total = 0.0


def _tick_cpu_counters() -> None:
    global _idle_total, _iowait_total, _last_ts
    now = time.time()
    dt = now - _last_ts
    _last_ts = now
    t = now - _start

    usage_frac = 0.20 + 0.15 * math.sin(t / 90) + random.uniform(-0.03, 0.03)
    usage_frac = max(0.03, min(0.6, usage_frac))
    iowait_frac = max(0.0, 0.01 + 0.01 * math.sin(t / 50))

    _idle_total += dt * (1 - usage_frac)
    _iowait_total += dt * iowait_frac


def _memory_and_load() -> tuple[float, float, float, float, float]:
    t = time.time() - _start
    used = (1.1 + 0.8 * (0.5 + 0.5 * math.sin(t / 120))) * 1024 ** 3
    used += random.uniform(-0.05, 0.05) * 1024 ** 3
    used = max(1.0 * 1024 ** 3, min(0.95 * RAM_CAP_BYTES, used))

    available = TOTAL_BYTES - used
    cached = 0.3 * 1024 ** 3 + random.uniform(-0.02, 0.02) * 1024 ** 3
    buffers = 0.05 * 1024 ** 3
    load1 = max(0.02, 0.15 + 0.4 * (0.5 + 0.5 * math.sin(t / 90)) + random.uniform(-0.05, 0.05))
    return available, cached, buffers, load1, used


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return

        _tick_cpu_counters()
        available, cached, buffers, load1, _used = _memory_and_load()

        lines = [
            "# HELP node_cpu_seconds_total Seconds the CPU spent in each mode (simulado).",
            "# TYPE node_cpu_seconds_total counter",
            f'node_cpu_seconds_total{{cpu="0",mode="idle"}} {_idle_total:.3f}',
            f'node_cpu_seconds_total{{cpu="0",mode="iowait"}} {_iowait_total:.3f}',
            "# HELP node_memory_MemTotal_bytes Total memory (simulado).",
            "# TYPE node_memory_MemTotal_bytes gauge",
            f"node_memory_MemTotal_bytes {TOTAL_BYTES:.0f}",
            "# HELP node_memory_MemAvailable_bytes Available memory (simulado).",
            "# TYPE node_memory_MemAvailable_bytes gauge",
            f"node_memory_MemAvailable_bytes {available:.0f}",
            "# HELP node_memory_Cached_bytes Cached memory (simulado).",
            "# TYPE node_memory_Cached_bytes gauge",
            f"node_memory_Cached_bytes {cached:.0f}",
            "# HELP node_memory_Buffers_bytes Buffer memory (simulado).",
            "# TYPE node_memory_Buffers_bytes gauge",
            f"node_memory_Buffers_bytes {buffers:.0f}",
            "# HELP node_load1 1m load average (simulado).",
            "# TYPE node_load1 gauge",
            f"node_load1 {load1:.3f}",
        ]
        body = ("\n".join(lines) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    http.server.HTTPServer(("0.0.0.0", 9100), Handler).serve_forever()
