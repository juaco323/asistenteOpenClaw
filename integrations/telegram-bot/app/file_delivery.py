from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

LOGGER = logging.getLogger(__name__)

FILE_MARKER_RE = re.compile(r"\[\[TELEGRAM_FILE:([^\]]+)\]\]", re.IGNORECASE)
MAX_SEARCH_DEPTH = 6
MAX_FILE_BYTES = 49 * 1024 * 1024

FILE_REQUEST_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*get\s+[\"']?(.+?)[\"']?\s*$", re.IGNORECASE),
    re.compile(
        r"^\s*(?:env[ií]ame|m[aá]ndame|p[aá]same|entreg[aá]me|dame|comp[aá]rteme)\s+"
        r"(?:el\s+)?archivo\s+[\"']?(.+?)[\"']?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:env[ií]ame|m[aá]ndame|p[aá]same|entreg[aá]me|dame)\s+"
        r"[\"']?([^\s\"']+\.[A-Za-z0-9]{1,10})[\"']?\s*(?:por\s+telegram)?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:quiero|necesito|solicito)\s+"
        r"(?:(?:que\s+me\s+)?(?:env[ií]es|mandes|pases|entregues|compartas)\s+)?"
        r"(?:el\s+)?archivo\s+[\"']?(.+?)[\"']?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:me\s+puedes|podr[ií]as|puedes)\s+"
        r"(?:enviar|mandar|pasar|entregar|compartir)\s+"
        r"(?:el\s+)?archivo\s+[\"']?(.+?)[\"']?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:por\s+favor\s+)?(?:env[ií]ame|m[aá]ndame|entreg[aá]me)\s+"
        r"(?:el\s+)?archivo\s+llamado\s+[\"']?(.+?)[\"']?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:entreg[aá]me|env[ií]ame|m[aá]ndame|dame)\s+"
        r"(?:el\s+)?archivo\s+.+?\s+"
        r"(?:de|sobre|llamado)\s+[\"']?(.+?)[\"']?\s*"
        r"(?:por\s+(?:este\s+medio|telegram))?\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:entreg[aá]me|env[ií]ame|m[aá]ndame|dame)\s+"
        r"(?:el\s+)?archivo\s+[\"']?(.+?)[\"']?\s*"
        r"(?:por\s+(?:este\s+medio|telegram))?\s*$",
        re.IGNORECASE,
    ),
)


def parse_file_request(text: str) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None
    for pattern in FILE_REQUEST_PATTERNS:
        match = pattern.match(stripped)
        if match:
            candidate = match.group(1).strip().strip("\"'")
            if candidate:
                return candidate
    return None


def extract_file_markers(text: str) -> tuple[str, list[Path]]:
    paths: list[Path] = []
    for match in FILE_MARKER_RE.finditer(text):
        raw = match.group(1).strip().strip("\"'")
        if raw:
            paths.append(Path(raw))
    clean = FILE_MARKER_RE.sub("", text).strip()
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean, paths


def _fold_segment(name: str) -> str:
    """Compara nombres sin distinguir mayúsculas y con acentos opcionales debilitados."""
    if not name:
        return ""
    n = unicodedata.normalize("NFD", name)
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    return n.casefold()


def _segments_match(user_seg: str, actual_seg: str) -> bool:
    if user_seg.casefold() == actual_seg.casefold():
        return True
    return _fold_segment(user_seg) == _fold_segment(actual_seg)


def _posix_tail_parts(path: Path) -> tuple[str, ...]:
    try:
        p = path.expanduser()
        parts = p.resolve(strict=False).parts
    except OSError:
        parts = path.expanduser().parts
    if parts and parts[0] == "/":
        return tuple(parts[1:])
    return tuple(parts)


def _find_ci_child(entries: list[Path], wanted: str) -> Path | None:
    if not wanted or wanted in (".", ".."):
        return None
    cf = wanted.casefold()
    fold_w = _fold_segment(wanted)
    for e in entries:
        if e.name.casefold() == cf:
            return e
    for e in entries:
        if _fold_segment(e.name) == fold_w:
            return e
    return None


def resolve_under_root_ci(root: Path, parts: tuple[str, ...]) -> Path | None:
    """Recorre root siguiendo parts con coincidencia insensible a mayúsculas/acentos."""
    if not parts:
        return root if root.exists() else None
    try:
        current = root if root.is_dir() else None
    except OSError:
        return None
    if current is None:
        return None
    for part in parts:
        if not part or part in (".", ".."):
            return None
        try:
            entries = list(current.iterdir())
        except OSError:
            return None
        nxt = _find_ci_child(entries, part)
        if nxt is None:
            return None
        current = nxt
    return current


