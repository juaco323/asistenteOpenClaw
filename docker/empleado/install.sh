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

random_token() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 24
  else
    date +%s | sha256sum | cut -d' ' -f1 | head -c 48
  fi
}

require_cmd docker

docker compose version >/dev/null 2>&1 || {
  echo "Docker Compose v2 no está disponible." >&2
  exit 1
}

mkdir -p "$TARGET_STATE_DIR" "$TARGET_WORKSPACE_DIR"
cp -a "$SOURCE_WORKSPACE/." "$TARGET_WORKSPACE_DIR/"

if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<EOF
OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:2026.4.9
OPENCLAW_CONTAINER_NAME=openclaw-empleado
OPENCLAW_HOST_PORT=18790
OPENCLAW_INTERNAL_PORT=18789
OPENCLAW_GATEWAY_TOKEN=$(random_token)
OPENCLAW_STATE_DIR=$TARGET_STATE_DIR
OPENCLAW_WORKSPACE_DIR=$TARGET_WORKSPACE_DIR
EOF
fi

docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" config >/dev/null

echo "Descargando imagen y levantando stack Docker de empleado..."
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" pull
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d

echo
echo "Empleado desplegado en modo test."
echo "Control UI: http://127.0.0.1:18790/"
echo "Token guardado en: $ENV_FILE"
echo
echo "Siguiente paso recomendado: abrir el Control UI, autenticar con el token y completar la configuración que falte."
