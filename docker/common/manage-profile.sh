#!/usr/bin/env bash
# Logica compartida de install/backup/update para los perfiles admin y empleado.
# Los wrappers en docker/<perfil>/{install,backup,update}.sh llaman a este script
# con el perfil correspondiente; ver docker/admin/install.sh como ejemplo.
set -euo pipefail

PROFILE="${1:?Uso: manage-profile.sh <admin|empleado> <install|backup|update>}"
ACTION="${2:?Uso: manage-profile.sh <admin|empleado> <install|backup|update>}"
shift 2 || true

case "$PROFILE" in
  admin|empleado) ;;
  *) echo "Perfil desconocido: $PROFILE (usar admin o empleado)" >&2; exit 1 ;;
esac

COMMON_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$COMMON_DIR/../.." && pwd)"
PROFILE_DIR="$REPO_ROOT/docker/$PROFILE"
SOURCE_WORKSPACE="$REPO_ROOT/workspace-$PROFILE"
TARGET_STATE_DIR="${HOME}/.openclaw-$PROFILE"
ENV_FILE="$PROFILE_DIR/.env"
COMPOSE_FILE="$PROFILE_DIR/docker-compose.yml"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Falta el comando requerido: $1" >&2
    exit 1
  }
}

do_install() {
  require_cmd docker

  docker compose version >/dev/null 2>&1 || {
    echo "Docker Compose v2 no esta disponible." >&2
    exit 1
  }

  mkdir -p "$TARGET_STATE_DIR"

  # El contenedor monta workspace-$PROFILE desde el repo (ver docker-compose.yml).
  rm -f "$SOURCE_WORKSPACE/BOOTSTRAP.md"

  # Log JSONL compartido entre logger.py, panel y (opcional) bot Telegram.
  touch "$SOURCE_WORKSPACE/.llm-test-runs.jsonl"

  if [ ! -f "$ENV_FILE" ]; then
    cp "$PROFILE_DIR/.env.example" "$ENV_FILE"
    echo "Se creo $ENV_FILE a partir de .env.example" >&2
    echo "Editalo antes de volver a ejecutar install.sh" >&2
    exit 1
  fi

  # Archivo openclaw.json vacío en el estado choca con el bind mount de ./openclaw.json del compose.
  if [[ -e "$TARGET_STATE_DIR/openclaw.json" ]] && [[ ! -s "$TARGET_STATE_DIR/openclaw.json" ]]; then
    rm -f "$TARGET_STATE_DIR/openclaw.json"
  fi

  case "$PROFILE" in
    admin) echo "Construyendo imagen del gateway (incluye base OPENCLAW_IMAGE) y levantando stack Docker de admin..." ;;
    empleado) echo "Construyendo imagen (OpenClaw + dependencias Python) y levantando stack Docker de empleado..." ;;
  esac
  # No usar compose pull sobre openclaw-$PROFILE: la etiqueta OPENCLAW_CONTAINER_NAME:local es local-only.
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d

  PROFILE_CAP="${PROFILE^}"
  echo "${PROFILE_CAP} desplegado. Workspace: ${SOURCE_WORKSPACE} (montado en el contenedor)."
  echo "Control UI OpenClaw: http://127.0.0.1:<OPENCLAW_HOST_PORT>/ (ver OPENCLAW_HOST_PORT en docker/$PROFILE/.env)."
  echo "Panel pruebas LLM (JSONL): http://127.0.0.1:<LLM_TEST_PANEL_HOST_PORT>/ (ver LLM_TEST_PANEL_HOST_PORT en docker/$PROFILE/.env)."
}

do_backup() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "No existe $ENV_FILE. Ejecuta primero install.sh" >&2
    exit 1
  fi

  set -a
  . "$ENV_FILE"
  set +a

  BACKUP_DIR="$PROFILE_DIR/backups"
  mkdir -p "$BACKUP_DIR"
  ARCHIVE="$BACKUP_DIR/$PROFILE-$(date +%Y%m%d-%H%M%S).tgz"

  tar -czf "$ARCHIVE" -C "$(dirname "$OPENCLAW_STATE_DIR")" "$(basename "$OPENCLAW_STATE_DIR")"

  echo "Backup creado en: $ARCHIVE"
}

do_update() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "No existe $ENV_FILE. Ejecuta primero install.sh" >&2
    exit 1
  fi

  # admin y empleado difieren aca desde antes de este refactor: admin separa
  # build --pull de up -d, empleado usa up -d --build (sin --pull). Se preserva
  # tal cual para no cambiar comportamiento existente.
  case "$PROFILE" in
    admin)
      docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --pull
      docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
      ;;
    empleado)
      docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --build
      ;;
  esac

  echo "Stack $PROFILE actualizado (workspace sigue siendo el del repo, montado en el contenedor)."
}

case "$ACTION" in
  install) do_install ;;
  backup) do_backup ;;
  update) do_update ;;
  *) echo "Accion desconocida: $ACTION (usar install, backup o update)" >&2; exit 1 ;;
esac
