#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/docker/monitoring"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Creado docker/monitoring/.env — revisa contraseña de Grafana."
fi
docker compose --env-file .env up -d --build
echo "Monitoreo levantado:"
echo "  Grafana:    http://127.0.0.1:${GRAFANA_HOST_PORT:-3000}"
echo "  Prometheus: http://127.0.0.1:${PROMETHEUS_HOST_PORT:-9090}"
