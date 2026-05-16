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


def _gmail_protocol_telegram() -> str:
    return (
        "Correo Gmail (gog, misma infraestructura que el asistente en OpenClaw): "
        "si el usuario redacta, pide borrador o envío de correo, aplica **exactamente** el protocolo "
        "de `AGENTS.md` / skill `email-gmail` del workspace activo. "
        "Usa la CLI `gog` disponible en el gateway; remitente **obligatorio** en cada comando Gmail: "
        '-a "prueba.openclaw.fj@gmail.com". '
        "Flujo obligatorio para mensajes nuevos: reunir destinatario, asunto y cuerpo; "
        "**solo** `gog gmail drafts create` primero; mostrar en la respuesta asunto, cuerpo e **ID de borrador**; "
        "**detener** hasta confirmación inequívoca en **este hilo de Telegram** de enviar **ese borrador** "
        "(vale lenguaje natural: «envíalo», «mándalo», «hazlo», «dale», «sí», «vale», «ok», «confirmo», «procede», «proceder con el envío», «enviar borrador ID …», etc.; no obligues una sola formula). "
        "**En el mismo turno** en que detectes esa aprobación, ejecuta `gog gmail drafts send \"<DRAFT_ID>\"` con el mismo `-a`; no repitas texto completo del borrador salvo que pida revisión el usuario. Si hay varios borradores ambiguos, pregunta el ID antes de enviar. "
        "No uses `gog gmail send` como primer paso para correos nuevos. "
        "No pidas otro medio de confirmación: Telegram es el canal válido. "
        "Tras crear borradores relevantes o enviar, actualiza trazas del workspace: `LOGS_EMAIL.md` y `HISTORY.md` "
        "(en admin vía `/app/logs_shared/` si aplica). "
        "No solicites contraseñas de Google ni tokens en el chat."
    )


def build_telegram_system_message(
    *,
    workspace: str,
    workspace_label: str,
    chat_id: int,
    user_id: int,
    username: str | None,
    policy: WorkspaceFilePolicy,
) -> str:
    handle = f"@{username}" if username else "sin_username"
    return (
        "CONTEXTO DE CANAL (obligatorio, prioridad alta): "
        "Estás atendiendo a un usuario exclusivamente a través de Telegram. "
        "El canal activo es Telegram; NO es webchat ni otro medio. "
        "No pidas chat_id, @username ni confirmación del canal: ya están disponibles. "
        f"Perfil/workspace activo: {workspace_label} ({workspace}). "
        f"chat_id de Telegram: {chat_id}. user_id: {user_id}. username: {handle}. "
        f"{_gmail_protocol_telegram()} "
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
        "No indiques que no puedes enviar por Telegram ni que falta un canal externo. "
        "Si el usuario dice get, envíame, mándame, entrégame o pide un archivo por nombre, "
        "localízalo solo dentro de las rutas de lectura permitidas y usa el marcador. "
        "Responde siempre en español profesional."
    )
