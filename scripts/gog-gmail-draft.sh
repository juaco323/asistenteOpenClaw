#!/usr/bin/env bash
# Crea borrador Gmail con cuerpo en texto plano legible (saltos de línea reales).
# Evita pasar \n literales o prefijos $ en --body.
set -euo pipefail

ACCOUNT="prueba.openclaw.fj@gmail.com"
TO=""
SUBJECT=""
BODY_FILE=""
ATTACH=()

usage() {
  cat <<'EOF'
Uso: gog-gmail-draft.sh --to DEST --subject ASUNTO [--body-file RUTA|-]

  --body-file -   lee el cuerpo desde stdin (texto plano con párrafos reales)
  --attach RUTA   repetible

Ejemplo:
  gog-gmail-draft.sh --to user@example.com --subject "Recordatorio" --body-file - <<'EOF'
Hola,

Te recuerdo la reunión de hoy a las 22:00.

Saludos.
EOF
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --to) TO="$2"; shift 2 ;;
    --subject) SUBJECT="$2"; shift 2 ;;
    --body-file) BODY_FILE="$2"; shift 2 ;;
    --attach) ATTACH+=("$2"); shift 2 ;;
    -h|--help) usage ;;
    *) echo "Opción desconocida: $1" >&2; usage ;;
  esac
done

[[ -n "$TO" && -n "$SUBJECT" && -n "$BODY_FILE" ]] || usage

TMP=""
cleanup() {
  [[ -n "$TMP" && -f "$TMP" ]] && rm -f "$TMP"
}
trap cleanup EXIT

if [[ "$BODY_FILE" == "-" ]]; then
  TMP="$(mktemp)"
  cat >"$TMP"
  BODY_FILE="$TMP"
fi

if [[ ! -f "$BODY_FILE" ]]; then
  echo "No existe el archivo de cuerpo: $BODY_FILE" >&2
  exit 1
fi

# Rechazar artefactos típicos de shell/JSON mal escapados
if grep -qE '\\n|\\r|\\t' "$BODY_FILE" 2>/dev/null; then
  echo "El cuerpo contiene secuencias literales \\n, \\r o \\t. Usa saltos de línea reales en el archivo." >&2
  exit 1
fi
if [[ "$(head -c1 "$BODY_FILE")" == '$' ]]; then
  echo "El cuerpo no debe empezar con $. Quita prefijos de shell/heredoc." >&2
  exit 1
fi

CMD=(gog gmail drafts create -a "$ACCOUNT" --to "$TO" --subject "$SUBJECT" --body-file "$BODY_FILE")
for f in "${ATTACH[@]}"; do
  CMD+=(--attach "$f")
done

exec "${CMD[@]}"
