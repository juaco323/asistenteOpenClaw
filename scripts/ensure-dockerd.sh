#!/usr/bin/env bash
# Arranca dockerd en entornos cloud sin módulos iptables (vfs + sin NAT).
set -euo pipefail
if ! sudo docker info >/dev/null 2>&1; then
  sudo pkill dockerd 2>/dev/null || true
  sleep 1
  sudo dockerd --iptables=false --ip-forward=false --storage-driver=vfs >/tmp/dockerd.log 2>&1 &
  for _ in $(seq 1 30); do
    sudo docker info >/dev/null 2>&1 && exit 0
    sleep 1
  done
  echo "No se pudo iniciar dockerd. Ver /tmp/dockerd.log" >&2
  exit 1
fi
