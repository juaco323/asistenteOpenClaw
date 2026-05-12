from __future__ import annotations

import asyncio
import logging
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
from app.openclaw.client import OpenClawClient, build_openclaw_client


LOGGER = logging.getLogger(__name__)

CHAT_ACTIVE: Final[int] = 1
REMINDER_MENU: Final[int] = 2
REMINDER_CREATE: Final[int] = 3

OPENCLAW_CLIENT_KEY = "openclaw_client"
SETTINGS_KEY = "settings"
SELECTED_WORKSPACE_KEY = "selected_workspace"


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
    # Comandos generales primero: si el ConversationHandler va delante, /start puede no
    # llegar al handler cuando el usuario no está en conversación (PTB 21).
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("workspace", workspace_command))
    application.add_handler(CommandHandler("estado", status_command))
    application.add_handler(CommandHandler("salir", exit_command))
    application.add_handler(
        CallbackQueryHandler(
            workspace_select_callback,
            pattern=r"^workspace:select:(admin|empleado)$",
        )
    )
    application.add_handler(_build_main_conversation())
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, default_text_message)
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
                BotCommand("recordatorios", "Lista o crea recordatorios"),
                BotCommand("workspace", "Cambia entre admin y empleado"),
                BotCommand("estado", "Revisa el estado de OpenClaw"),
                BotCommand("salir", "Sale del modo actual"),
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
    if isinstance(selected, str) and selected in settings.workspaces:
        return selected
    if settings.default_workspace and settings.default_workspace in settings.workspaces:
        context.user_data[SELECTED_WORKSPACE_KEY] = settings.default_workspace
        return settings.default_workspace
    if len(settings.workspaces) == 1:
        only_workspace = next(iter(settings.workspaces))
        context.user_data[SELECTED_WORKSPACE_KEY] = only_workspace
        return only_workspace
    return None


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
    context.user_data[SELECTED_WORKSPACE_KEY] = normalized
    return normalized


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
        "Usa /workspace para cambiar entre admin y empleado.\n"
        "Usa /chat para hablar con el agente remoto.\n"
        "Usa /recordatorios para revisar o crear tareas.\n"
        "Usa /estado para revisar conectividad.\n"
        "Usa /salir para salir del modo actual."
    )
    return ConversationHandler.END


async def enter_chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        f"Entraste en modo chat con {workspace.label}.\n"
        "Escribe cualquier mensaje y lo enviaremos a OpenClaw.\n"
        "Usa /salir cuando quieras terminar."
    )
    return CHAT_ACTIVE


async def forward_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message is None or not await _ensure_authorized(update, context):
        return ConversationHandler.END
    if update.effective_user is None:
        return CHAT_ACTIVE

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

    try:
        reply = await client.chat(
            workspace=workspace_name,
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            message=text,
        )
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Chat forwarding failed")
        await update.message.reply_text(f"No pude hablar con OpenClaw: {exc}")
        return CHAT_ACTIVE

    workspace = settings.get_workspace(workspace_name)
    await update.message.reply_text(f"[{workspace.label}]\n{reply}")
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
        await query.edit_message_text(f"No pude cargar los recordatorios: {exc}")
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
        await update.message.reply_text(f"No pude crear el recordatorio: {exc}")
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
    if update.message is not None:
        await update.message.reply_text("Sali del modo actual.")
    elif update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Sali del modo actual.")
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
        workspace_name = _apply_workspace_argument(context, context.args[0])
        if workspace_name is None:
            await update.message.reply_text("Workspace no valido. Usa /workspace admin o /workspace empleado.")
            return
        await update.message.reply_text(
            f"Workspace activo: {settings.get_workspace(workspace_name).label}."
        )
        return

    current = _resolve_workspace_from_context(context)
    current_label = settings.get_workspace(current).label if current else "sin seleccionar"
    await update.message.reply_text(
        f"Workspace actual: {current_label}.\nSelecciona otro si quieres cambiar:",
        reply_markup=_workspace_keyboard(settings),
    )


async def workspace_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_authorized(update, context):
        return
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    settings = _get_settings(context)
    workspace_name = query.data.split(":")[-1]
    context.user_data[SELECTED_WORKSPACE_KEY] = workspace_name
    await query.edit_message_text(
        f"Workspace activo: {settings.get_workspace(workspace_name).label}."
    )


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
            label = settings.get_workspace(workspace_name).label
            lines.append(f"- {label}: ERROR ({result})")
        else:
            lines.append(f"- {result}")
    await update.message.reply_text("\n".join(lines))


async def default_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or not await _ensure_authorized(update, context):
        return
    workspace_name = _resolve_workspace_from_context(context)
    if workspace_name is None:
        suffix = "Primero elige uno con /workspace."
    else:
        settings = _get_settings(context)
        suffix = f"Workspace activo: {settings.get_workspace(workspace_name).label}."
    await update.message.reply_text(
        "Usa /chat para hablar con OpenClaw o /recordatorios para gestionar tareas. "
        + suffix
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOGGER.exception("Unhandled Telegram error", exc_info=context.error)
