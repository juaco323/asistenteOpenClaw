#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
SOURCE_WORKSPACE="$REPO_ROOT/workspace-empleado"
ENV_FILE="$SCRIPT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "No existe $ENV_FILE. Ejecuta primero install.sh" >&2
  exit 1
fi

set -a
. "$ENV_FILE"
set +a

mkdir -p "$OPENCLAW_WORKSPACE_DIR"
cp -a "$SOURCE_WORKSPACE/." "$OPENCLAW_WORKSPACE_DIR/"

docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" pull
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d

echo "Stack empleado actualizado y workspace sincronizado."
