#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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
    echo "Falta docker/$d/.env (copia desde .env.example de cada carpeta)." >&2
    exit 1
  fi
done

echo "== OpenClaw admin =="
docker compose --env-file docker/admin/.env -f docker/admin/docker-compose.yml up -d

echo "== OpenClaw empleado =="
docker compose --env-file docker/empleado/.env -f docker/empleado/docker-compose.yml up -d --build

echo "== Bot Telegram =="
docker compose --env-file docker/telegram/.env -f docker/telegram/docker-compose.yml up -d --build

echo "Stack completo levantado (admin, empleado, Telegram). Puertos: OPENCLAW_HOST_PORT en docker/admin/.env y docker/empleado/.env."
