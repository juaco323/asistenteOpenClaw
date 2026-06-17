#!/usr/bin/env bash
# Prepara y levanta el stack en PC local (p. ej. /home/joaquin). No usar en agente cloud.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

HOST_HOME="${OPENCLAW_PC_HOME:-/home/joaquin}"

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Falta: $1" >&2
    exit 1
  }
}

require docker
docker compose version >/dev/null 2>&1 || {
  echo "Se requiere Docker Compose v2. ¿Está Docker Desktop en marcha?" >&2
  exit 1
}

if ! docker info >/dev/null 2>&1; then
  echo "Docker no responde. Abre Docker Desktop o ejecuta: sudo systemctl start docker" >&2
  exit 1
fi

chmod +x "$ROOT/scripts/set-env-home.sh" "$ROOT/docker/stack-up.sh" "$ROOT/docker/stack-down.sh"

# Credenciales en bandeja → docker/*/ .env
if [ -f "$ROOT/credentials-inbox/admin.env" ]; then
  "$ROOT/scripts/apply-env-from-docx.sh"
else
  for d in admin empleado telegram; do
    if [ ! -f "$ROOT/docker/$d/.env" ]; then
      cp "$ROOT/docker/$d/.env.example" "$ROOT/docker/$d/.env"
      echo "Creado docker/$d/.env desde ejemplo (rellena secretos)." >&2
    fi
  done
fi

"$ROOT/scripts/set-env-home.sh" "$HOST_HOME"

for f in docker/admin/.env docker/empleado/.env docker/telegram/.env; do
  if [ -f "$ROOT/$f" ] && grep -qE '^(OPENAI_API_KEY|TELEGRAM_BOT_TOKEN)=$' "$ROOT/$f" 2>/dev/null; then
    echo "Aviso: $f tiene secretos vacíos. Copia credentials-inbox/*.env o rellena a mano." >&2
  fi
done

mkdir -p \
  "$HOST_HOME/.openclaw-admin" \
  "$HOST_HOME/.openclaw-empleado" \
  "$HOST_HOME/Documentos/telegram-openclaw-incoming" \
  "$HOST_HOME/.config/gogcli" \
  "$ROOT/workspace-admin" \
  "$ROOT/workspace-empleado"

touch "$ROOT/workspace-admin/.llm-test-runs.jsonl" "$ROOT/workspace-empleado/.llm-test-runs.jsonl"
rm -f "$ROOT/workspace-admin/BOOTSTRAP.md" 2>/dev/null || true

echo "== Levantando stack (PC local) =="
"$ROOT/docker/stack-up.sh"

echo ""
echo "Listo. Admin: http://127.0.0.1:18791/  Empleado: http://127.0.0.1:18790/"
