from __future__ import annotations

import asyncio
import logging
import secrets
import time
from pathlib import Path
from typing import Final

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
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

from app.config import Settings
from app.errors import format_gateway_error
from app.llm_test_log import append_llm_test_run
from app.file_delivery import (
    deliver_marked_files,
    extract_file_markers,
    find_file_by_name,
    parse_file_request,
    send_telegram_file,
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
MAX_WORKSPACE_PASSWORD_ATTEMPTS: Final[int] = 5
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
    # ConversationHandler del chat antes que /salir global: si no, /salir no cierra
    # CHAT_ACTIVE y /chat puede reanudar el perfil sin nueva contraseña.
    application.add_handler(_build_main_conversation())
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
                BotCommand("get", "Recibe un archivo por nombre"),
                BotCommand("recordatorios", "Lista o crea recordatorios"),
                BotCommand("workspace", "Cambia entre admin y empleado"),
                BotCommand("estado", "Revisa el estado de OpenClaw"),
                BotCommand("prueba_llm", "Prueba LLM admin + registro (solo perfil admin)"),
                BotCommand("salir", "Sale del chat y cierra sesión de perfil"),
            ]
        )

    return _post_init


def _build_main_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("chat", enter_chat_mode),
            CommandHandler("recordatorios", reminders_menu_command),
        ],
        states={
            CHAT_ACTIVE: [
                CommandHandler("get", get_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, forward_chat_message),
            ],
            REMINDER_MENU: [
                CallbackQueryHandler(reminder_list_callback, pattern=r"^reminders:list$"),
                CallbackQueryHandler(
                    reminder_create_prompt_callback,
                    pattern=r"^reminders:create$",
                ),
                CallbackQueryHandler(reminders_close_callback, pattern=r"^reminders:close$"),
            ],
            REMINDER_CREATE: [
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


async def _begin_workspace_switch(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    workspace_name: str,
) -> None:
    settings = _get_settings(context)
    workspace = settings.get_workspace(workspace_name)
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
    if update.message is not None:
        await update.message.reply_text(prompt)
    elif update.callback_query is not None and update.callback_query.message is not None:
        await update.callback_query.message.reply_text(prompt)


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
    if update.message is not None:
        await update.message.reply_text(
            "Contraseña correcta.\n"
            f"Workspace activo: {workspace.label}."
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
        "En modo chat puedes pedir archivos en lenguaje natural "
        "(entrégame el archivo informe.pptx, envíame el informe.docx, dame presentacion.pptx).\n"
        "Usa /get nombre_archivo para recibir un adjunto directo.\n"
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

    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if isinstance(pending, str) and pending in settings.workspaces:
        await update.message.reply_text(
            "Hay un cambio de perfil pendiente de contraseña. Completa /workspace o usa /salir."
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
        reply = await client.chat(
            workspace="admin",
            user_id=user.id,
            username=user.username,
            message=prompt,
            chat_id=chat_id,
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

    settings = _get_settings(context)
    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if isinstance(pending, str) and pending in settings.workspaces:
        workspace = settings.get_workspace(pending)
        await update.message.reply_text(
            f"Aún falta la contraseña del perfil {workspace.label}.\n"
            "Escríbela en un mensaje de texto (no uses /chat hasta ver «Contraseña correcta»).\n"
            "Usa /salir para cancelar el cambio de perfil."
        )
        return ConversationHandler.END

    if not context.user_data.get(WORKSPACE_AUTH_KEY):
        await update.message.reply_text(
            "No hay un perfil autenticado.\n"
            f"Usa /workspace para elegir entre {_workspace_prompt(settings)} e ingresar la contraseña.",
            reply_markup=_workspace_keyboard(settings)
            if _available_workspace_names(settings)
            else None,
        )
        return ConversationHandler.END

    workspace_name = _resolve_workspace_from_context(context)
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
        f"Entraste en modo chat con {workspace.label}.\n"
        "Escribe cualquier mensaje y lo enviaremos a OpenClaw por Telegram.\n"
        "Para recibir archivos usa lenguaje natural: entrégame el archivo X, envíame X, dame X, etc.\n"
        "Usa /salir para terminar el chat y cerrar la sesión del perfil."
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
        reply = await client.chat(
            workspace=workspace_name,
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            message=prompt,
            chat_id=chat_id,
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
    await deliver_marked_files(
        update,
        read_roots=read_roots,
        deny_roots=deny_roots,
        paths=paths,
        audit_path=_audit_path(settings),
        user_id=update.effective_user.id,
        workspace=workspace_name,
    )


async def forward_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if update.effective_user is None:
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

    client = _get_client(context)
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Enviame un mensaje de texto para pasarlo a OpenClaw.")
        return CHAT_ACTIVE

    context.user_data["chat_active"] = True
    file_query = parse_file_request(text)
    if file_query is not None:
        return await _handle_file_request(update, context, file_query)

    chat_id = update.effective_chat.id if update.effective_chat else update.effective_user.id
    try:
        reply = await client.chat(
            workspace=workspace_name,
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            message=text,
            chat_id=chat_id,
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Chat forwarding failed")
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
    if context.user_data.get(WORKSPACE_AUTH_KEY) and current:
        estado = f"Perfil autenticado: {settings.get_workspace(current).label}."
    else:
        estado = "Sin perfil autenticado (después de elegir con el botón debes escribir la contraseña)."
    await update.message.reply_text(
        f"{estado}\n\n"
        "Pulsa Administrador o Empleado y luego escribe la contraseña en el chat. "
        "El botón no basta para iniciar sesión.\n"
        "Cuando veas «Contraseña correcta», usa /chat.",
        reply_markup=_workspace_keyboard(settings),
    )


async def workspace_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    query = update.callback_query
    if query is None:
        return

    await query.answer(
        "Siguiente paso: escribe la contraseña del perfil en el chat.",
        show_alert=True,
    )
    settings = _get_settings(context)
    workspace_name = query.data.split(":")[-1]
    if workspace_name not in settings.workspaces:
        return
    await _begin_workspace_switch(update, context, workspace_name)


async def workspace_password_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return

    settings = _get_settings(context)
    pending = context.user_data.get(PENDING_WORKSPACE_KEY)
    if not isinstance(pending, str) or pending not in settings.workspaces:
        await update.message.reply_text("No hay un cambio de perfil pendiente. Usa /workspace.")
        return

    attempts = int(context.user_data.get(WORKSPACE_AUTH_ATTEMPTS_KEY, 0))
    if attempts >= MAX_WORKSPACE_PASSWORD_ATTEMPTS:
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
        remaining = MAX_WORKSPACE_PASSWORD_ATTEMPTS - attempts
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
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        suffix = "Primero elige un perfil con /workspace (se solicita contraseña)."
    else:
        settings = _get_settings(context)
        suffix = (
            f"Workspace activo: {settings.get_workspace(workspace_name).label}. "
            "Usa /salir para cerrar sesión del perfil."
        )
    await update.message.reply_text(
        "Usa /chat para hablar con OpenClaw o /recordatorios para gestionar tareas. "
        + suffix
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOGGER.exception("Unhandled Telegram error", exc_info=context.error)
