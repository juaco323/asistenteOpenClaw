#!/usr/bin/env bash
# Comprueba que no haya .env reales ni patrones típicos de secretos en el índice de git.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

echo "== Archivos .env en el índice (debe estar vacío) =="
if tracked_env="$(git ls-files | grep -E '(^|/)\.env(\.|$)' | grep -vE '\.env\.(example|pc-oficina\.example)$' || true)"; then
  if [ -n "$tracked_env" ]; then
    echo "$tracked_env"
    fail=1
  else
    echo "(ninguno)"
  fi
fi

echo "== .env locales ignorados por git =="
for f in \
  docker/admin/.env \
  docker/empleado/.env \
  docker/telegram/.env \
  credentials-inbox/admin.env \
  credentials-inbox/empleado.env \
  credentials-inbox/telegram.env; do
  if [ -f "$f" ]; then
    if git check-ignore -q "$f"; then
      echo "OK ignorado: $f"
    else
      echo "ERROR no ignorado: $f"
      fail=1
    fi
  fi
done

echo "== Patrones de secretos en archivos rastreados =="
if git grep -n -E '(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|xox[baprs]-[a-zA-Z0-9-]{10,}|[0-9]{8,10}:[A-Za-z0-9_-]{35,})' -- ':!*.example' ':!scripts/check-no-secrets.sh' 2>/dev/null; then
  fail=1
else
  echo "(ningún patrón típico en HEAD)"
fi

if [ "$fail" -ne 0 ]; then
  echo "check-no-secrets: FALLO" >&2
  exit 1
fi
echo "check-no-secrets: OK"
