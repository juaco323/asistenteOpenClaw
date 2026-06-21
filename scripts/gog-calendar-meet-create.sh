#!/usr/bin/env bash
# Crea evento Google Calendar con Meet (solo perfil Administrador).
# Uso:
#   ./scripts/gog-calendar-meet-create.sh --dry-run \
#     --summary "Reunión seguimiento" \
#     --from "2026-06-27T10:00:00-04:00" \
#     --to "2026-06-27T11:00:00-04:00" \
#     --attendees "uno@ejemplo.com,dos@ejemplo.com"
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${REPO_ROOT}/docker/empleado/.env"
ACCOUNT="prueba.openclaw.fj@gmail.com"
CALENDAR_ID="primary"

DRY_RUN=""
SUMMARY=""
FROM=""
TO=""
ATTENDEES=""
REMINDERS="popup:30m,email:1d"
SEND_UPDATES="all"
DESCRIPTION="Reunión creada por OpenClaw (admin-comms)."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --summary) SUMMARY="$2"; shift ;;
    --from) FROM="$2"; shift ;;
    --to) TO="$2"; shift ;;
    --attendees) ATTENDEES="$2"; shift ;;
    --reminders) REMINDERS="$2"; shift ;;
    --description) DESCRIPTION="$2"; shift ;;
    -h|--help)
      sed -n '2,9p' "$0"
      exit 0
      ;;
    *) echo "Opción desconocida: $1" >&2; exit 1 ;;
  esac
  shift
done

[[ -n "${SUMMARY}" && -n "${FROM}" && -n "${TO}" ]] || {
  echo "Faltan --summary, --from y --to" >&2
  exit 1
}

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source <(grep -E '^GOG_KEYRING_PASSWORD=' "${ENV_FILE}" | sed 's/^/export /')
fi
export GOG_KEYRING_BACKEND=file
export XDG_CONFIG_HOME="${HOME}/.config"

CMD=(gog)
[[ -n "${DRY_RUN}" ]] && CMD+=(-n)
CMD+=(
  calendar create "${CALENDAR_ID}"
  -a "${ACCOUNT}"
  --summary "${SUMMARY}"
  --from "${FROM}"
  --to "${TO}"
  --with-meet
  --reminder "${REMINDERS}"
  --description "${DESCRIPTION}"
  --send-updates "${SEND_UPDATES}"
  --json
)
[[ -n "${ATTENDEES}" ]] && CMD+=(--attendees "${ATTENDEES}")

OUT=$("${CMD[@]}")
echo "$OUT" | python3 -c "
import sys, json
raw = sys.stdin.read().strip()
if not raw:
    sys.exit(0)
d = json.loads(raw)
if d.get('dry_run'):
    print('DRY_RUN: OK — se crearía evento con Meet')
    print(json.dumps(d, indent=2, ensure_ascii=False)[:2000])
    sys.exit(0)
ev = d.get('event', d)
link = ev.get('hangoutLink')
if not link:
    for ep in (ev.get('conferenceData') or {}).get('entryPoints', []):
        if ep.get('entryPointType') == 'video':
            link = ep.get('uri')
            break
print('EVENT_ID:', ev.get('id', ''))
print('MEET_LINK:', link or '')
print('CALENDAR_LINK:', ev.get('htmlLink', ''))
print('SUMMARY:', ev.get('summary', ''))
"
