#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for d in telegram empleado admin; do
  f="docker/$d/.env"
  y="docker/$d/docker-compose.yml"
  if [ -f "$f" ] && [ -f "$y" ]; then
    echo "== Bajando $d =="
    docker compose --env-file "$f" -f "$y" down
  fi
done

echo "Stacks detenidos (orden: telegram, empleado, admin)."
