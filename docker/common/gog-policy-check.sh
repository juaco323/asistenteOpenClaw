#!/bin/sh
# Política de comandos gog antes de delegar en gog.real (admin + empleado).
# OPENCLAW_WORKSPACE_PROFILE: admin | empleado (definido en docker-compose).

profile="${OPENCLAW_WORKSPACE_PROFILE:-empleado}"

die() {
	echo "openclaw-gog-policy: $1" >&2
	exit 1
}

# Bloqueo global: envío Gmail directo sin borrador (fuerza drafts create + drafts send).
if [ "$1" = "gmail" ] && [ "$2" = "send" ]; then
	die "comando bloqueado: use 'gog gmail drafts create' y 'gog gmail drafts send' tras confirmación del usuario"
fi

# Perfil empleado: sin borrado ni modificación en Drive.
if [ "$profile" = "empleado" ]; then
	case "$1/$2" in
	drive/delete | drive/trash | drive/update | drive/rename)
		die "comando bloqueado en perfil empleado: $1 $2"
		;;
	esac
fi

# Perfil empleado: sin Calendar/Meet (solo admin).
if [ "$profile" = "empleado" ]; then
	case "$1" in
	calendar | cal)
		die "comando bloqueado en perfil empleado: Calendar/Meet solo en perfil administrador"
		;;
	esac
fi

# Perfil admin: cancelar reunión solo vía script (correo con motivo automático).
if [ "$profile" = "admin" ]; then
	case "$2" in
	delete | del | rm | remove)
		case "$1" in
		calendar | cal)
			if [ "${OPENCLAW_MEET_CANCEL_APPROVED:-}" != "1" ]; then
				die "calendar delete bloqueado: use gog-calendar-meet-cancel.sh --event-id ID --reason \"motivo\" --admin-name \"Nombre\" (envía correo a invitados y luego elimina el evento)"
			fi
			;;
		esac
		;;
	esac
fi
