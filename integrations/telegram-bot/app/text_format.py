"""Limpieza de Markdown para Telegram.

El bot envía mensajes en texto plano (sin ``parse_mode``): cualquier ``**negrita**``,
``## título`` o `` `código` `` que produzca el gateway (los protocolos de skills están
escritos en Markdown, pensado para el Control UI) llega tal cual al chat y se ve como
asteriscos/almohadillas literales. Esta función normaliza ese texto para Telegram antes
de enviarlo, sin tocar el contenido en sí.
"""

from __future__ import annotations

import re

_CODE_FENCE_RE = re.compile(r"```(?:[^\n`]*\n)?(.*?)```", re.DOTALL)
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_HEADING_RE = re.compile(r"^#{1,6}[ \t]*", re.MULTILINE)
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def sanitize_markdown_for_telegram(text: str) -> str:
    if not text:
        return text
    cleaned = _CODE_FENCE_RE.sub(lambda m: m.group(1).strip("\n"), text)
    cleaned = _BOLD_RE.sub(r"\1", cleaned)
    cleaned = _INLINE_CODE_RE.sub(r"\1", cleaned)
    cleaned = _HEADING_RE.sub("", cleaned)
    cleaned = _BLANK_LINES_RE.sub("\n\n", cleaned)
    return cleaned.strip()
