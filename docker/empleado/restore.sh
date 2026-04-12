#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
ARCHIVE="${1:-}"

if [ -z "$ARCHIVE" ]; then
  echo "Uso: $0 <archivo-backup.tgz>" >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "No existe $ENV_FILE. Ejecuta primero install.sh" >&2
  exit 1
fi

set -a
. "$ENV_FILE"
set +a

docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" down || true
tar -xzf "$ARCHIVE" -C "$(dirname "$OPENCLAW_STATE_DIR")"
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d

echo "Restore completado para empleado."
