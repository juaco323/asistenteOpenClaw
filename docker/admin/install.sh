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

# Log JSONL compartido entre logger.py, panel y (opcional) bot Telegram.
touch "$SOURCE_WORKSPACE/.llm-test-runs.jsonl"

if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
  echo "Se creo $ENV_FILE a partir de .env.example" >&2
  echo "Editalo antes de volver a ejecutar install.sh" >&2
  exit 1
fi

if [[ -e "$TARGET_STATE_DIR/openclaw.json" ]] && [[ ! -s "$TARGET_STATE_DIR/openclaw.json" ]]; then
  rm -f "$TARGET_STATE_DIR/openclaw.json"
fi

echo "Construyendo imagen del gateway (incluye base OPENCLAW_IMAGE) y levantando stack Docker de admin..."
# No usar compose pull sobre openclaw-admin: la etiqueta OPENCLAW_CONTAINER_NAME:local es local-only.
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" build --pull
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d

echo "Admin desplegado. Workspace: ${SOURCE_WORKSPACE} (montado en el contenedor)."
echo "Control UI OpenClaw: http://127.0.0.1:<OPENCLAW_HOST_PORT>/ (ver OPENCLAW_HOST_PORT en docker/admin/.env)."
echo "Panel pruebas LLM (JSONL): http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/ (ver LLM_TEST_PANEL_HOST_PORT en docker/admin/.env)."
