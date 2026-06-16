#!/bin/sh
# OpenClaw sanea GOG_KEYRING_PASSWORD en exec; normaliza cuerpos de borrador Gmail.
set -e
for pwfile in /tmp/openclaw-gog-keyring.pw /home/node/.openclaw/gog-keyring.pw; do
	if [ -r "$pwfile" ]; then
		GOG_KEYRING_PASSWORD=$(cat "$pwfile")
		export GOG_KEYRING_PASSWORD
		break
	fi
done
export GOG_KEYRING_BACKEND="${GOG_KEYRING_BACKEND:-file}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-/home/node/.config}"

if [ "$1" = "gmail" ] && [ "$2" = "drafts" ] && [ "$3" = "create" ]; then
	exec python3 /usr/local/bin/gog-gmail-draft-wrap.py "$@"
fi

exec /usr/local/bin/gog.real "$@"
