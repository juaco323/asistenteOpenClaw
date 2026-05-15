#!/usr/bin/env bash
# Delega en el logger del repo con perfil empleado (mismo venv que admin).
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../../admin/llm-test-logger/run.sh" --profile empleado "$@"
