#!/usr/bin/env bash
# Orquestador: levanta Prometheus y Grafana como stacks Docker independientes.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
echo "== Prometheus (contenedor dedicado) =="
"$ROOT/prometheus/install.sh"
echo ""
echo "== Grafana (contenedor dedicado) =="
"$ROOT/grafana/install.sh"
echo ""
echo "Monitoreo completo listo."
echo "  Prometheus: http://127.0.0.1:9090"
echo "  Grafana:    http://127.0.0.1:3000  → dashboard «OpenClaw — Monitoreo completo»"
