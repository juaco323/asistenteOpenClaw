#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
BACKUP_DIR="$SCRIPT_DIR/backups"

if [ ! -f "$ENV_FILE" ]; then
  echo "No existe $ENV_FILE. Ejecuta primero install.sh" >&2
  exit 1
fi

set -a
. "$ENV_FILE"
set +a

mkdir -p "$BACKUP_DIR"
ARCHIVE="$BACKUP_DIR/empleado-$(date +%Y%m%d-%H%M%S).tgz"

tar -czf "$ARCHIVE" -C "$(dirname "$OPENCLAW_STATE_DIR")" "$(basename "$OPENCLAW_STATE_DIR")"

echo "Backup creado en: $ARCHIVE"
