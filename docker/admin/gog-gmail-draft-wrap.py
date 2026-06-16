#!/usr/bin/env python3
"""Normaliza --body de gog gmail drafts create (\\n literales, prefijo $)."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile


def normalize_body(text: str) -> str:
    if text.startswith("$"):
        text = text[1:]
    return (
        text.replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
    )


def body_to_tempfile(text: str) -> str:
    fd, path = tempfile.mkstemp(prefix="gog-body-", suffix=".txt")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(normalize_body(text))
    return path


def rewrite_draft_create_argv(argv: list[str]) -> tuple[list[str], list[str]]:
    if len(argv) < 3 or argv[0:3] != ["gmail", "drafts", "create"]:
        return argv, []

    rest = argv[3:]
    out = ["gmail", "drafts", "create"]
    temps: list[str] = []
    i = 0
    while i < len(rest):
        flag = rest[i]
        if flag == "--body" and i + 1 < len(rest):
            temps.append(body_to_tempfile(rest[i + 1]))
            out.extend(["--body-file", temps[-1]])
            i += 2
            continue
        if flag == "--body-file" and i + 1 < len(rest):
            src = rest[i + 1]
            if src == "-":
                raw = sys.stdin.read()
            else:
                with open(src, encoding="utf-8") as f:
                    raw = f.read()
            temps.append(body_to_tempfile(raw))
            out.extend(["--body-file", temps[-1]])
            i += 2
            continue
        out.append(flag)
        i += 1
    return out, temps


def main() -> None:
    argv = sys.argv[1:]
    new_argv, temps = rewrite_draft_create_argv(argv)
    try:
        raise SystemExit(
            subprocess.call(["/usr/local/bin/gog.real", *new_argv])
        )
    finally:
        for path in temps:
            try:
                os.unlink(path)
            except OSError:
                pass


if __name__ == "__main__":
    main()
