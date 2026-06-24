#!/usr/bin/env bash
# Crea reunión Zoom y envía invitación por Gmail a los correos indicados (solo Administrador).
# Uso:
#   ./scripts/zoom-meeting-create.sh --dry-run \
#     --summary "Reunión seguimiento" \
#     --from "2026-06-27T10:00:00-04:00" \
#     --duration 60 \
#     --attendees "uno@ejemplo.com,dos@ejemplo.com" \
#     --admin-name "María González"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/zoom-api-common.sh
source "${SCRIPT_DIR}/zoom-api-common.sh"
zoom_load_env

DRY_RUN=""
SUMMARY=""
FROM=""
TO=""
DURATION=""
TIMEZONE="America/Santiago"
ATTENDEES=""
ADMIN_NAME="Administrador"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --summary) SUMMARY="$2"; shift ;;
    --from) FROM="$2"; shift ;;
    --to) TO="$2"; shift ;;
    --duration) DURATION="$2"; shift ;;
    --timezone) TIMEZONE="$2"; shift ;;
    --attendees) ATTENDEES="$2"; shift ;;
    --admin-name) ADMIN_NAME="$2"; shift ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
  shift
done

[[ -n "${SUMMARY}" && -n "${FROM}" ]] || {
  echo "Faltan --summary y --from" >&2
  exit 1
}

PARSED=$(
  FROM="${FROM}" TO="${TO}" DURATION="${DURATION}" TIMEZONE="${TIMEZONE}" python3 <<'PY'
import json, os
from datetime import datetime, timezone

from_str = os.environ["FROM"]
to_str = os.environ.get("TO", "").strip()
dur_env = os.environ.get("DURATION", "").strip()
tz = os.environ.get("TIMEZONE", "America/Santiago")

def parse_iso(s):
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)

start = parse_iso(from_str)
if to_str:
    end = parse_iso(to_str)
    duration = max(1, int((end - start).total_seconds() // 60))
elif dur_env:
    duration = max(1, int(dur_env))
else:
    duration = 60

# Zoom API: start_time sin offset + timezone aparte
start_naive = start.strftime("%Y-%m-%dT%H:%M:%S")
human = start.strftime("%d/%m/%Y %H:%M")
print(json.dumps({
    "start_time": start_naive,
    "duration": duration,
    "timezone": tz,
    "human_start": human,
}, ensure_ascii=False))
PY
)

START_TIME=$(echo "${PARSED}" | python3 -c 'import sys,json; print(json.load(sys.stdin)["start_time"])')
DURATION_MIN=$(echo "${PARSED}" | python3 -c 'import sys,json; print(json.load(sys.stdin)["duration"])')
HUMAN_START=$(echo "${PARSED}" | python3 -c 'import sys,json; print(json.load(sys.stdin)["human_start"])')

if [[ -n "${DRY_RUN}" ]]; then
  echo "DRY_RUN: se crearía reunión Zoom"
  echo "TÍTULO: ${SUMMARY}"
  echo "INICIO: ${HUMAN_START} (${TIMEZONE})"
  echo "DURACIÓN: ${DURATION_MIN} min"
  echo "INVITADOS: ${ATTENDEES:-ninguno}"
  exit 0
fi

TOKEN=$(zoom_access_token)

PAYLOAD=$(SUMMARY="${SUMMARY}" START_TIME="${START_TIME}" DURATION_MIN="${DURATION_MIN}" TIMEZONE="${TIMEZONE}" python3 <<'PY'
import json, os
print(json.dumps({
    "topic": os.environ["SUMMARY"],
    "type": 2,
    "start_time": os.environ["START_TIME"],
    "duration": int(os.environ["DURATION_MIN"]),
    "timezone": os.environ["TIMEZONE"],
    "settings": {
        "host_video": True,
        "participant_video": True,
        "join_before_host": False,
        "waiting_room": True,
        "approval_type": 2,
    },
}))
PY
)

RESP=$(curl -sS -X POST "${ZOOM_API_BASE}/users/me/meetings" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}")

MEETING_ID=$(echo "${RESP}" | python3 -c '
import sys, json
d = json.load(sys.stdin)
if "id" not in d:
    sys.stderr.write(json.dumps(d, ensure_ascii=False)[:800])
    sys.stderr.write("\n")
    sys.exit(1)
print(d["id"])
')

JOIN_URL=$(echo "${RESP}" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("join_url",""))')
PASS=$(echo "${RESP}" | python3 -c 'import sys,json; p=json.load(sys.stdin).get("password"); print(p or "")')

echo "MEETING_ID: ${MEETING_ID}"
echo "ZOOM_LINK: ${JOIN_URL}"
echo "SUMMARY: ${SUMMARY}"
echo "INICIO: ${HUMAN_START} (${TIMEZONE})"
echo "DURACIÓN: ${DURATION_MIN} min"
[[ -n "${PASS}" ]] && echo "CONTRASEÑA_ZOOM: ${PASS}"

if [[ -n "${ATTENDEES}" ]]; then
  BODY_FILE=$(mktemp)
  cleanup() { rm -f "${BODY_FILE}"; }
  trap cleanup EXIT
  SUMMARY="${SUMMARY}" HUMAN_START="${HUMAN_START}" TIMEZONE="${TIMEZONE}" \
    DURATION_MIN="${DURATION_MIN}" JOIN_URL="${JOIN_URL}" PASS="${PASS}" \
    ADMIN_NAME="${ADMIN_NAME}" BODY_FILE="${BODY_FILE}" python3 <<'PY'
import os
summary = os.environ["SUMMARY"]
when = os.environ["HUMAN_START"]
tz = os.environ["TIMEZONE"]
dur = os.environ["DURATION_MIN"]
link = os.environ["JOIN_URL"]
pwd = os.environ.get("PASS", "").strip()
admin = os.environ["ADMIN_NAME"]
lines = [
    "Estimado/a,",
    "",
    "Le invitamos a la siguiente reunión por Zoom:",
    "",
    f"Título: {summary}",
    f"Fecha y hora: {when} ({tz})",
    f"Duración: {dur} minutos",
    f"Enlace: {link}",
]
if pwd:
    lines.append(f"Contraseña: {pwd}")
lines.extend(["", "Saludos cordiales,", f"Atte: {admin}", ""])
with open(os.environ["BODY_FILE"], "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
PY
  SUBJECT="Invitación: ${SUMMARY}"
  echo "== Envío de invitación por correo =="
  echo "DESTINATARIOS: ${ATTENDEES}"
  DRAFT_ID=$(gog_send_email "${ATTENDEES}" "${SUBJECT}" "${BODY_FILE}")
  echo "CORREO_ENVIADO: sí (draft ${DRAFT_ID})"
fi

echo "ESTADO: reunion_zoom_creada"
