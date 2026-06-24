#!/usr/bin/env bash
# Cancela reunión Zoom: correo con motivo a invitados + eliminación en Zoom API.
# Uso:
#   ./scripts/zoom-meeting-cancel.sh \
#     --meeting-id "81234567890" \
#     --reason "Conflicto de agenda" \
#     --admin-name "María González" \
#     --attendees "uno@ejemplo.com,dos@ejemplo.com"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/zoom-api-common.sh
source "${SCRIPT_DIR}/zoom-api-common.sh"
zoom_load_env

DRY_RUN=""
MEETING_ID=""
REASON=""
ADMIN_NAME=""
ATTENDEES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --meeting-id) MEETING_ID="$2"; shift ;;
    --reason) REASON="$2"; shift ;;
    --admin-name) ADMIN_NAME="$2"; shift ;;
    --attendees) ATTENDEES="$2"; shift ;;
    -h|--help)
      sed -n '2,9p' "$0"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
  shift
done

[[ -n "${MEETING_ID}" && -n "${REASON}" && -n "${ADMIN_NAME}" ]] || {
  echo "Faltan --meeting-id, --reason (asunto del correo) y --admin-name" >&2
  exit 1
}

[[ -n "${ATTENDEES}" ]] || {
  echo "ERROR: --attendees obligatorio (correos del resumen o LOGS_COMMS)" >&2
  exit 1
}

BODY_FILE=$(mktemp)
cleanup() { rm -f "${BODY_FILE}"; }
trap cleanup EXIT

ADMIN_NAME="${ADMIN_NAME}" BODY_FILE="${BODY_FILE}" python3 <<'PY'
import os
admin = os.environ["ADMIN_NAME"]
with open(os.environ["BODY_FILE"], "w", encoding="utf-8") as f:
    f.write(f"La reunión por Zoom ha sido cancelada.\n\tAtte: {admin}\n")
PY

SUBJECT="${REASON}"

echo "== Paso 1: correo de cancelación a invitados =="
echo "DESTINATARIOS: ${ATTENDEES}"
echo "ASUNTO: ${SUBJECT}"

if [[ -n "${DRY_RUN}" ]]; then
  echo "--- CUERPO ---"
  cat "${BODY_FILE}"
  echo "--- FIN CUERPO ---"
  gog_send_email "${ATTENDEES}" "${SUBJECT}" "${BODY_FILE}" "dry"
  echo "DRY_RUN: no se elimina la reunión en Zoom"
  exit 0
fi

DRAFT_ID=$(gog_send_email "${ATTENDEES}" "${SUBJECT}" "${BODY_FILE}")
echo "CORREO_ENVIADO: sí (draft ${DRAFT_ID})"

echo "== Paso 2: eliminar reunión en Zoom =="
TOKEN=$(zoom_access_token)
HTTP_CODE=$(curl -sS -o /tmp/zoom-delete-out.json -w "%{http_code}" -X DELETE \
  "${ZOOM_API_BASE}/meetings/${MEETING_ID}" \
  -H "Authorization: Bearer ${TOKEN}")

if [[ "${HTTP_CODE}" != "204" && "${HTTP_CODE}" != "200" ]]; then
  echo "ERROR: Zoom API respondió HTTP ${HTTP_CODE}" >&2
  cat /tmp/zoom-delete-out.json >&2 2>/dev/null || true
  exit 1
fi

echo "MEETING_ID: ${MEETING_ID}"
echo "ESTADO: reunion_zoom_cancelada"
echo "ASUNTO_CORREO: ${SUBJECT}"
echo "ADMINISTRADOR: ${ADMIN_NAME}"
