#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

"$ROOT/scripts/ensure-dockerd.sh"
sudo chmod 666 /var/run/docker.sock 2>/dev/null || true

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Falta: $1" >&2
    exit 1
  }
}

require docker
docker compose version >/dev/null 2>&1 || {
  echo "Se requiere Docker Compose v2." >&2
  exit 1
}

for d in admin empleado telegram; do
  if [ ! -f "docker/$d/.env" ]; then
    echo "Falta docker/$d/.env (copia desde .env.example o usa scripts/apply-env-from-docx.sh)." >&2
    exit 1
  fi
done

compose_up() {
  local stack="$1"
  local extra=()
  if [ -f "docker/$stack/docker-compose.build-host.yml" ]; then
    extra+=(-f "docker/$stack/docker-compose.build-host.yml")
  fi
  if [ -f "docker/$stack/docker-compose.runtime-cloud.yml" ]; then
    extra+=(-f "docker/$stack/docker-compose.runtime-cloud.yml")
  fi
  docker compose --env-file "docker/$stack/.env" -f "docker/$stack/docker-compose.yml" "${extra[@]}" up -d --build
}

echo "== OpenClaw admin =="
compose_up admin

echo "== OpenClaw empleado =="
compose_up empleado

echo "== Bot Telegram =="
compose_up telegram

echo "Stack completo levantado (admin, empleado, Telegram)."
