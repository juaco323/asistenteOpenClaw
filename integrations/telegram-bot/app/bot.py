from __future__ import annotations

import asyncio
import logging
import secrets
import time
from pathlib import Path
from typing import Final

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Conflict
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.auth_lockout import AuthLockoutStore
from app.config import DEFAULT_WORKSPACE_PASSWORDS, Settings
from app.errors import format_gateway_error
from app.gateway_progress import run_with_telegram_progress
from app.llm_test_log import append_llm_test_run
from app.file_delivery import (
    deliver_marked_files,
    extract_file_markers,
    find_file_by_name,
    parse_file_request,
    send_telegram_file,
)
from app.telegram_incoming import (
    AUDIO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    build_user_message_for_incoming,
    resolve_incoming_dir,
    save_telegram_upload,
)
from app.openclaw.client import OpenClawClient, build_openclaw_client


LOGGER = logging.getLogger(__name__)

CHAT_ACTIVE: Final[int] = 1
REMINDER_MENU: Final[int] = 2
REMINDER_CREATE: Final[int] = 3

OPENCLAW_CLIENT_KEY = "openclaw_client"
SETTINGS_KEY = "settings"
SELECTED_WORKSPACE_KEY = "selected_workspace"
PENDING_WORKSPACE_KEY = "pending_workspace"
WORKSPACE_AUTH_KEY = "workspace_authenticated"
WORKSPACE_AUTH_ATTEMPTS_KEY = "workspace_auth_attempts"
AUTH_LOCKOUT_STORE_KEY = "auth_lockout_store"
AUDIT_LOG_NAME = "file-delivery-audit.jsonl"


def build_application(settings: Settings) -> Application:
    client = build_openclaw_client(settings)
    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(_build_post_init(settings))
        .build()
    )

    application.bot_data[OPENCLAW_CLIENT_KEY] = client
    application.bot_data[SETTINGS_KEY] = settings
    application.bot_data[AUTH_LOCKOUT_STORE_KEY] = AuthLockoutStore(
        settings.data_dir / "auth-lockouts.json",
        max_attempts=settings.auth_max_attempts,
        lockout_seconds=settings.auth_lockout_seconds,
    )
    _warn_default_workspace_passwords(settings)
    # ConversationHandler del chat antes que /salir global: si no, /salir no cierra
    # CHAT_ACTIVE y /chat puede reanudar el perfil sin nueva contraseña.
    application.add_handler(_build_main_conversation())
    application.add_handler(
        MessageHandler(
            (filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO) & ~filters.COMMAND,
            routed_orphan_media,
        )
    )
    application.add_handler(CommandHandler("workspace", workspace_command))
    application.add_handler(
        CallbackQueryHandler(
            workspace_select_callback,
            pattern=r"^workspace:select:(admin|empleado)$",
        )
    )
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("estado", status_command))
    application.add_handler(CommandHandler("get", get_command))
    application.add_handler(CommandHandler("salir", exit_command))
    application.add_handler(CommandHandler("prueba_llm", prueba_llm_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, routed_text_message)
    )
    application.add_error_handler(error_handler)
    return application


def _build_post_init(settings: Settings):
    async def _post_init(application: Application) -> None:
        if not settings.sync_telegram_commands:
            return
        await application.bot.set_my_commands(
            [
                BotCommand("start", "Muestra ayuda del bot"),
                BotCommand("chat", "Habla con OpenClaw"),
                BotCommand("correo", "Redactar o enviar Gmail (mismo gateway)"),
                BotCommand("comunicaciones", "Recordatorios; Meet crear/cancelar (admin)"),
                BotCommand("get", "Recibe un archivo por nombre"),
                BotCommand("recordatorios", "Lista o crea recordatorios"),
                BotCommand("workspace", "Cambia entre admin y empleado"),
                BotCommand("estado", "Revisa el estado de OpenClaw"),
                BotCommand("prueba_llm", "Prueba LLM admin + registro (solo perfil admin)"),
                BotCommand("salir", "Sale del chat y cierra sesión de perfil"),
            ]
        )

    return _post_init


def _conversation_side_commands() -> list:
    """Comandos que deben funcionar también dentro del modo /chat o recordatorios."""
    return [
        CommandHandler("workspace", workspace_command_in_conversation),
        CommandHandler("chat", enter_chat_mode),
        CommandHandler("correo", enter_correo_mode),
        CommandHandler("comunicaciones", enter_comunicaciones_mode),
        CommandHandler("estado", status_command_in_conversation),
    ]


def _build_main_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("chat", enter_chat_mode),
            CommandHandler("correo", enter_correo_mode),
            CommandHandler("comunicaciones", enter_comunicaciones_mode),
            CommandHandler("recordatorios", reminders_menu_command),
        ],
        states={
            CHAT_ACTIVE: [
                CommandHandler("get", get_command),
                *_conversation_side_commands(),
                MessageHandler(
                    (filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO) & ~filters.COMMAND,
                    forward_chat_media,
                ),
                MessageHandler(filters.TEXT & ~filters.COMMAND, forward_chat_message),
            ],
            REMINDER_MENU: [
                *_conversation_side_commands(),
                CallbackQueryHandler(reminder_list_callback, pattern=r"^reminders:list$"),
                CallbackQueryHandler(
                    reminder_create_prompt_callback,
                    pattern=r"^reminders:create$",
                ),
                CallbackQueryHandler(reminders_close_callback, pattern=r"^reminders:close$"),
            ],
            REMINDER_CREATE: [
                *_conversation_side_commands(),
                MessageHandler(
                    (filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO) & ~filters.COMMAND,
                    reminder_reject_media,
                ),
                MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_create_message),
            ],
        },
        fallbacks=[
            CommandHandler("salir", exit_command),
            CommandHandler("start", start_command),
        ],
        allow_reentry=True,
    )


