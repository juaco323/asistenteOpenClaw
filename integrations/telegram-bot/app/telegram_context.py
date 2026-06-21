from __future__ import annotations

from pathlib import Path

from app.workspace_policy import WorkspaceFilePolicy


def _format_paths(paths: tuple[Path, ...]) -> str:
    return ", ".join(str(path) for path in paths) if paths else "(ninguna)"


def _delete_policy_text(policy: WorkspaceFilePolicy) -> str:
    if policy.delete_allowed:
        return (
            "Eliminación: permitida solo fuera de las zonas protegidas. "
            f"Zonas donde NUNCA eliminar: {_format_paths(policy.delete_forbidden_roots)}."
        )
    return (
        "Eliminación: ESTRICTAMENTE PROHIBIDA en todas las rutas. "
        "No ejecutes rm, rmdir, trash ni borrado equivalente. "
        "Si el usuario pide eliminar un archivo, recházalo y ofrece indicar la ruta "
        "para que lo borre manualmente desde el explorador. "
        f"Zonas especialmente protegidas: {_format_paths(policy.delete_forbidden_roots)}."
    )


def _admin_comms_protocol_telegram(*, workspace: str) -> str:
    logs_path = (
        "/app/logs_shared/LOGS_COMMS.md"
        if workspace == "admin"
        else "LOGS_COMMS.md"
    )
    meet_block = ""
    if workspace == "admin":
        meet_block = (
            "Google Calendar + Meet — **solo perfil Administrador** (Telegram y Control UI `:18791`). "
            "Leer `skills/admin-comms/calendar-meet.md`. "
            "**Crear reunión:** propuesta → confirmación en chat → "
            "`gog calendar create primary` o `scripts/gog-calendar-meet-create.sh` con "
            '`-a "prueba.openclaw.fj@gmail.com"`, `--with-meet`, `--send-updates all` (obligatorio si hay invitados), '
            '`--reminder popup:30m,email:1d` → `reunion_creada` + Meet link en LOGS_COMMS. '
            "**Cancelar reunión:** preguntar **motivo** (asunto del correo) y **nombre del administrador** (`Atte:`) si faltan; "
            "confirmación → `gog-calendar-meet-cancel.sh --event-id … --reason … --admin-name …` "
            "(correo automático: asunto=motivo, cuerpo «La reunión ha sido cancelada.» + Atte: nombre). "
            "**Prohibido** `gog calendar create` o `delete` sin confirmación del usuario en este chat. "
        )
    else:
        meet_block = (
            "Google Calendar + Meet — **prohibido** en perfil empleado (crear **y** cancelar reuniones). "
            "Si lo piden, indica perfil **Administrador** (`/workspace admin`; Control UI gateway `:18791`) "
            "y ofrece recordatorio por correo con `admin-comms`. "
        )
    return (
        "Comunicaciones administrativas (`admin-comms`, skill del workspace activo): "
        "si el usuario pide recordatorio, seguimiento, confirmación o mensaje formal a terceros, "
        "aplica `skills/admin-comms/SKILL.md` y el protocolo de `AGENTS.md` § comunicaciones. "
        "Extrae destinatario, fecha/plazo, responsable y acción pendiente; si falta lo esencial, pregunta. "
        "Redacta asunto y cuerpo en español profesional; guarda borrador en "
        "`~/Documentos/Comunicaciones/borradores/COMMS_<fecha>_<tema>.md` (`mkdir -p` si falta). "
        f"Registra estado en `{logs_path}` como `pendiente_confirmacion` (columna Agente: "
        f"{'Administrador' if workspace == 'admin' else 'Empleado'}). "
        "Presenta borrador **una vez** y detente. "
        "**Telegram es canal válido de confirmación** («envíalo», «vale», «confirma», «agéndala», «cancela la reunión», etc.). "
        "Sin confirmación explícita: **prohibido** despacho externo (correo, calendar). "
        "Tras confirmar envío por correo, encadena `email-gmail` (borrador gog → confirmación → send) "
        "y actualiza LOGS_COMMS + LOGS_EMAIL/HISTORY si aplica. "
        f"{meet_block}"
    )


