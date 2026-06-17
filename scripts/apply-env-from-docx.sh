#!/usr/bin/env bash
# Aplica credenciales desde credentials-inbox/ a docker/*/ .env
# Acepta .env planos (admin.env, …) o .docx (.env admin.docx, …)
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="${1:-$ROOT/credentials-inbox}"
SCRIPT="$ROOT/scripts/docx-to-env.py"
HOST_HOME="${OPENCLAW_APPLY_HOST_HOME:-$HOME}"

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Falta: $1" >&2
    exit 1
  }
}

require python3

rewrite_host_paths() {
  local dst="$1"
  if [ ! -f "$dst" ]; then
    return 0
  fi
  local changed=0
  for old in /home/joaquin /home/fernanda2114t /home/ubuntu; do
    if [ "$old" != "$HOST_HOME" ] && grep -q "$old" "$dst" 2>/dev/null; then
      sed -i "s|${old}|${HOST_HOME}|g" "$dst"
      changed=1
    fi
  done
  if [ "$changed" -eq 1 ]; then
    echo "  (rutas de home → ${HOST_HOME})"
  fi
  # PC local: Telegram → host.docker.internal (no 127.0.0.1 dentro del contenedor)
  if [[ "$dst" == *docker/telegram/.env ]]; then
    sed -i \
      -e 's|OPENCLAW_ADMIN_BASE_URL=http://127.0.0.1:|OPENCLAW_ADMIN_BASE_URL=http://host.docker.internal:|g' \
      -e 's|OPENCLAW_EMPLEADO_BASE_URL=http://127.0.0.1:|OPENCLAW_EMPLEADO_BASE_URL=http://host.docker.internal:|g' \
      "$dst"
  fi
}

apply_plain() {
  local src_name="$1"
  local env_rel="$2"
  local src="$INBOX/$src_name"
  local dst="$ROOT/$env_rel"
  if [ ! -f "$src" ]; then
    return 1
  fi
  cp "$src" "$dst"
  rewrite_host_paths "$dst"
  echo "Copiado $src_name → $env_rel"
  return 0
}

apply_docx() {
  local docx_name="$1"
  local env_rel="$2"
  local src="$INBOX/$docx_name"
  local dst="$ROOT/$env_rel"
  if [ ! -f "$src" ]; then
    return 1
  fi
  python3 "$SCRIPT" "$src" "$dst"
  rewrite_host_paths "$dst"
  return 0
}

apply_stack() {
  local plain_name="$1"
  local docx_name="$2"
  local env_rel="$3"
  if apply_plain "$plain_name" "$env_rel"; then
    return 0
  fi
  if apply_docx "$docx_name" "$env_rel"; then
    return 0
  fi
  echo "No encontrado para $env_rel (probado: $plain_name, $docx_name)" >&2
  return 1
}

missing=0
apply_stack "admin.env" ".env admin.docx" "docker/admin/.env" || missing=1
apply_stack "empleado.env" ".env empleado.docx" "docker/empleado/.env" || missing=1
apply_stack "telegram.env" ".env telegram.docx" "docker/telegram/.env" || missing=1

if [ "$missing" -ne 0 ]; then
  echo "" >&2
  echo "Coloca en $INBOX uno de estos formatos por stack:" >&2
  echo "  admin.env          o  .env admin.docx" >&2
  echo "  empleado.env       o  .env empleado.docx" >&2
  echo "  telegram.env       o  .env telegram.docx" >&2
  exit 1
fi

echo "Credenciales aplicadas en docker/admin/.env, docker/empleado/.env y docker/telegram/.env"
