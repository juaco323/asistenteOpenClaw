#!/usr/bin/env bash
# Ejecuta logger.py con un venv local (compatible con PEP 668 / Debian).
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VPY=".venv/bin/python"

if ! python3 -m venv -h >/dev/null 2>&1; then
  echo "No esta disponible 'python3 -m venv'. Instala el paquete de tu version, por ejemplo:" >&2
  echo "  sudo apt install python3.14-venv" >&2
  exit 1
fi

venv_ok() {
  [[ -x "$VPY" ]] && "$VPY" -m pip --version >/dev/null 2>&1
}

if ! venv_ok; then
  echo "Creando o reparando entorno virtual en $SCRIPT_DIR/.venv ..." >&2
  rm -rf .venv
  python3 -m venv .venv
  if ! venv_ok; then
    echo "Intentando instalar pip en el venv (ensurepip)..." >&2
    "$VPY" -m ensurepip --upgrade >/dev/null 2>&1 || true
  fi
  if ! venv_ok; then
    echo "El venv quedo sin pip ejecutable. Suele faltar el paquete completo de venv:" >&2
    echo "  sudo apt install python3.14-venv" >&2
    echo "(ajusta la version a la salida de: python3 --version)" >&2
    exit 1
  fi
fi

"$VPY" -m pip install -q -U pip
"$VPY" -m pip install -q -r requirements.txt
exec "$VPY" logger.py "$@"
