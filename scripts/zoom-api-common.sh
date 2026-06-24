#!/usr/bin/env bash
# Funciones compartidas para scripts Zoom (Server-to-Server OAuth).
# No ejecutar directamente; source desde zoom-meeting-*.sh

zoom_load_env() {
  local script_dir caller
  caller="${BASH_SOURCE[1]:-${BASH_SOURCE[0]}}"
  script_dir="$(cd "$(dirname "${caller}")" && pwd)"
  ENV_FILE=""
  for ENV_CANDIDATE in \
    "${script_dir}/../docker/admin/.env" \
    "${script_dir}/../docker/empleado/.env" \
    "${HOME}/asistenteOpenClaw/docker/admin/.env" \
    "${HOME}/asistenteOpenClaw/docker/empleado/.env"; do
    if [[ -f "${ENV_CANDIDATE}" ]]; then
      ENV_FILE="${ENV_CANDIDATE}"
      break
    fi
  done
  if [[ -n "${ENV_FILE}" && -f "${ENV_FILE}" ]]; then
    # shellcheck disable=SC1090
    source <(grep -E '^(GOG_KEYRING_PASSWORD|ZOOM_ACCOUNT_ID|ZOOM_CLIENT_ID|ZOOM_CLIENT_SECRET)=' "${ENV_FILE}" | sed 's/^/export /')
  fi
  export GOG_KEYRING_BACKEND=file
  export XDG_CONFIG_HOME="${HOME}/.config"
  export ZOOM_ACCOUNT_ID="${ZOOM_ACCOUNT_ID:-}"
  export ZOOM_CLIENT_ID="${ZOOM_CLIENT_ID:-}"
  export ZOOM_CLIENT_SECRET="${ZOOM_CLIENT_SECRET:-}"
  export ZOOM_API_BASE="${ZOOM_API_BASE:-https://api.zoom.us/v2}"
}

zoom_require_credentials() {
  if [[ -z "${ZOOM_ACCOUNT_ID}" || -z "${ZOOM_CLIENT_ID}" || -z "${ZOOM_CLIENT_SECRET}" ]]; then
    echo "ERROR: faltan ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID o ZOOM_CLIENT_SECRET en docker/admin/.env" >&2
    echo "Ver docs/configurar-zoom-api.md" >&2
    return 1
  fi
}

zoom_access_token() {
  local raw token
  zoom_require_credentials || return 1
  raw=$(curl -sS -X POST "https://zoom.us/oauth/token" \
    -u "${ZOOM_CLIENT_ID}:${ZOOM_CLIENT_SECRET}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=account_credentials&account_id=${ZOOM_ACCOUNT_ID}")
  token=$(echo "${raw}" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)
if "access_token" not in d:
    err = d.get("reason") or d.get("error") or json.dumps(d, ensure_ascii=False)
    sys.stderr.write(str(err))
    sys.stderr.write("\n")
    sys.exit(1)
print(d["access_token"])
' 2>/dev/null) || {
    echo "ERROR: no se pudo obtener token Zoom OAuth" >&2
    echo "${raw}" >&2
    return 1
  }
  echo "${token}"
}

gog_send_email() {
  # Uso: gog_send_email "to@a.com,b@b.com" "Asunto" /path/body.txt [dry_run_flag]
  local to="$1" subject="$2" body_file="$3" dry="${4:-}"
  local draft_out draft_id
  local gog_cmd=(gog)
  [[ -n "${dry}" ]] && gog_cmd+=(-n)
  draft_out=$("${gog_cmd[@]}" gmail drafts create \
    -a "prueba.openclaw.fj@gmail.com" \
    --to "${to}" \
    --subject "${subject}" \
    --body-file "${body_file}" \
    --json)
  if [[ -n "${dry}" ]]; then
    echo "${draft_out}"
    return 0
  fi
  draft_id=$(echo "${draft_out}" | python3 -c '
import sys, json
raw = sys.stdin.read().strip()
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
sys.exit(1)
')
  "${gog_cmd[@]}" gmail drafts send "${draft_id}" -a "prueba.openclaw.fj@gmail.com" --json >/dev/null
  echo "${draft_id}"
}
