#!/usr/bin/env bash
# Cancela reunión Calendar: correo con motivo a invitados + delete con notificación.
# Uso:
#   ./scripts/gog-calendar-meet-cancel.sh \
#     --event-id "qva7nm51inj395jnl0j85opds0" \
#     --reason "Conflicto de agenda del equipo" \
#     --admin-name "María González"
#   ./scripts/gog-calendar-meet-cancel.sh --dry-run --event-id "…" --reason "…" --admin-name "…"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE=""
for ENV_CANDIDATE in \
  "/etc/openclaw/admin.env" \
  "${REPO_ROOT}/docker/admin/.env" \
  "${REPO_ROOT}/docker/empleado/.env" \
  "${SCRIPT_DIR}/../docker/admin/.env" \
  "${SCRIPT_DIR}/../docker/empleado/.env" \
  "${HOME}/asistenteOpenClaw/docker/admin/.env" \
  "${HOME}/asistenteOpenClaw/docker/empleado/.env"; do
  if [[ -f "${ENV_CANDIDATE}" ]]; then
    ENV_FILE="${ENV_CANDIDATE}"
    break
  fi
done
ACCOUNT="prueba.openclaw.fj@gmail.com"
CALENDAR_ID="primary"

DRY_RUN=""
EVENT_ID=""
REASON=""
ADMIN_NAME=""
ATTENDEES_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --event-id) EVENT_ID="$2"; shift ;;
    --reason) REASON="$2"; shift ;;
    --admin-name) ADMIN_NAME="$2"; shift ;;
    --attendees) ATTENDEES_OVERRIDE="$2"; shift ;;
    --calendar-id) CALENDAR_ID="$2"; shift ;;
    -h|--help)
      sed -n '2,9p' "$0"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
  shift
done

[[ -n "${EVENT_ID}" && -n "${REASON}" && -n "${ADMIN_NAME}" ]] || {
  echo "Faltan --event-id, --reason (asunto del correo) y --admin-name (obligatorios)" >&2
  exit 1
}

