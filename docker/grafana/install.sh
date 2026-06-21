#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Creado docker/grafana/.env — cambia GRAFANA_ADMIN_PASSWORD en producción."
fi
docker compose --env-file .env up -d
echo "Grafana: http://127.0.0.1:${GRAFANA_HOST_PORT:-3000}"
echo "Dashboard: OpenClaw — Monitoreo completo (CPU/RAM host y contenedores)"