def _strip_redundant_prefix(
    candidate_parts: tuple[str, ...],
    root: Path,
) -> tuple[str, ...]:
    """Si el usuario repite el nombre del directorio raíz (p. ej. Documentos/...), quítalo."""
    if not candidate_parts:
        return candidate_parts
    try:
        root_name = root.resolve(strict=False).name
    except OSError:
        root_name = root.name
    if root_name and _segments_match(candidate_parts[0], root_name):
        return tuple(candidate_parts[1:])
    return candidate_parts


def resolve_absolute_user_path_ci(user_path: Path, read_roots: list[Path]) -> Path | None:
    """
    Si user_path es absoluta pero con distinta capitalización/acentos, resuelve bajo read_roots.
    """
    up = user_path.expanduser()
    user_parts = _posix_tail_parts(up)
    if not user_parts:
        return None
    for root in read_roots:
        try:
            if not root.exists():
                continue
        except OSError:
            continue
        root_parts = _posix_tail_parts(root.resolve(strict=False))
        if len(user_parts) < len(root_parts):
            continue
        if not all(
            _segments_match(u, r)
            for u, r in zip(user_parts[: len(root_parts)], root_parts, strict=True)
        ):
            continue
        remainder = tuple(user_parts[len(root_parts) :])
        found = resolve_under_root_ci(root, remainder)
        if found is not None and found.is_file():
            return found
    return None


def _first_file_matching_name_ci(
    root: Path,
    filename: str,
    read_roots: list[Path],
    deny: list[Path],
) -> Path | None:
    target_cf = filename.casefold()
    target_fold = _fold_segment(filename)
    try:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            try:
                if len(p.relative_to(root).parts) > MAX_SEARCH_DEPTH:
                    continue
            except ValueError:
                continue
            if not is_delivery_allowed(p, read_roots, deny):
                continue
            if p.name.casefold() == target_cf or _fold_segment(p.name) == target_fold:
                return p
    except OSError:
        LOGGER.warning("No se pudo rglob CI en %s", root)
    return None


def is_path_allowed(path: Path, roots: list[Path]) -> bool:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return False
    for root in roots:
        try:
            root_resolved = root.resolve(strict=False)
        except OSError:
            continue
        if resolved == root_resolved or root_resolved in resolved.parents:
            return True
    return False


def is_path_denied(path: Path, deny_roots: list[Path]) -> bool:
    if not deny_roots:
        return False
    return is_path_allowed(path, deny_roots)


def is_delivery_allowed(
    path: Path,
    read_roots: list[Path],
    deny_roots: list[Path],
) -> bool:
    if is_path_denied(path, deny_roots):
        return False
    return is_path_allowed(path, read_roots)


def find_file_by_name(
    name: str,
    read_roots: list[Path],
    *,
    deny_roots: list[Path] | None = None,
) -> Path | None:
    deny = deny_roots or []
    candidate = Path(name)
    if candidate.is_absolute():
        p = candidate.expanduser()
        if p.is_file() and is_delivery_allowed(p, read_roots, deny):
            return p
        alt = resolve_absolute_user_path_ci(p, read_roots)
        if alt is not None and is_delivery_allowed(alt, read_roots, deny):
            return alt
        return None

    basename = candidate.name
    if not basename:
        return None

    for root in read_roots:
        if not root.exists():
            continue
        rel_parts = _strip_redundant_prefix(tuple(candidate.parts), root)
        direct = root / basename
        if direct.is_file() and is_delivery_allowed(direct, read_roots, deny):
            return direct
        if candidate.parts:
            nested = root.joinpath(*candidate.parts)
            if nested.is_file() and is_delivery_allowed(nested, read_roots, deny):
                return nested
        ci_nested = resolve_under_root_ci(root, rel_parts)
        if ci_nested is not None and ci_nested.is_file() and is_delivery_allowed(
            ci_nested, read_roots, deny
        ):
            return ci_nested

    for root in read_roots:
        if not root.is_dir():
            continue
        try:
            for match in root.rglob(basename):
                if match.is_file() and is_delivery_allowed(match, read_roots, deny):
                    if len(match.relative_to(root).parts) <= MAX_SEARCH_DEPTH:
                        return match
        except OSError:
            LOGGER.warning("No se pudo buscar en %s", root)

    for root in read_roots:
        hit = _first_file_matching_name_ci(root, basename, read_roots, deny)
        if hit is not None:
            return hit

    if "." not in basename:
        target_fold = _fold_segment(basename)
        target_cf = basename.casefold()
        for root in read_roots:
            if not root.is_dir():
                continue
            try:
                for match in root.rglob("*"):
                    if not match.is_file() or not is_delivery_allowed(match, read_roots, deny):
                        continue
                    if len(match.relative_to(root).parts) > MAX_SEARCH_DEPTH:
                        continue
                    stem_cf = match.stem.casefold()
                    if (
                        stem_cf == target_cf
                        or _fold_segment(match.stem) == target_fold
                        or target_cf in stem_cf
                        or target_fold in _fold_segment(match.stem)
                    ):
                        return match
            except OSError:
                LOGGER.warning("No se pudo buscar en %s", root)
    return None


