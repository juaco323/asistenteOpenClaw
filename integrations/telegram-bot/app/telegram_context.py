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
