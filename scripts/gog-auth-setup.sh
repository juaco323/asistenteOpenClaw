#!/usr/bin/env bash
# Configura OAuth de gog (Gmail + Drive) para prueba.openclaw.fj@gmail.com en el HOST.
# Los tokens quedan en ~/.config/gogcli y los ven los contenedores admin/empleado.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${REPO_ROOT}/docker/empleado/.env"
JSON="${HOME}/Descargas/prueba_openclaw.fj.json"
ACCOUNT="prueba.openclaw.fj@gmail.com"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Falta ${ENV_FILE}" >&2
  exit 1
fi

# shellcheck disable=SC1090
source <(grep -E '^(GOG_KEYRING_PASSWORD|GOG_ACCOUNT)=' "${ENV_FILE}" | sed 's/^/export /')

export GOG_KEYRING_BACKEND=file
export XDG_CONFIG_HOME="${HOME}/.config"

if [[ -z "${GOG_KEYRING_PASSWORD:-}" ]]; then
  echo "GOG_KEYRING_PASSWORD vacía en ${ENV_FILE}" >&2
  exit 1
fi

if [[ ! -f "${JSON}" ]]; then
  echo "Falta JSON OAuth: ${JSON}" >&2
  exit 1
fi

if ! command -v gog >/dev/null 2>&1; then
  echo "Instala gog: https://gogcli.sh/" >&2
  exit 1
fi

echo "== Credenciales OAuth (cliente) =="
gog auth credentials set "${JSON}"

echo ""
echo "== Tokens actuales =="
gog auth list || true

echo ""
echo "== Autorización interactiva (Gmail + Drive + Calendar) =="
echo "Se abrirá el navegador o verás una URL. Inicia sesión con la cuenta de pruebas del proyecto."
echo "Cuenta: ${ACCOUNT}"
echo ""

gog auth add "${ACCOUNT}" --services gmail,drive,calendar

echo ""
echo "== Verificación =="
gog auth list

echo ""
echo "Recrea contenedores si ya estaban levantados:"
echo "  cd ${REPO_ROOT} && docker compose --env-file docker/admin/.env -f docker/admin/docker-compose.yml up -d --force-recreate openclaw-admin"
echo "  cd ${REPO_ROOT} && docker compose --env-file docker/empleado/.env -f docker/empleado/docker-compose.yml up -d --force-recreate openclaw-empleado"