def _get_client(context: ContextTypes.DEFAULT_TYPE) -> OpenClawClient:
    return context.application.bot_data[OPENCLAW_CLIENT_KEY]


def _get_lockout_store(context: ContextTypes.DEFAULT_TYPE) -> AuthLockoutStore:
    return context.application.bot_data[AUTH_LOCKOUT_STORE_KEY]


def _warn_default_workspace_passwords(settings: Settings) -> None:
    for name, default in DEFAULT_WORKSPACE_PASSWORDS.items():
        if settings.workspace_passwords.get(name) == default:
            LOGGER.warning(
                "Contraseña por defecto activa para perfil %s; cambia TELEGRAM_%s_PASSWORD en producción",
                name,
                name.upper(),
            )


def _lockout_reply(lockout) -> str:
    minutes = max(1, (lockout.seconds_remaining + 59) // 60)
    return (
        f"Demasiados intentos fallidos. Acceso bloqueado durante ~{minutes} min.\n"
        "Vuelve a intentar más tarde o contacta al administrador del sistema."
    )


def _get_settings(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return context.application.bot_data[SETTINGS_KEY]


def _normalize_workspace_name(raw: str) -> str | None:
    normalized = raw.strip().lower()
    mapping = {
        "admin": "admin",
        "administrador": "admin",
        "empleado": "empleado",
    }
    return mapping.get(normalized)


async def _ensure_authorized(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    settings = _get_settings(context)
    user = update.effective_user
    if user is None:
        return False

    if not settings.allowed_user_ids and not settings.allowed_usernames:
        return True

    username = (user.username or "").lower()
    if user.id in settings.allowed_user_ids or username in settings.allowed_usernames:
        return True

    LOGGER.warning(
        "Telegram acceso denegado: user_id=%s username=%r (configurar TELEGRAM_ALLOWED_USER_IDS)",
        user.id,
        user.username,
    )
    if update.message is not None:
        await update.message.reply_text("No tienes permiso para usar este bot.")
    elif update.callback_query is not None:
        await update.callback_query.answer("No autorizado", show_alert=True)
    return False


def _available_workspace_names(settings: Settings) -> list[str]:
    return settings.workspace_names()


def _workspace_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    settings.get_workspace(workspace_name).label,
                    callback_data=f"workspace:select:{workspace_name}",
                )
            ]
            for workspace_name in _available_workspace_names(settings)
        ]
    )


