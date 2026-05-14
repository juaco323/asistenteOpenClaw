#!/usr/bin/env bash
# Abre el Control UI con el token de docker/admin/.env (solo uso local).
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${DIR}/.env"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "No existe ${ENV_FILE}. Copia .env.example a .env y rellena OPENCLAW_GATEWAY_TOKEN." >&2
  exit 1
fi
TOKEN=$(grep -E '^OPENCLAW_GATEWAY_TOKEN=' "${ENV_FILE}" | cut -d= -f2- | tr -d '\r' | head -1)
PORT=$(grep -E '^OPENCLAW_HOST_PORT=' "${ENV_FILE}" | cut -d= -f2- | tr -d '\r' | head -1)
PORT="${PORT:-18789}"
if [[ -z "${TOKEN}" ]]; then
  echo "OPENCLAW_GATEWAY_TOKEN está vacío en ${ENV_FILE}." >&2
  exit 1
fi
URL="http://127.0.0.1:${PORT}/?token=${TOKEN}"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${URL}" >/dev/null 2>&1 || true
elif command -v sensible-browser >/dev/null 2>&1; then
  sensible-browser "${URL}" >/dev/null 2>&1 || true
else
  echo "Abre en el navegador (no se encontró xdg-open):"
  echo "${URL}"
  exit 0
fi