if [[ -z "${GOG_KEYRING_PASSWORD:-}" && -n "${ENV_FILE}" && -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source <(grep -E '^GOG_KEYRING_PASSWORD=' "${ENV_FILE}" | sed 's/^/export /')
fi
export GOG_KEYRING_BACKEND=file
export XDG_CONFIG_HOME="${HOME}/.config"
export GOG_KEYRING_PASSWORD="${GOG_KEYRING_PASSWORD:-}"

GOG_BASE=(gog)
GOG_READ=(gog)
[[ -n "${DRY_RUN}" ]] && GOG_BASE+=(-n)

fetch_event_json() {
  local out
  out=$("${GOG_READ[@]}" calendar event "${CALENDAR_ID}" "${EVENT_ID}" \
    -a "${ACCOUNT}" --json 2>/dev/null || true)
  if echo "${out}" | python3 -c 'import sys,json; d=json.load(sys.stdin); ev=d.get("event",d); sys.exit(0 if (ev or {}).get("id") else 1)' 2>/dev/null; then
    echo "${out}"
    return 0
  fi
  "${GOG_READ[@]}" calendar events list "${CALENDAR_ID}" \
    -a "${ACCOUNT}" \
    --from=-30d \
    --to=+30d \
    --all-pages \
    --max 250 \
    --json 2>/dev/null || echo '{}'
}

EVENT_JSON=$(fetch_event_json)

PARSED=$(
  EVENT_JSON="${EVENT_JSON}" EVENT_ID="${EVENT_ID}" ATTENDEES_OVERRIDE="${ATTENDEES_OVERRIDE}" ACCOUNT="${ACCOUNT}" python3 <<'PY'
import json, os

raw = os.environ.get("EVENT_JSON", "").strip() or "{}"
eid = os.environ["EVENT_ID"]
override = os.environ.get("ATTENDEES_OVERRIDE", "").strip()
account = os.environ["ACCOUNT"]

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    data = {}

events = data.get("events", data if isinstance(data, list) else [])
ev = data.get("event")
if not ev or not ev.get("id"):
    ev = next((e for e in events if e.get("id") == eid), None)

if override:
    attendees = [a.strip() for a in override.split(",") if a.strip()]
elif ev:
    attendees = [
        a["email"]
        for a in (ev.get("attendees") or [])
        if a.get("email") and a["email"].lower() != account.lower()
    ]
else:
    attendees = []

print(json.dumps({
    "attendees": attendees,
    "found": bool(ev),
}, ensure_ascii=False))
PY
)

ATTENDEES=$(echo "${PARSED}" | python3 -c 'import sys,json; print(",".join(json.load(sys.stdin)["attendees"]))')
FOUND=$(echo "${PARSED}" | python3 -c 'import sys,json; print("1" if json.load(sys.stdin)["found"] else "0")')

if [[ "${FOUND}" != "1" && -z "${ATTENDEES_OVERRIDE}" ]]; then
  echo "AVISO: no se encontró el evento ${EVENT_ID}; pasa --attendees con los correos del resumen." >&2
fi

if [[ -z "${ATTENDEES}" ]]; then
  echo "ERROR: sin destinatarios para el correo de cancelación. Pasa --attendees o verifica el event-id." >&2
  exit 1
fi

BODY_FILE=$(mktemp)
cleanup() { rm -f "${BODY_FILE}"; }
trap cleanup EXIT

ADMIN_NAME="${ADMIN_NAME}" BODY_FILE="${BODY_FILE}" python3 <<'PY'
import os

admin = os.environ["ADMIN_NAME"]
path = os.environ["BODY_FILE"]
body = f"La reunión ha sido cancelada.\n\tAtte: {admin}\n"
with open(path, "w", encoding="utf-8") as f:
    f.write(body)
PY

SUBJECT="${REASON}"

if [[ -n "${ATTENDEES}" ]]; then
  echo "== Paso 1: correo de cancelación a invitados =="
  echo "DESTINATARIOS: ${ATTENDEES}"
  echo "ASUNTO: ${SUBJECT}"
  if [[ -n "${DRY_RUN}" ]]; then
    echo "--- CUERPO ---"
    cat "${BODY_FILE}"
    echo "--- FIN CUERPO ---"
    "${GOG_BASE[@]}" gmail drafts create \
      -a "${ACCOUNT}" \
      --to "${ATTENDEES}" \
      --subject "${SUBJECT}" \
      --body-file "${BODY_FILE}" \
      --json
  else
    DRAFT_OUT=$("${GOG_BASE[@]}" gmail drafts create \
      -a "${ACCOUNT}" \
      --to "${ATTENDEES}" \
      --subject "${SUBJECT}" \
      --body-file "${BODY_FILE}" \
      --json)
    DRAFT_ID=$(echo "${DRAFT_OUT}" | python3 -c '
import sys, json
raw = sys.stdin.read().strip()
if not raw:
    sys.exit(1)
d = json.loads(raw)
for key in ("draftId", "id"):
    if d.get(key):
        print(d[key]); sys.exit(0)
draft = d.get("draft") or {}
for key in ("id", "draftId"):
    if draft.get(key):
        print(draft[key]); sys.exit(0)
msg = draft.get("message") or {}
if msg.get("id"):
    print(msg["id"]); sys.exit(0)
sys.stderr.write(f"No draft id in response: {raw[:500]}\n")
sys.exit(1)
')
    if [[ -z "${DRAFT_ID}" ]]; then
      echo "ERROR: no se obtuvo draftId del borrador de cancelación" >&2
      exit 1
    fi
    "${GOG_BASE[@]}" gmail drafts send "${DRAFT_ID}" -a "${ACCOUNT}" --json >/dev/null
    echo "CORREO_ENVIADO: sí (draft ${DRAFT_ID})"
  fi
fi

echo "== Paso 2: eliminar evento en Calendar (notificación estándar) =="
export OPENCLAW_MEET_CANCEL_APPROVED=1
DELETE_CMD=("${GOG_BASE[@]}")
DELETE_CMD+=(
  calendar delete "${CALENDAR_ID}" "${EVENT_ID}"
  -a "${ACCOUNT}"
  --send-updates all
  -y
  --json
)
DELETE_OUT=$("${DELETE_CMD[@]}" 2>&1 || true)

if [[ -n "${DRY_RUN}" ]]; then
  echo "DRY_RUN: OK — se cancelaría ${EVENT_ID}"
  echo "${DELETE_OUT}"
  exit 0
fi

echo "EVENT_ID: ${EVENT_ID}"
echo "ESTADO: reunion_cancelada"
echo "ASUNTO_CORREO: ${SUBJECT}"
echo "ADMINISTRADOR: ${ADMIN_NAME}"
echo "NOTIFICACION_CALENDAR: send-updates all"