def _resolve_workspace_from_context(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    settings = _get_settings(context)
    selected = context.user_data.get(SELECTED_WORKSPACE_KEY)
    if not context.user_data.get(WORKSPACE_AUTH_KEY):
        return None
    if isinstance(selected, str) and selected in settings.workspaces:
        return selected
    return None


def _clear_stale_pending_if_authenticated(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sesión válida anula un pending_workspace obsoleto (p. ej. callback antiguo)."""
    if _resolve_workspace_from_context(context) is not None:
        context.user_data.pop(PENDING_WORKSPACE_KEY, None)
        context.user_data.pop(WORKSPACE_AUTH_ATTEMPTS_KEY, None)


def _get_pending_workspace_switch(
    context: ContextTypes.DEFAULT_TYPE,
    settings: Settings,
) -> str | None:
    _clear_stale_pending_if_authenticated(context)
    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if isinstance(pending, str) and pending in settings.workspaces:
        return pending
    return None


async def _reply_pending_password_required(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    settings: Settings,
    pending: str,
    extra_hint: str = "",
) -> None:
    workspace = settings.get_workspace(pending)
    hint = (
        f"Aún falta la contraseña del perfil {workspace.label}.\n"
        "Escríbela en un mensaje de texto (no uses /chat ni /correo hasta ver «Contraseña correcta»).\n"
        "Usa /salir para cancelar el cambio de perfil."
    )
    if extra_hint:
        hint = f"{hint}\n{extra_hint}"
    if update.message is not None:
        await update.message.reply_text(hint)


async def _require_authenticated_workspace(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str | None:
    """Devuelve el workspace activo o envía el mensaje de error correspondiente."""
    if update.message is None:
        return None

    settings = _get_settings(context)
    _clear_stale_pending_if_authenticated(context)

    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is not None:
        return workspace_name

    pending = _get_pending_workspace_switch(context, settings)
    if pending is not None:
        await _reply_pending_password_required(update, context, settings=settings, pending=pending)
        return None

    if not context.user_data.get(WORKSPACE_AUTH_KEY):
        await update.message.reply_text(
            "No hay un perfil autenticado.\n"
            f"Usa /workspace para elegir entre {_workspace_prompt(settings)} e ingresar la contraseña.",
            reply_markup=_workspace_keyboard(settings)
            if _available_workspace_names(settings)
            else None,
        )
        return None

    await update.message.reply_text(
        "No hay un workspace activo.\n"
        f"Usa /workspace para elegir entre {_workspace_prompt(settings)}.",
        reply_markup=_workspace_keyboard(settings)
        if _available_workspace_names(settings)
        else None,
    )
    return None


def _is_admin_validated(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return (
        context.user_data.get(WORKSPACE_AUTH_KEY, False)
        and context.user_data.get(SELECTED_WORKSPACE_KEY) == "admin"
    )


def _audit_path(settings: Settings) -> Path:
    return settings.data_dir / AUDIT_LOG_NAME


def _file_access_for(settings: Settings, workspace_name: str) -> tuple[list, list]:
    return settings.read_roots_for(workspace_name), settings.deny_roots_for(workspace_name)


def _clear_workspace_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(WORKSPACE_AUTH_KEY, None)
    context.user_data.pop(SELECTED_WORKSPACE_KEY, None)
    context.user_data.pop(PENDING_WORKSPACE_KEY, None)
    context.user_data.pop(WORKSPACE_AUTH_ATTEMPTS_KEY, None)
    context.user_data.pop("chat_active", None)


async def _secure_delete_message(update: Update) -> None:
    message = update.message
    if message is None:
        return
    try:
        await message.delete()
    except Exception:  # pragma: no cover
        LOGGER.warning(
            "No se pudo borrar el mensaje sensible user_id=%s message_id=%s",
            update.effective_user.id if update.effective_user else None,
            message.message_id,
        )


async def _reply_workspace_message(update: Update, text: str) -> None:
    if update.message is not None:
        await update.message.reply_text(text)
    elif update.callback_query is not None and update.callback_query.message is not None:
        await update.callback_query.message.reply_text(text)


async def _begin_workspace_switch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    workspace_name: str,
) -> None:
    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
    user = update.effective_user
    if user is not None:
        lockout_store = _get_lockout_store(context)
        lockout = lockout_store.ensure_can_attempt(user.id)
        if lockout.locked:
            message = _lockout_reply(lockout)
            await _reply_workspace_message(update, message)
            return

    if (
        context.user_data.get(WORKSPACE_AUTH_KEY)
        and context.user_data.get(SELECTED_WORKSPACE_KEY) == workspace_name
        and not context.user_data.get(PENDING_WORKSPACE_KEY)
    ):
        await _reply_workspace_message(
            update,
            f"Ya tienes sesión activa como {workspace.label}.\n"
            "Escribe tu consulta o usa /chat, /correo o /comunicaciones.\n"
            "Para cambiar de perfil: /workspace <otro> (pedirá la contraseña del nuevo perfil).",
        )
        return

    if context.user_data.get(PENDING_WORKSPACE_KEY) == workspace_name:
        if (
            context.user_data.get(WORKSPACE_AUTH_KEY)
            and context.user_data.get(SELECTED_WORKSPACE_KEY) == workspace_name
        ):
            context.user_data.pop(PENDING_WORKSPACE_KEY, None)
            context.user_data.pop(WORKSPACE_AUTH_ATTEMPTS_KEY, None)
            await _reply_workspace_message(
                update,
                f"Ya tienes sesión activa como {workspace.label}.",
            )
            return
        await _reply_workspace_message(
            update,
            f"Pendiente la contraseña de {workspace.label}.\n"
            "Escríbela en un mensaje de texto normal (se borrará al enviarlo). "
            "No pulses el botón otra vez.\n"
            "Usa /salir para cancelar.",
        )
        return

    if user is not None:
        _get_lockout_store(context).reset_attempts(user.id)

    # Cambio de perfil: invalidar sesión anterior hasta confirmar contraseña.
    context.user_data.pop(WORKSPACE_AUTH_KEY, None)
    context.user_data.pop(SELECTED_WORKSPACE_KEY, None)
    context.user_data.pop("chat_active", None)
    context.user_data[PENDING_WORKSPACE_KEY] = workspace_name
    context.user_data[WORKSPACE_AUTH_ATTEMPTS_KEY] = 0
    prompt = (
        f"Perfil elegido: {workspace.label}.\n\n"
        "El botón solo selecciona el perfil; no inicia sesión.\n"
        "Ahora escribe la contraseña de ese perfil en un mensaje de texto normal "
        "(no es un comando). El mensaje se borrará al enviarlo.\n"
        "Cuando veas «Contraseña correcta», podrás usar /chat.\n"
        "Usa /salir para cancelar."
    )
    await _reply_workspace_message(update, prompt)


async def _complete_workspace_switch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    workspace_name: str,
) -> None:
    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
    context.user_data[SELECTED_WORKSPACE_KEY] = workspace_name
    context.user_data[WORKSPACE_AUTH_KEY] = True
    context.user_data.pop(PENDING_WORKSPACE_KEY, None)
    user = update.effective_user
    if user is not None:
        _get_lockout_store(context).clear_user(user.id)
    if update.message is not None:
        await update.message.reply_text(
            "Contraseña correcta.\n"
            f"Workspace activo: {workspace.label}.\n"
            "Ya puedes escribir tu consulta aquí (sin /chat) o usar /chat para modo conversación."
        )


def _apply_workspace_argument(
    context: ContextTypes.DEFAULT_TYPE,
    raw_value: str | None,
) -> str | None:
    if raw_value is None:
        return _resolve_workspace_from_context(context)

    settings = _get_settings(context)
    normalized = _normalize_workspace_name(raw_value)
    if normalized is None or normalized not in settings.workspaces:
        return None
    if context.user_data.get(WORKSPACE_AUTH_KEY) and context.user_data.get(
        SELECTED_WORKSPACE_KEY
    ) == normalized:
        return normalized
    return None


def _workspace_prompt(settings: Settings) -> str:
    return ", ".join(
        settings.get_workspace(name).label for name in _available_workspace_names(settings)
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END

    settings = _get_settings(context)
    current_workspace = _resolve_workspace_from_context(context)
    current_label = (
        settings.get_workspace(current_workspace).label if current_workspace else "sin seleccionar"
    )
    configured = _available_workspace_names(settings)
    if configured:
        workspace_summary = ", ".join(settings.get_workspace(name).label for name in configured)
    else:
        workspace_summary = "modo mock"

    await update.message.reply_text(
        "Bot listo para OpenClaw.\n\n"
        f"Workspaces configurados: {workspace_summary}.\n"
        f"Workspace activo: {current_label}.\n\n"
        "Usa /workspace para elegir perfil: pulsa un botón o escribe /workspace admin|empleado, "
        "luego escribe la contraseña del perfil, y después /chat.\n"
        "Usa /chat para hablar con el agente remoto.\n"
        "Usa /correo para redactar o enviar correo Gmail (borrador y confirmación en este chat; "
        "mismas credenciales que el asistente en el gateway).\n"
        "Usa /comunicaciones para recordatorios, seguimientos y confirmaciones (admin-comms); "
        "en perfil Administrador también **crear y cancelar** reuniones Google Meet/Calendar.\n"
        "En modo /chat puedes pedir archivos del equipo en lenguaje natural "
        "(entrégame el archivo informe.pptx, …) o **enviar un documento o foto** para correo con adjunto.\n"
        "Usa /get nombre_archivo para recibir un adjunto directo desde el equipo.\n"
        "Usa /recordatorios para revisar o crear tareas.\n"
        "Usa /estado para revisar conectividad.\n"
        "Usa /prueba_llm <texto> para una prueba registrada solo en perfil Administrador (ver README).\n"
        "Usa /salir para salir del modo chat y cerrar la sesión del perfil activo."
    )
    return ConversationHandler.END


async def prueba_llm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return

    settings = _get_settings(context)
    if settings.openclaw_mode != "gateway":
        await update.message.reply_text(
            "/prueba_llm solo tiene sentido con OPENCLAW_MODE=gateway y gateway admin accesible."
        )
        return

    if "admin" not in settings.workspaces:
        await update.message.reply_text("No hay gateway admin configurado (OPENCLAW_ADMIN_*).")
        return

    _clear_stale_pending_if_authenticated(context)
    pending = _get_pending_workspace_switch(context, settings)
    if pending is not None:
        await update.message.reply_text(
            "Hay un cambio de perfil pendiente de contraseña. Completa /workspace o usa /salir."
        )
        return

    if not context.user_data.get(WORKSPACE_AUTH_KEY):
        await update.message.reply_text(
            "Autentica el perfil Administrador con /workspace admin y la contraseña, luego reintenta."
        )
        return

    if _resolve_workspace_from_context(context) != "admin":
        await update.message.reply_text(
            "Este comando solo se ejecuta con el perfil Administrador activo. "
            "Usa /workspace admin, introduce la contraseña y vuelve a enviar /prueba_llm."
        )
        return

    log_path = settings.admin_llm_test_log_path
    if log_path is None:
        await update.message.reply_text(
            "Falta TELEGRAM_ADMIN_LLM_TEST_LOG_PATH en docker/telegram/.env "
            "y el volumen del JSONL (ver docker/telegram/README.md)."
        )
        return

    prompt = " ".join(context.args).strip()
    if not prompt:
        await update.message.reply_text("Uso: /prueba_llm <prompt de prueba en una sola línea>")
        return

    client = _get_client(context)
    user = update.effective_user
    if user is None:
        return
    chat_id = update.effective_chat.id if update.effective_chat else user.id
    t0 = time.perf_counter()
    try:
        reply = await run_with_telegram_progress(
            update,
            label="Ejecutando prueba LLM…",
            coro_factory=lambda: client.chat(
                workspace="admin",
                user_id=user.id,
                username=user.username,
                message=prompt,
                chat_id=chat_id,
                admin_validated=True,
            ),
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("prueba_llm chat failed")
        latency = time.perf_counter() - t0
        await asyncio.to_thread(
            append_llm_test_run,
            log_path,
            input_text=prompt,
            output_text=f"<error: {exc!r}>",
            latency_seconds=latency,
            source="telegram",
            extra={"ok": False},
        )
        await update.message.reply_text(
            format_gateway_error(
                settings,
                "admin",
                exc,
                action="ejecutar la prueba LLM",
            )
        )
        return

    latency = time.perf_counter() - t0
    await asyncio.to_thread(
        append_llm_test_run,
        log_path,
        input_text=prompt,
        output_text=reply,
        latency_seconds=latency,
        source="telegram",
        extra={"ok": True},
    )
    await update.message.reply_text(
        "[Administrador] Prueba completada.\n"
        "Registro completado. Revisa el panel de OpenClaw.\n\n"
        f"(latencia ~{latency:.2f}s)\n\n{reply[:3500]}"
        + ("…" if len(reply) > 3500 else "")
    )


async def enter_chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END

    workspace_name = await _require_authenticated_workspace(update, context)
    if workspace_name is None:
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
    incoming_hint = resolve_incoming_dir(settings.host_home)
    await update.message.reply_text(
        f"Entraste en modo chat con {workspace.label}.\n"
        "Escribe cualquier mensaje y lo enviaremos a OpenClaw por Telegram.\n"
        "Puedes pedir correo Gmail (borrador y envío tras confirmación); también /correo resume el protocolo.\n"
        "Puedes pedir recordatorios y comunicaciones formales con /comunicaciones (admin-comms). "
        "En perfil **Administrador**: crear y cancelar reuniones Meet/Calendar (solo admin).\n"
        "Puedes **enviar un documento o foto**; el bot lo guarda y el asistente puede usarlo en Gmail con "
        f"`gog ... --attach` y la ruta que te indique (carpeta típica: `{incoming_hint}`).\n"
        "Para recibir archivos del equipo usa lenguaje natural: entrégame el archivo X, envíame X, etc.\n"
        "Usa /salir para terminar el chat y cerrar la sesión del perfil."
    )
    context.user_data["chat_active"] = True
    return CHAT_ACTIVE


async def enter_correo_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Activa el mismo flujo que /chat, con recordatorio del protocolo Gmail del gateway."""
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END

    workspace_name = await _require_authenticated_workspace(update, context)
    if workspace_name is None:
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
    incoming_hint = resolve_incoming_dir(settings.host_home)
    await update.message.reply_text(
        f"Modo correo con {workspace.label} (mismo gateway y credenciales GOG que el asistente).\n\n"
        "Indica destinatario, asunto y texto del mensaje en tus siguientes mensajes.\n"
        "También puedes **enviar un documento o foto**: se guarda en el equipo y el borrador puede incluir "
        f"`--attach` con esa ruta (típico: `{incoming_hint}`).\n"
        "El agente creará primero un borrador en Gmail y te mostrará su ID.\n"
        "Para enviar, una sola aclaración al estilo borrador siguiente basta si ya mostraste el ID: "
        "«envíalo», «mándalo», «hazlo», «dale», «sí», «vale», «ok», «confirmo», «procede», "
        "«proceder con el envío» o «Enviar borrador ID: …» con el número que devolvió gog.\n\n"
        "Usa /salir para terminar el modo chat y cerrar la sesión del perfil."
    )
    context.user_data["chat_active"] = True
    return CHAT_ACTIVE


async def enter_comunicaciones_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Modo comunicaciones: admin-comms (recordatorios) y Meet solo en perfil admin."""
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END

    workspace_name = await _require_authenticated_workspace(update, context)
    if workspace_name is None:
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
    meet_hint = (
        "En perfil **Administrador** también puedes **crear** reuniones con **Google Meet** "
        "(confirmación en este chat antes de `gog calendar create`) o **Zoom** "
        "(`zoom-meeting-create.sh` tras confirmación; invitación por correo a los invitados). "
        "Puedes **cancelar** Meet o Zoom (motivo → asunto; **preguntaré tu nombre para Atte** si no lo indicas; "
        "resumen con invitados; confirmación → script con `--attendees`).\n"
        if workspace_name == "admin"
        else "Para **crear o cancelar** reuniones en Google Meet/Calendar o **Zoom**, usa perfil Administrador: /workspace admin.\n"
    )
    await update.message.reply_text(
        f"Modo comunicaciones con {workspace.label}.\n\n"
        "Puedes pedir:\n"
        "• **Recordatorio**, seguimiento o confirmación (redacto borrador formal)\n"
        "• Guardado en `~/Documentos/Comunicaciones/` y estado en LOGS_COMMS\n"
        f"{meet_hint}"
        "Confirmaciones válidas en Telegram: «envíalo», «vale», «confirma», «agéndala», «cancela la reunión», etc.\n"
        "El correo Gmail sigue el mismo flujo borrador → confirmación (`/correo` si solo quieres email).\n\n"
        "Usa /salir para cerrar sesión del perfil."
    )
    context.user_data["chat_active"] = True
    return CHAT_ACTIVE


async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if not context.args:
        await update.message.reply_text(
            "Uso: /get nombre_archivo.ext\n"
            "También puedes escribir en el chat: get informe.pptx"
        )
        return _current_conversation_state(context)

    filename = " ".join(context.args).strip()
    return await _handle_file_request(update, context, filename)


def _current_conversation_state(context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data.get("chat_active"):
        return CHAT_ACTIVE
    return ConversationHandler.END


async def _handle_file_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    filename: str,
) -> int:
    if update.message is None or update.effective_user is None:
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await update.message.reply_text("Primero selecciona un workspace con /workspace.")
        return ConversationHandler.END

    workspace = settings.get_workspace(workspace_name)
    read_roots, deny_roots = _file_access_for(settings, workspace_name)
    audit = _audit_path(settings)
    user_id = update.effective_user.id
    found = find_file_by_name(filename, read_roots, deny_roots=deny_roots)
    if found is not None:
        await send_telegram_file(
            update,
            found,
            read_roots=read_roots,
            deny_roots=deny_roots,
            caption=f"[{workspace.label}] {found.name}",
            audit_path=audit,
            user_id=user_id,
            workspace=workspace_name,
        )
        return CHAT_ACTIVE if context.user_data.get("chat_active") else ConversationHandler.END

    client = _get_client(context)
    chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    prompt = (
        f"[Solicitud Telegram — entregar archivo] El usuario pide recibir en este chat de Telegram "
        f"el archivo: {filename}. Localízalo o indícalo con [[TELEGRAM_FILE:/ruta/absoluta]]. "
        "No pidas chat_id ni confirmes el canal: ya es Telegram."
    )
    try:
        reply = await run_with_telegram_progress(
            update,
            label="Buscando el archivo solicitado…",
            coro_factory=lambda: client.chat(
                workspace=workspace_name,
                user_id=update.effective_user.id,
                username=update.effective_user.username,
                message=prompt,
                chat_id=chat_id,
                admin_validated=_is_admin_validated(context),
            ),
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("File request forwarding failed")
        await update.message.reply_text(
            format_gateway_error(
                settings,
                workspace_name,
                exc,
                action="localizar el archivo solicitado",
            )
        )
        return CHAT_ACTIVE if context.user_data.get("chat_active") else ConversationHandler.END

    await _reply_with_optional_files(update, settings, workspace_name, reply)
    return CHAT_ACTIVE if context.user_data.get("chat_active") else ConversationHandler.END


async def _reply_with_optional_files(
    update: Update,
    settings: Settings,
    workspace_name: str,
    reply: str,
) -> None:
    if update.message is None or update.effective_user is None:
        return
    workspace = settings.get_workspace(workspace_name)
    read_roots, deny_roots = _file_access_for(settings, workspace_name)
    clean_text, paths = extract_file_markers(reply)
    if clean_text:
        await update.message.reply_text(f"[{workspace.label}]\n{clean_text}")
    elif paths:
        await update.message.reply_text(f"[{workspace.label}] Enviando archivo(s)...")
    elif (reply or "").strip():
        await update.message.reply_text(f"[{workspace.label}]\n{reply.strip()}")
    else:
        await update.message.reply_text(
            f"[{workspace.label}] La acción se procesó en el gateway, pero no hubo texto en la respuesta. "
            "Revisa LOGS_COMMS o el calendario si esperabas confirmación de una reunión."
        )
    await deliver_marked_files(
        update,
        read_roots=read_roots,
        deny_roots=deny_roots,
        paths=paths,
        audit_path=_audit_path(settings),
        user_id=update.effective_user.id,
        workspace=workspace_name,
    )


async def workspace_command_in_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await workspace_command(update, context)
    return _current_conversation_state(context)


async def status_command_in_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await status_command(update, context)
    return _current_conversation_state(context)


async def _deliver_openclaw_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    text: str,
    progress_label: str = "Procesando tu consulta…",
) -> None:
    if update.message is None or update.effective_user is None:
        return

    settings = _get_settings(context)
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await update.message.reply_text("Primero selecciona un workspace con /workspace.")
        return

    client = _get_client(context)
    chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    file_query = parse_file_request(text)
    if file_query is not None:
        await _handle_file_request(update, context, file_query)
        return

    try:
        reply = await run_with_telegram_progress(
            update,
            label=progress_label,
            coro_factory=lambda: client.chat(
                workspace=workspace_name,
                user_id=update.effective_user.id,
                username=update.effective_user.username,
                message=text,
                chat_id=chat_id,
                admin_validated=_is_admin_validated(context),
            ),
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("OpenClaw chat delivery failed")
        await update.message.reply_text(
            format_gateway_error(
                settings,
                workspace_name,
                exc,
                action="obtener la respuesta del agente",
            )
        )
        return

    await _reply_with_optional_files(update, settings, workspace_name, reply)


async def forward_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if update.effective_user is None:
        return CHAT_ACTIVE

    _clear_stale_pending_if_authenticated(context)
    if _get_pending_workspace_switch(context, _get_settings(context)):
        await workspace_password_message(update, context)
        return CHAT_ACTIVE

    if not context.user_data.get(WORKSPACE_AUTH_KEY):
        await update.message.reply_text(
            "La sesión del perfil está cerrada.\n"
            "Usa /workspace para autenticarte y luego /chat."
        )
        return ConversationHandler.END

    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await update.message.reply_text("Primero selecciona un workspace con /workspace.")
        return ConversationHandler.END

    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text(
            "Enviame un mensaje de texto o un documento/foto (en /chat) para pasarlo a OpenClaw."
        )
        return CHAT_ACTIVE

    context.user_data["chat_active"] = True
    await _deliver_openclaw_text(update, context, text=text)
    return CHAT_ACTIVE


async def forward_chat_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda documento/foto de Telegram y reenvía al gateway con ruta para --attach."""
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if update.effective_user is None:
        return CHAT_ACTIVE

    if context.user_data.get(PENDING_WORKSPACE_KEY):
        await update.message.reply_text(
            "Para iniciar sesión en un perfil envía la **contraseña en texto**, no un archivo ni foto."
        )
        return CHAT_ACTIVE

    if not context.user_data.get(WORKSPACE_AUTH_KEY):
        await update.message.reply_text(
            "La sesión del perfil está cerrada.\n"
            "Usa /workspace para autenticarte y luego /chat."
        )
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await update.message.reply_text("Primero selecciona un workspace con /workspace.")
        return ConversationHandler.END

    write_roots = settings.write_roots_for(workspace_name)
    deny_roots = settings.deny_roots_for(workspace_name)
    user_id = update.effective_user.id
    try:
        saved = await save_telegram_upload(
            update,
            context,
            host_home=settings.host_home,
            write_roots=write_roots,
            deny_roots=deny_roots,
            user_id=user_id,
        )
    except PermissionError as exc:
        await update.message.reply_text(str(exc))
        return CHAT_ACTIVE
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return CHAT_ACTIVE
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Fallo guardando archivo entrante de Telegram")
        await update.message.reply_text(
            format_gateway_error(
                settings,
                workspace_name,
                exc,
                action="guardar el archivo recibido por Telegram",
            )
        )
        return CHAT_ACTIVE

    is_image = saved.suffix.lower() in IMAGE_EXTENSIONS
    is_audio = saved.suffix.lower() in AUDIO_EXTENSIONS
    if is_audio:
        confirm_label = "Audio guardado en el equipo; transcribiendo con Whisper…"
    elif is_image:
        confirm_label = "Imagen guardada en el equipo; enviando al asistente…"
    else:
        confirm_label = "Archivo guardado en el equipo; enviando al asistente…"
    await update.message.reply_text(f"{confirm_label}\n{saved.resolve()}")
    prompt = build_user_message_for_incoming(
        saved_path=saved,
        caption=update.message.caption,
    )
    context.user_data["chat_active"] = True
    client = _get_client(context)
    chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    image_path_arg = saved if is_image else None
    if is_audio:
        progress_label = "Transcribiendo audio…"
    elif is_image:
        progress_label = "Analizando imagen…"
    else:
        progress_label = "Procesando tu consulta…"
    try:
        reply = await run_with_telegram_progress(
            update,
            label=progress_label,
            coro_factory=lambda: client.chat(
                workspace=workspace_name,
                user_id=user_id,
                username=update.effective_user.username,
                message=prompt,
                chat_id=chat_id,
                admin_validated=_is_admin_validated(context),
                image_path=image_path_arg,
            ),
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Chat forwarding failed (media)")
        await update.message.reply_text(
            format_gateway_error(
                settings,
                workspace_name,
                exc,
                action="obtener la respuesta del agente",
            )
        )
        return CHAT_ACTIVE

    await _reply_with_optional_files(update, settings, workspace_name, reply)
    return CHAT_ACTIVE


async def reminder_reject_media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    if update.message:
        await update.message.reply_text(
            "Solo puedo registrar recordatorios con texto. Escribe el contenido del recordatorio."
        )
    return REMINDER_CREATE


async def routed_orphan_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return
    if context.user_data.get(PENDING_WORKSPACE_KEY):
        await update.message.reply_text(
            "Para iniciar sesión en un perfil envía la **contraseña en texto**, no un archivo, foto ni audio."
        )
        return
    await update.message.reply_text(
        "Para que el asistente procese un archivo, foto o audio, entra antes con /chat "
        "(perfil autenticado) y vuelve a enviar el documento, la foto o el audio."
    )


async def reminders_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace_name = _apply_workspace_argument(context, context.args[0] if context.args else None)
    if workspace_name is None:
        await update.message.reply_text(
            "No hay un workspace activo.\n"
            f"Usa /workspace para elegir entre {_workspace_prompt(settings)}.",
            reply_markup=_workspace_keyboard(settings)
            if _available_workspace_names(settings)
            else None,
        )
        return ConversationHandler.END

    workspace = settings.get_workspace(workspace_name)
    await update.message.reply_text(
        f"Gestion de recordatorios en {workspace.label}:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Ver recordatorios", callback_data="reminders:list"),
                    InlineKeyboardButton("Crear recordatorio", callback_data="reminders:create"),
                ],
                [
                    InlineKeyboardButton("Cerrar", callback_data="reminders:close"),
                ],
            ]
        ),
    )
    return REMINDER_MENU


