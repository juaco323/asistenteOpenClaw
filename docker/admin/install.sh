#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
SOURCE_WORKSPACE="$REPO_ROOT/workspace-admin"
TARGET_STATE_DIR="${HOME}/.openclaw-admin"
ENV_FILE="$SCRIPT_DIR/.env"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Falta el comando requerido: $1" >&2
    exit 1
  }
}

require_cmd docker

docker compose version >/dev/null 2>&1 || {
  echo "Docker Compose v2 no esta disponible." >&2
  exit 1
}

mkdir -p "$TARGET_STATE_DIR"

# El contenedor monta workspace-admin desde el repo (ver docker-compose.yml).
rm -f "$SOURCE_WORKSPACE/BOOTSTRAP.md"

if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
  echo "Se creo $ENV_FILE a partir de .env.example" >&2
  echo "Editalo antes de volver a ejecutar install.sh" >&2
  exit 1
fi

if [[ -e "$TARGET_STATE_DIR/openclaw.json" ]] && [[ ! -s "$TARGET_STATE_DIR/openclaw.json" ]]; then
  rm -f "$TARGET_STATE_DIR/openclaw.json"
fi

echo "Descargando imagen y levantando stack Docker de admin..."
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" pull
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d

echo "Admin desplegado. Workspace: ${SOURCE_WORKSPACE} (montado en el contenedor)."
echo "Panel: http://127.0.0.1:<OPENCLAW_HOST_PORT>/ (valor en docker/admin/.env)."
