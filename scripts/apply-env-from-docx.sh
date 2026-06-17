#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="${1:-$ROOT/credentials-inbox}"
SCRIPT="$ROOT/scripts/docx-to-env.py"

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Falta: $1" >&2
    exit 1
  }
}

require python3

apply_one() {
  local docx_name="$1"
  local env_rel="$2"
  local src="$INBOX/$docx_name"
  local dst="$ROOT/$env_rel"
  if [ ! -f "$src" ]; then
    echo "No encontrado: $src" >&2
    return 1
  fi
  python3 "$SCRIPT" "$src" "$dst"
}

missing=0
apply_one ".env admin.docx" "docker/admin/.env" || missing=1
apply_one ".env empleado.docx" "docker/empleado/.env" || missing=1
apply_one ".env telegram.docx" "docker/telegram/.env" || missing=1

if [ "$missing" -ne 0 ]; then
  echo "Coloca los tres .docx en: $INBOX" >&2
  echo "  - .env admin.docx" >&2
  echo "  - .env empleado.docx" >&2
  echo "  - .env telegram.docx" >&2
  exit 1
fi

echo "Credenciales aplicadas en docker/admin/.env, docker/empleado/.env y docker/telegram/.env"
