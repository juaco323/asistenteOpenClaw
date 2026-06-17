#!/usr/bin/env python3
"""Extrae el contenido de un .docx y lo escribe como archivo .env (solo texto plano)."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def extract_docx_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    parts: list[str] = []
    for node in root.iter():
        if node.tag.endswith("}t") and node.text:
            parts.append(node.text)
        elif node.tag.endswith("}tab"):
            parts.append("\t")
        elif node.tag.endswith("}br") or node.tag.endswith("}cr"):
            parts.append("\n")
    text = "".join(parts)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} <entrada.docx> <salida.env>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    if not src.is_file():
        print(f"No existe: {src}", file=sys.stderr)
        return 1
    content = extract_docx_text(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    print(f"Escrito {dst} ({len(content)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
