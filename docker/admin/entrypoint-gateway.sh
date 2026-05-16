#!/bin/sh
set -e
umask 077
if [ -n "${GOG_KEYRING_PASSWORD:-}" ]; then
	printf '%s' "$GOG_KEYRING_PASSWORD" > /tmp/openclaw-gog-keyring.pw
	chmod 600 /tmp/openclaw-gog-keyring.pw || true
fi
exec "$@"