def _gmail_protocol_telegram() -> str:
    return (
        "Correo Gmail (gog, misma infraestructura que el asistente en OpenClaw): "
        "si el usuario redacta, pide borrador o envío de correo, aplica **exactamente** el protocolo "
        "de `AGENTS.md` / skill `email-gmail` del workspace activo. "
        "Usa la CLI `gog` disponible en el gateway; remitente **obligatorio** en cada comando Gmail: "
        '-a "prueba.openclaw.fj@gmail.com". '
        "Flujo obligatorio para mensajes nuevos: reunir destinatario, asunto y cuerpo; "
        "el cuerpo del correo debe ser texto formal legible (saltos de línea reales con `--body-file` o heredoc; "
        "**prohibido** `\n` literal, prefijo `$` o escapes de programación en `--body`). "
        "**solo** `gog gmail drafts create` primero; en esa **primera** respuesta muestra asunto, cuerpo e **ID de borrador** y espera confirmación. "
        "**Tras confirmación** («envíalo», «mándalo», «vale», …): "
        "**Excepción cancelación reunión (solo admin):** si confirmó cancelar con motivo, ejecuta `scripts/gog-calendar-meet-cancel.sh` "
        "en el mismo turno — correo con motivo **automático**, sin segundo «envíalo». "
        "En el resto de casos: "
        "**prohibido** volver a mostrar asunto o cuerpo completos; ejecuta en el mismo turno `gog gmail drafts send \"<DRAFT_ID>\"` con `-a \"prueba.openclaw.fj@gmail.com\"` "
        "y responde **muy breve** (resultado del comando + ID; sin rearmar el borrador). "
        "**Adjuntos:** si el mensaje del usuario incluye ruta de archivo (p. ej. tras enviar documento/foto "
        "por Telegram), crea el borrador con `--attach` repetido por cada ruta absoluta legible en el "
        "gateway (misma ruta que en el host si `OPENCLAW_HOST_HOME` monta el home igual). "
        "Varios archivos: `--attach /ruta/uno.pdf --attach /ruta/dos.png`. "
        "Si hay varios borradores ambiguos, pregunta el ID antes de `drafts send`. "
        "No uses `gog gmail send` como primer paso para correos nuevos. "
        "No pidas otro medio de confirmación: Telegram es el canal válido. "
        "Tras crear borradores relevantes o enviar, actualiza trazas del workspace: `LOGS_EMAIL.md` y `HISTORY.md` "
        "(en admin vía `/app/logs_shared/` si aplica). "
        "No solicites contraseñas de Google ni tokens en el chat."
    )


def _admin_validation_text(admin_validated: bool) -> str:
    if not admin_validated:
        return ""
    return (
        "[ADMIN_VALIDADO: el usuario se autenticó con la contraseña de administrador "
        "en el bot de Telegram antes de esta sesión. "
        "Esta validación es suficiente como 'validación administrativa'; "
        "no pidas contraseña ni credenciales adicionales para acceder a métricas, "
        "historial de correos enviados, logs operativos ni cualquier dato de trazabilidad. "
        "Muestra la información solicitada directamente.] "
    )


def build_telegram_system_message(
    *,
    workspace: str,
    workspace_label: str,
    chat_id: int,
    user_id: int,
    username: str | None,
    policy: WorkspaceFilePolicy,
    admin_validated: bool = False,
) -> str:
    handle = f"@{username}" if username else "sin_username"
    return (
        _admin_validation_text(admin_validated)
        + "CONTEXTO DE CANAL (obligatorio, prioridad alta): "
        "Estás atendiendo a un usuario exclusivamente a través de Telegram. "
        "El canal activo es Telegram; NO es webchat ni otro medio. "
        "No pidas chat_id, @username ni confirmación del canal: ya están disponibles. "
        "Clasificación de mensajes: si el usuario pide información, listas, rankings, "
        "investigación o redacción («dame los 5 mejores…», «explica…», «busca…») sin la palabra "
        "**archivo** ni una ruta con extensión (.pdf, .txt, etc.), responde con LLM y web; "
        "**no** busques en disco un fichero cuyo nombre coincida con la frase. "
        "Solo entrega/busca archivos con [[TELEGRAM_FILE:…]] cuando pidan explícitamente un "
        "archivo, usen get, o den un nombre con extensión. "
        f"Perfil/workspace activo: {workspace_label} ({workspace}). "
        f"chat_id de Telegram: {chat_id}. user_id: {user_id}. username: {handle}. "
        f"{_gmail_protocol_telegram()} "
        f"{_admin_comms_protocol_telegram(workspace=workspace)} "
        "Política de archivos del perfil activo: "
        f"lectura/entrega (get) permitida en: {_format_paths(policy.read_roots)}. "
        f"escritura/creación permitida en: {_format_paths(policy.write_roots)}. "
        f"acceso denegado (lectura, escritura y entrega): {_format_paths(policy.deny_roots)}. "
        f"{_delete_policy_text(policy)} "
        f"Carpeta por defecto para crear archivos nuevos: {policy.default_create_dir}. "
        "Crea archivos nuevos solo dentro de las rutas de escritura permitidas. "
        "Entrega de archivos: el bot de Telegram adjunta archivos automáticamente en este mismo chat. "
        "Cuando localices, generes o el usuario pida un archivo, incluye en tu respuesta "
        "una línea por archivo con el formato exacto [[TELEGRAM_FILE:/ruta/absoluta/en/linux/archivo.ext]] "
        "usando la ruta real en el host y respetando la política del perfil. "
        "Archivos que el usuario **envía** por Telegram se guardan bajo "
        "`…/Documentos/telegram-openclaw-incoming/` (ruta absoluta en el mensaje del usuario cuando aplica); "
        "para Gmail, usa esas rutas con `gog gmail drafts create … --attach`. "
        "No indiques que no puedes enviar por Telegram ni que falta un canal externo. "
        "Si el usuario dice get, envíame, mándame, entrégame o pide un archivo por nombre, "
        "localízalo solo dentro de las rutas de lectura permitidas y usa el marcador. "
        "Búsqueda de archivos en disco: el usuario puede equivocarse en mayúsculas, acentos o en el "
        "nombre exacto de carpeta; **antes de afirmar que no existe**, busca candidatos con criterio "
        "insensible a mayúsculas (p. ej. `find RUTA -iname 'patrón'`, listar directorios y comparar "
        "nombres, `glob` con variantes). Si hay varias coincidencias, aclara o muestra rutas; en "
        "`[[TELEGRAM_FILE:…]]` y en `gog --attach` usa siempre la **ruta canónica real** del fichero. "
        "Responde siempre en español profesional."
    )
