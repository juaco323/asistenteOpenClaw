#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
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

if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
  echo "Se creo $ENV_FILE a partir de .env.example"
  echo "Editalo antes de continuar y luego vuelve a ejecutar install.sh" >&2
  exit 1
fi

echo "Construyendo y levantando bot de Telegram..."
docker compose --env-file "$ENV_FILE" -f "$SCRIPT_DIR/docker-compose.yml" up -d --build
echo "Bot de Telegram desplegado."
echo "Asegurate de que openclaw-admin (18789) y openclaw-empleado (18790) esten arriba; el bot usa host.docker.internal para hablar con ellos."
