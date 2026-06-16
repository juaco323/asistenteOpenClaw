#!/bin/sh
# Materializa GOG_KEYRING_PASSWORD para que /usr/local/bin/gog (wrapper) abra el llavero
# aunque OpenClaw no pase *_PASSWORD al subproceso exec.
set -e
umask 077
if [ -n "${GOG_KEYRING_PASSWORD:-}" ]; then
	for pwfile in /tmp/openclaw-gog-keyring.pw /home/node/.openclaw/gog-keyring.pw; do
		printf '%s' "$GOG_KEYRING_PASSWORD" >"$pwfile"
		chmod 600 "$pwfile" 2>/dev/null || true
	done
fi
exec "$@"
