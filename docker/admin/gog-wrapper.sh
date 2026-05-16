#!/bin/sh
set -e
PWFILE=/tmp/openclaw-gog-keyring.pw
if [ -r "$PWFILE" ]; then
	GOG_KEYRING_PASSWORD=$(cat "$PWFILE")
	export GOG_KEYRING_PASSWORD
fi
export GOG_KEYRING_BACKEND="${GOG_KEYRING_BACKEND:-file}"
exec /usr/local/bin/gog.real "$@"
