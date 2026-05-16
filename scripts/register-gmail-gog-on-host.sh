#!/usr/bin/env bash
# Rellena ~/.config/gogcli en el HOST (misma ruta que montan los contenedores admin/empleado).
#
# Requisitos manuales:
# - JSON de cliente OAuth de Google Cloud descargado; por defecto en
#     ~/Descargas/prueba_openclaw.fj.json
#   (puedes usar otra ruta: export GOG_CLIENT_JSON=/ruta/al.json antes de ejecutar).
# - gog instalado en el host (compatible con la CLI del contenedor).
#
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${REPO_ROOT}/docker/empleado/.env"
JSON_PATH="${GOG_CLIENT_JSON:-${HOME}/Descargas/prueba_openclaw.fj.json}"

if ! command -v gog >/dev/null 2>&1; then
  echo "No se encontró 'gog' en el PATH." >&2
  echo "Instálalo donde corresponda (p. ej. paquete gogcli de tu distribución/Homebrew)." >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "No existe ${ENV_FILE}. Copia desde .env.example y configura GOG_KEYRING_PASSWORD." >&2
  exit 1
fi

GOG_PW="$(grep -m1 -E '^GOG_KEYRING_PASSWORD=' "${ENV_FILE}" | sed 's/^GOG_KEYRING_PASSWORD=//')"
GOG_ACC="$(grep -m1 -E '^GOG_ACCOUNT=' "${ENV_FILE}" | sed 's/^GOG_ACCOUNT=//')"
GOG_ACC="${GOG_ACC:-prueba.openclaw.fj@gmail.com}"

if [[ -z "${GOG_PW}" ]]; then
  echo "Define GOG_KEYRING_PASSWORD en ${ENV_FILE}" >&2
  exit 1
fi

mkdir -p "${HOME}/Descargas" "${HOME}/.config/gogcli"

export GOG_KEYRING_BACKEND=file
export GOG_KEYRING_PASSWORD="${GOG_PW}"

if [[ ! -f "${JSON_PATH}" ]]; then
  echo ""
  echo "Falta el JSON del cliente OAuth de Google:"
  echo "  ${JSON_PATH}"
  echo ""
  echo "Dónde obtenerlo:"
  echo "  Google Cloud Console → tu proyecto → APIs y servicios → Credenciales"
  echo "  → crear ID de cliente OAuth 2.0 (tipo acorde al flujo para gog) → descargar JSON."
  echo "Guárdalo en la ruta anterior o ejecuta antes:"
  echo "  export GOG_CLIENT_JSON=/ruta/absoluta/tu_credencial.json"
  exit 1
fi


echo ""
echo "Siguiente paso INTERACTIVO (navegador / URL de autorización Gmail):"
echo "  export GOG_KEYRING_BACKEND=file"
echo "  export GOG_KEYRING_PASSWORD='(igual que en docker/empleado/.env)'"
echo "  gog auth add ${GOG_ACC} --services gmail"
echo ""
echo "Verificación rápida:"
echo "  gog auth list"
echo ""
echo "Recarga gateways si ya estaban en marcha:"
echo "  cd ${REPO_ROOT}"
echo "  docker compose --env-file docker/admin/.env -f docker/admin/docker-compose.yml up -d --force-recreate"
echo "  docker compose --env-file docker/empleado/.env -f docker/empleado/docker-compose.yml up -d --force-recreate"
