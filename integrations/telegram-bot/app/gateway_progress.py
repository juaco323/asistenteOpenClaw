from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from telegram import Update
from telegram.constants import ChatAction

LOGGER = logging.getLogger(__name__)
T = TypeVar("T")


async def run_with_telegram_progress(
    update: Update,
    *,
    label: str,
    coro_factory: Callable[[], Awaitable[T]],
) -> T:
    """Muestra «escribiendo…» y un aviso breve mientras el gateway/OpenClaw responde."""
    message = update.message
    if message is None:
        return await coro_factory()

    chat = message.chat
    progress_msg = None
    typing_task: asyncio.Task[None] | None = None

    async def _typing_loop() -> None:
        try:
            while True:
                await chat.send_action(ChatAction.TYPING)
                await asyncio.sleep(4.5)
        except asyncio.CancelledError:
            return
        except Exception as exc:  # pragma: no cover
            LOGGER.debug("typing loop stopped: %s", exc)

    try:
        progress_msg = await message.reply_text(label)
        typing_task = asyncio.create_task(_typing_loop())
        return await coro_factory()
    finally:
        if typing_task is not None:
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
        if progress_msg is not None:
            try:
                await progress_msg.delete()
            except Exception:
                pass
