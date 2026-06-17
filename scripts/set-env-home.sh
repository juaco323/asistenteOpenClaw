#!/usr/bin/env bash
# Reescribe rutas de home y URLs de Telegram en docker/*/ .env
# Uso: ./scripts/set-env-home.sh [/home/joaquin]
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_HOME="${1:-/home/joaquin}"
TARGET_HOME="${TARGET_HOME%/}"

if [ ! -d "$TARGET_HOME" ] && [ "$TARGET_HOME" != "$HOME" ]; then
  echo "Aviso: $TARGET_HOME no existe aún en este host (se usará igual en los .env)." >&2
fi

rewrite_file() {
  local f="$1"
  [ -f "$f" ] || return 0
  sed -i \
    -e "s|/home/joaquin|${TARGET_HOME}|g" \
    -e "s|/home/fernanda2114t|${TARGET_HOME}|g" \
    -e "s|/home/ubuntu|${TARGET_HOME}|g" \
    "$f"
}

for f in docker/admin/.env docker/empleado/.env docker/telegram/.env; do
  rewrite_file "$ROOT/$f"
done

# PC local con Docker Desktop / Engine: el bot habla con los gateways por host.docker.internal
if [ -f "$ROOT/docker/telegram/.env" ]; then
  sed -i \
    -e 's|OPENCLAW_ADMIN_BASE_URL=http://127.0.0.1:|OPENCLAW_ADMIN_BASE_URL=http://host.docker.internal:|g' \
    -e 's|OPENCLAW_EMPLEADO_BASE_URL=http://127.0.0.1:|OPENCLAW_EMPLEADO_BASE_URL=http://host.docker.internal:|g' \
    "$ROOT/docker/telegram/.env"
fi

echo "Rutas actualizadas a ${TARGET_HOME} en docker/admin|.env, docker/empleado/.env y docker/telegram/.env"
echo "Telegram: OPENCLAW_*_BASE_URL → host.docker.internal (PC local)"
