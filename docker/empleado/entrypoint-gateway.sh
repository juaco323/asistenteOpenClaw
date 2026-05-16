#!/bin/sh
# Materializa GOG_KEYRING_PASSWORD en un fichero solo-lectura del usuario node para que
# /usr/local/bin/gog (wrapper) pueda abrir el llavero aunque el gateway no pase la var al exec.
set -e
umask 077
if [ -n "${GOG_KEYRING_PASSWORD:-}" ]; then
	printf '%s' "$GOG_KEYRING_PASSWORD" > /tmp/openclaw-gog-keyring.pw
	chmod 600 /tmp/openclaw-gog-keyring.pw || true
fi
exec "$@"