def resolve_delivery_path(
    path: Path,
    read_roots: list[Path],
    *,
    deny_roots: list[Path] | None = None,
) -> Path | None:
    deny = deny_roots or []
    expanded = path.expanduser()
    if expanded.is_absolute():
        if expanded.is_file() and is_delivery_allowed(expanded, read_roots, deny):
            return expanded
        alt = resolve_absolute_user_path_ci(expanded, read_roots)
        if alt is not None and is_delivery_allowed(alt, read_roots, deny):
            return alt
    else:
        found = find_file_by_name(str(expanded), read_roots, deny_roots=deny)
        if found is not None:
            return found
    if expanded.is_file() and is_delivery_allowed(expanded, read_roots, deny):
        return expanded
    found = find_file_by_name(expanded.name, read_roots, deny_roots=deny)
    if found is not None:
        return found
    return None


async def send_telegram_file(
    update: Update,
    path: Path,
    *,
    read_roots: list[Path],
    deny_roots: list[Path] | None = None,
    caption: str | None = None,
    audit_path: Path | None = None,
    user_id: int | None = None,
    workspace: str | None = None,
) -> bool:
    if update.message is None:
        return False
    deny = deny_roots or []
    resolved = resolve_delivery_path(path, read_roots, deny_roots=deny)
    if resolved is None:
        if path.is_file() and is_path_denied(path.expanduser(), deny):
            await update.message.reply_text(
                "Ese archivo está prohibido para este perfil."
            )
        elif path.is_file() and not is_path_allowed(path.expanduser(), read_roots):
            await update.message.reply_text(
                "Ese archivo está fuera de las rutas permitidas para este perfil."
            )
        else:
            await update.message.reply_text(f"No encontré el archivo: {path.name}")
        if audit_path is not None and user_id is not None and workspace is not None:
            from app.audit import append_file_audit

            append_file_audit(
                audit_path=audit_path,
                user_id=user_id,
                workspace=workspace,
                action="deliver",
                requested=str(path),
                resolved=None,
                allowed=False,
            )
        return False
    path = resolved
    try:
        size = path.stat().st_size
    except OSError:
        await update.message.reply_text(f"No pude leer el archivo: {path.name}")
        return False
    if size > MAX_FILE_BYTES:
        await update.message.reply_text(
            f"El archivo {path.name} supera el límite de Telegram ({MAX_FILE_BYTES // (1024 * 1024)} MB)."
        )
        return False

    try:
        with path.open("rb") as handle:
            await update.message.reply_document(document=handle, filename=path.name, caption=caption)
    except OSError as exc:
        LOGGER.exception("Error enviando archivo %s", path)
        await update.message.reply_text(f"No pude enviar {path.name}: {exc}")
        return False
    if audit_path is not None and user_id is not None and workspace is not None:
        from app.audit import append_file_audit

        append_file_audit(
            audit_path=audit_path,
            user_id=user_id,
            workspace=workspace,
            action="deliver",
            requested=str(path),
            resolved=str(path),
            allowed=True,
        )
    return True


async def deliver_marked_files(
    update: Update,
    *,
    read_roots: list[Path],
    deny_roots: list[Path] | None = None,
    paths: list[Path],
    audit_path: Path | None = None,
    user_id: int | None = None,
    workspace: str | None = None,
) -> int:
    sent = 0
    for path in paths:
        if await send_telegram_file(
            update,
            path,
            read_roots=read_roots,
            deny_roots=deny_roots,
            audit_path=audit_path,
            user_id=user_id,
            workspace=workspace,
        ):
            sent += 1
    return sent