async def reminder_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await _ensure_authorized(update, context):
        return ConversationHandler.END

    query = update.callback_query
    user = update.effective_user
    if query is None or user is None:
        return REMINDER_MENU

    await query.answer()
    settings = _get_settings(context)
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await query.edit_message_text("No hay un workspace activo. Usa /workspace.")
        return ConversationHandler.END

    try:
        reminders = await _get_client(context).list_reminders(
            workspace=workspace_name,
            user_id=user.id,
            username=user.username,
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Reminder listing failed")
        await query.edit_message_text(
            format_gateway_error(
                settings,
                workspace_name,
                exc,
                action="cargar los recordatorios",
            )
        )
        return REMINDER_MENU

    workspace = settings.get_workspace(workspace_name)
    await query.edit_message_text(
        f"[{workspace.label}]\n{reminders}",
        reply_markup=query.message.reply_markup if query.message else None,
    )
    return REMINDER_MENU


async def reminder_create_prompt_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    if not await _ensure_authorized(update, context):
        return ConversationHandler.END

    query = update.callback_query
    if query is None:
        return REMINDER_MENU

    await query.answer()
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await query.edit_message_text("No hay un workspace activo. Usa /workspace.")
        return ConversationHandler.END

    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
    if query.message is not None:
        await query.message.reply_text(
            f"Escribeme el texto del nuevo recordatorio para {workspace.label}.\n"
            "Usa /salir si quieres cancelar."
        )
    return REMINDER_CREATE


async def reminder_create_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if update.effective_user is None:
        return REMINDER_CREATE

    settings = _get_settings(context)
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        await update.message.reply_text("Primero selecciona un workspace con /workspace.")
        return ConversationHandler.END

    content = (update.message.text or "").strip()
    if not content:
        await update.message.reply_text("El recordatorio no puede estar vacio.")
        return REMINDER_CREATE

    try:
        result = await _get_client(context).create_reminder(
            workspace=workspace_name,
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            content=content,
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Reminder creation failed")
        await update.message.reply_text(
            format_gateway_error(
                settings,
                workspace_name,
                exc,
                action="crear el recordatorio",
            )
        )
        return REMINDER_CREATE

    workspace = settings.get_workspace(workspace_name)
    await update.message.reply_text(f"[{workspace.label}]\n{result}")
    return REMINDER_MENU


async def reminders_close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Modulo de recordatorios cerrado.")
    return ConversationHandler.END


async def exit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if context.user_data.get(PENDING_WORKSPACE_KEY):
        return await workspace_password_cancel(update, context)
    had_workspace = bool(context.user_data.get(WORKSPACE_AUTH_KEY))
    _clear_workspace_session(context)
    if update.message is not None:
        if had_workspace:
            await update.message.reply_text(
                "Sali del modo actual y cerré la sesión del perfil.\n"
                "Usa /workspace para autenticarte de nuevo."
            )
        else:
            await update.message.reply_text("Sali del modo actual.")
    elif update.callback_query is not None:
        await update.callback_query.answer()
        text = (
            "Sali del modo actual y cerré la sesión del perfil."
            if had_workspace
            else "Sali del modo actual."
        )
        await update.callback_query.edit_message_text(text)
    return ConversationHandler.END


async def workspace_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return

    settings = _get_settings(context)
    available = _available_workspace_names(settings)
    if not available:
        await update.message.reply_text("No hay workspaces configurados; el bot esta en modo mock.")
        return

    if context.args:
        workspace_name = _normalize_workspace_name(context.args[0])
        if workspace_name is None or workspace_name not in settings.workspaces:
            await update.message.reply_text("Workspace no valido. Usa /workspace admin o /workspace empleado.")
            return
        await _begin_workspace_switch(update, context, workspace_name)
        return

    current = _resolve_workspace_from_context(context)
    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if isinstance(pending, str) and pending in settings.workspaces:
        pending_label = settings.get_workspace(pending).label
        estado = f"Pendiente contraseña de {pending_label}. Escríbela en texto (no pulses el botón otra vez)."
    elif context.user_data.get(WORKSPACE_AUTH_KEY) and current:
        estado = f"Perfil autenticado: {settings.get_workspace(current).label}."
    else:
        estado = "Sin perfil autenticado (después de elegir con el botón debes escribir la contraseña)."
    await update.message.reply_text(
        f"{estado}\n\n"
        "Pulsa Administrador o Empleado y luego escribe la contraseña en el chat. "
        "El botón no basta para iniciar sesión.\n"
        "Cuando veas «Contraseña correcta», usa /chat, /correo o /comunicaciones.",
        reply_markup=_workspace_keyboard(settings),
    )


async def workspace_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    query = update.callback_query
    if query is None:
        return

    settings = _get_settings(context)
    workspace_name = query.data.split(":")[-1]
    if workspace_name not in settings.workspaces:
        return

    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if pending == workspace_name:
        await query.answer(
            "Escribe la contraseña en el chat (texto normal). No hace falta pulsar el botón otra vez.",
            show_alert=True,
        )
        return
    if (
        context.user_data.get(WORKSPACE_AUTH_KEY)
        and context.user_data.get(SELECTED_WORKSPACE_KEY) == workspace_name
        and not pending
    ):
        await query.answer(
            f"Ya tienes sesión en {settings.get_workspace(workspace_name).label}.",
            show_alert=True,
        )
        return

    await query.answer(
        "Siguiente paso: escribe la contraseña del perfil en el chat.",
        show_alert=True,
    )
    await _begin_workspace_switch(update, context, workspace_name)


async def workspace_password_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return

    settings = _get_settings(context)
    user = update.effective_user
    if user is None:
        return

    lockout_store = _get_lockout_store(context)
    lockout = lockout_store.ensure_can_attempt(user.id)
    if lockout.locked:
        await _secure_delete_message(update)
        await update.message.reply_text(_lockout_reply(lockout))
        return

    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if not isinstance(pending, str) or pending not in settings.workspaces:
        await update.message.reply_text("No hay un cambio de perfil pendiente. Usa /workspace.")
        return

    attempts = int(context.user_data.get(WORKSPACE_AUTH_ATTEMPTS_KEY, 0))
    if attempts >= settings.auth_max_attempts:
        await _secure_delete_message(update)
        context.user_data.pop(PENDING_WORKSPACE_KEY, None)
        await update.message.reply_text(
            "Demasiados intentos fallidos. Usa /workspace para volver a intentar."
        )
        return

    provided = (update.message.text or "").strip()
    await _secure_delete_message(update)

    expected = settings.workspace_passwords.get(pending, "")
    if not secrets.compare_digest(provided, expected):
        attempts += 1
        context.user_data[WORKSPACE_AUTH_ATTEMPTS_KEY] = attempts
        lockout = lockout_store.record_failure(user.id)
        if lockout.locked:
            context.user_data.pop(PENDING_WORKSPACE_KEY, None)
            await update.message.reply_text(_lockout_reply(lockout))
            return
        remaining = settings.auth_max_attempts - attempts
        if remaining <= 0:
            context.user_data.pop(PENDING_WORKSPACE_KEY, None)
            await update.message.reply_text(
                "Contraseña incorrecta. Se bloqueó el intento actual.\n"
                "Usa /workspace para empezar de nuevo."
            )
        else:
            await update.message.reply_text(
                "Contraseña incorrecta.\n"
                f"Te quedan {remaining} intento(s). Vuelve a escribir la contraseña "
                "o usa /salir para cancelar."
            )
        return

    context.user_data.pop(WORKSPACE_AUTH_ATTEMPTS_KEY, None)
    await _complete_workspace_switch(update, context, pending)


async def workspace_password_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop(PENDING_WORKSPACE_KEY, None)
    context.user_data.pop(WORKSPACE_AUTH_ATTEMPTS_KEY, None)
    if update.message is not None:
        await update.message.reply_text("Cambio de perfil cancelado.")
    return ConversationHandler.END


async def routed_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get(PENDING_WORKSPACE_KEY):
        settings = _get_settings(context)
        _clear_stale_pending_if_authenticated(context)
        if _get_pending_workspace_switch(context, settings):
            await workspace_password_message(update, context)
            return
    await default_text_message(update, context)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return

    settings = _get_settings(context)
    available = _available_workspace_names(settings)
    if not available:
        await update.message.reply_text("Modo mock activo. No hay gateways reales configurados.")
        return

    client = _get_client(context)
    results = await asyncio.gather(
        *[client.healthcheck(workspace=name) for name in available],
        return_exceptions=True,
    )

    lines = ["Estado de OpenClaw:"]
    for workspace_name, result in zip(available, results, strict=True):
        if isinstance(result, Exception):
            lines.append(
                format_gateway_error(
                    settings,
                    workspace_name,
                    result,
                    action="comprobar el estado del gateway",
                )
            )
        else:
            lines.append(f"- {result}")
    await update.message.reply_text("\n".join(lines))


async def default_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return

    text = (update.message.text or "").strip()
    if not text:
        return

    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is not None:
        context.user_data["chat_active"] = True
        await _deliver_openclaw_text(update, context, text=text)
        return

    await update.message.reply_text(
        "Primero elige un perfil con /workspace (botón + contraseña en texto).\n"
        "Después podrás escribir consultas directamente o usar /chat, /correo, /comunicaciones y /recordatorios."
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, Conflict):
        LOGGER.error(
            "Conflicto de polling: hay otra instancia del bot con el mismo token. "
            "Debe correr solo un telegram-openclaw-bot."
        )
        return
    LOGGER.exception("Unhandled Telegram error", exc_info=context.error)
