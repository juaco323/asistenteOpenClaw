from __future__ import annotations

import re
import time
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from app.file_delivery import MAX_FILE_BYTES, is_path_allowed, is_path_denied

INCOMING_DIRNAME = "telegram-openclaw-incoming"


def resolve_incoming_dir(host_home: Path) -> Path:
    """Directorio donde se guardan archivos y fotos enviados por Telegram."""
    return (host_home / "Documentos" / INCOMING_DIRNAME).resolve()


def is_dir_write_allowed(
    dir_path: Path,
    write_roots: list[Path],
    deny_roots: list[Path],
) -> bool:
    try:
        resolved = dir_path.resolve(strict=False)
    except OSError:
        return False
    if is_path_denied(resolved, deny_roots):
        return False
    return is_path_allowed(resolved, write_roots)


def sanitize_upload_filename(file_name: str | None, file_id: str) -> str:
    if file_name:
        raw = Path(file_name).name.strip()
    else:
        raw = ""
    raw = raw.replace("\x00", "")
    raw = re.sub(r'[\n\r\\<>:"|?*]', "", raw)
    if not raw or raw in {".", ".."}:
        tail = "".join(c for c in file_id if c.isalnum())[:20] or "archivo"
        raw = f"telegram_{tail}.bin"
    if len(raw) > 180:
        stem, dot, suf = raw.rpartition(".")
        if dot and len(stem) > 8:
            raw = f"{stem[:140]}.{suf[:30]}"
        else:
            raw = raw[:180]
    return raw


def build_unique_destination(incoming_dir: Path, user_id: int, safe_name: str) -> Path:
    base_ms = int(time.time() * 1000)
    candidate = incoming_dir / f"{base_ms}_{user_id}_{safe_name}"
    if not candidate.exists():
        return candidate
    for n in range(1, 1000):
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix or ""
        alt = incoming_dir / f"{base_ms}_{user_id}_{stem}_{n}{suffix}"
        if not alt.exists():
            return alt
    return incoming_dir / f"{base_ms}_{user_id}_{safe_name}_{base_ms}"


def _check_size_limit(file_size: int | None) -> None:
    if file_size is not None and file_size > MAX_FILE_BYTES:
        mb = MAX_FILE_BYTES // (1024 * 1024)
        raise ValueError(
            f"El archivo supera el límite ({mb} MB). Reduce el tamaño o comprímelo."
        )


async def save_telegram_upload(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    host_home: Path,
    write_roots: list[Path],
    deny_roots: list[Path],
    user_id: int,
) -> Path:
    msg = update.message
    if msg is None:
        raise ValueError("Mensaje no disponible.")

    incoming_dir = resolve_incoming_dir(host_home)
    if not is_dir_write_allowed(incoming_dir, write_roots, deny_roots):
        raise PermissionError(
            "Esta política de perfil no permite guardar archivos entrantes. "
            "Revisa write_roots o TELEGRAM_*_WRITE_ROOTS."
        )
    incoming_dir.mkdir(parents=True, exist_ok=True)

    if msg.document:
        doc = msg.document
        _check_size_limit(doc.file_size)
        safe = sanitize_upload_filename(doc.file_name, doc.file_id)
        tg_file = await context.bot.get_file(doc.file_id)
    elif msg.photo:
        photo = msg.photo[-1]
        _check_size_limit(photo.file_size)
        safe = f"foto_{photo.file_unique_id}.jpg"
        tg_file = await context.bot.get_file(photo.file_id)
    else:
        raise ValueError("Tipo de mensaje no soportado (usa documento o foto).")

    dest = build_unique_destination(incoming_dir, user_id, safe)
    await tg_file.download_to_drive(custom_path=str(dest))
    try:
        got = dest.stat().st_size
    except OSError as exc:
        raise RuntimeError(f"No se pudo leer el archivo descargado: {exc}") from exc
    if got > MAX_FILE_BYTES:
        dest.unlink(missing_ok=True)
        raise ValueError(
            f"Tras descargar, el archivo supera el límite ({MAX_FILE_BYTES // (1024 * 1024)} MB)."
        )

    return dest


def build_user_message_for_incoming(
    *,
    saved_path: Path,
    caption: str | None,
) -> str:
    cap = (caption or "").strip()
    path_str = str(saved_path.resolve())
    intro = (
        "[Archivo recibido por Telegram]\n"
        f"Ruta absoluta en el equipo (úsame con `gog gmail drafts create` y `--attach`): "
        f"{path_str}\n"
        f"Nombre: {saved_path.name}\n\n"
    )
    if cap:
        return intro + f"Instrucción / pie del mensaje del usuario:\n{cap}"
    return (
        intro
        + "El usuario no escribió pie de foto ni texto junto al archivo. "
        "Si vas a enviar correo con este adjunto, pide destinatario y asunto si faltan."
    )
