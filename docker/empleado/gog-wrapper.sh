#!/bin/sh
# OpenClaw 2026.5.7 sanea variables *PASSWORD* al lanzar herramientas; leemos la clave
# desde un archivo creado en el arranque del contenedor (ver entrypoint-gateway.sh).
set -e
PWFILE=/tmp/openclaw-gog-keyring.pw
if [ -r "$PWFILE" ]; then
	GOG_KEYRING_PASSWORD=$(cat "$PWFILE")
	export GOG_KEYRING_PASSWORD
fi
export GOG_KEYRING_BACKEND="${GOG_KEYRING_BACKEND:-file}"
exec /usr/local/bin/gog.real "$@"
