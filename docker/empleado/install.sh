#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
SOURCE_WORKSPACE="$REPO_ROOT/workspace-empleado"
TARGET_STATE_DIR="${HOME}/.openclaw-empleado"
TARGET_WORKSPACE_DIR="$TARGET_STATE_DIR/workspace"
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

mkdir -p "$TARGET_STATE_DIR" "$TARGET_WORKSPACE_DIR"

if [ -d "$SOURCE_WORKSPACE" ]; then
  cp -a "$SOURCE_WORKSPACE/." "$TARGET_WORKSPACE_DIR/"
fi

# Si queda BOOTSTRAP.md (p. ej. copia manual desde el repo OpenClaw), el gateway
# prioriza "definir identidad en chat" y ignora SOUL.md/IDENTITY.md del perfil oficina.
rm -f "$TARGET_WORKSPACE_DIR/BOOTSTRAP.md"

if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
  echo "Se creo $ENV_FILE a partir de .env.example" >&2
  echo "Editalo antes de volver a ejecutar install.sh" >&2
  exit 1
fi

# Archivo openclaw.json vacío en el estado choca con el bind mount de ./openclaw.json del compose.
if [[ -e "$TARGET_STATE_DIR/openclaw.json" ]] && [[ ! -s "$TARGET_STATE_DIR/openclaw.json" ]]; then
  rm -f "$TARGET_STATE_DIR/openclaw.json"
fi

echo "Construyendo imagen (OpenClaw + dependencias Python) y levantando stack Docker de empleado..."
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" build --pull
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d

echo "Empleado desplegado en: http://127.0.0.1:18790/"
