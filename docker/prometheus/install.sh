#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Creado docker/prometheus/.env"
fi
docker compose --env-file .env up -d --build
echo "Prometheus: http://127.0.0.1:${PROMETHEUS_HOST_PORT:-9090}"
echo "LLM exporter metrics: http://127.0.0.1:${LLM_METRICS_HOST_PORT:-9092}/metrics"
