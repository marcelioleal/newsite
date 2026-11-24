#!/usr/bin/env python3
"""Apply the vague-anchor-text replacements described by review_vague_links.py.

Re-scans posts and for each finding:

  - If the URL points at a verified-dead host (rapidshare, 2.download-1,
    files-upload, imageshack, antoniofonseca.files.wordpress.com) → leaves
    the anchor as-is and prints a WARN so the owner knows to clean it up
    with the dead-link pass.

  - If the URL points at marcelioleal.com (the user's OWN legacy WP blog)
    → leaves the anchor as-is and prints an INTERNAL warning so the owner
    can convert it to a relative Hugo path manually (we don't know the
    new slug yet in every case).

  - Otherwise → rewrites the anchor text to the host-aware suggestion from
    the review helper. In markdown form: `[old](url)` → `[suggestion](url)`.
    In HTML form: `<a href="url">old</a>` → `<a href="url">suggestion</a>`.

Idempotent: once applied, subsequent runs find no vague anchors to replace.
"""
from __future__ import annotations

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_vague_links import (  # noqa: E402
    POST_DIRS,
    VAGUE_TEXTS_RE,
    _MD_ANCHOR_RE,
    _HTML_ANCHOR_RE,
    suggest_replacement,
)

DEAD_HOST_SUBSTRINGS = (
    "rapidshare.com",
    "2.download-1.files-upload.com",
    "files-upload.com",
    "imageshack.us",
    "antoniofonseca.files.wordpress.com",
    "taroba.fm.br",
)
INTERNAL_HOSTS = ("marcelioleal.com",)


def is_dead_host(url: str) -> bool:
    return any(fragment in url for fragment in DEAD_HOST_SUBSTRINGS)


def is_internal_host(url: str) -> bool:
    return any(fragment in url for fragment in INTERNAL_HOSTS)


def process_file(path: Path, lang_pt: bool) -> tuple[int, list[str]]:
    text = path.read_text(encoding="utf-8")
    original = text
    warnings: list[str] = []
    applied = 0

    def md_sub(match: re.Match) -> str:
        nonlocal applied
        anchor_text, url = match.group(1), match.group(2)
        if not VAGUE_TEXTS_RE.fullmatch(anchor_text.strip()):
            return match.group(0)
        if is_dead_host(url):
            warnings.append(f"  DEAD  {path}: `[{anchor_text}]({url})` — leaving as-is")
            return match.group(0)
        if is_internal_host(url):
            warnings.append(f"  INTRN {path}: `[{anchor_text}]({url})` — convert to Hugo relative manually")
            return match.group(0)
        suggestion = suggest_replacement(url, lang_pt)
        applied += 1
        return f"[{suggestion}]({url})"

    def html_sub(match: re.Match) -> str:
        nonlocal applied
        url = match.group("url")
        anchor_text = match.group("text").strip()
        if not VAGUE_TEXTS_RE.fullmatch(anchor_text):
            return match.group(0)
        if is_dead_host(url):
            warnings.append(f"  DEAD  {path}: `<a href=\"{url}\">{anchor_text}</a>` — leaving as-is")
            return match.group(0)
        if is_internal_host(url):
            warnings.append(f"  INTRN {path}: `<a href=\"{url}\">{anchor_text}</a>` — convert to Hugo relative manually")
            return match.group(0)
        suggestion = suggest_replacement(url, lang_pt)
        applied += 1
        prefix = match.group(0).split(">", 1)[0] + ">"
        return f"{prefix}{suggestion}</a>"

    text = _MD_ANCHOR_RE.sub(md_sub, text)
    text = _HTML_ANCHOR_RE.sub(html_sub, text)

    if text != original:
        path.write_text(text, encoding="utf-8")

    return applied, warnings


def main() -> int:
    total_applied = 0
    all_warnings: list[str] = []
    for root in POST_DIRS:
        lang_pt = "pt-br" in str(root)
        for md in root.rglob("*.md"):
            applied, warnings = process_file(md, lang_pt)
            if applied:
                print(f"{md.relative_to(root.parent.parent.parent)}: +{applied}")
                total_applied += applied
            all_warnings.extend(warnings)

    print()
    print(f"Replacements applied: {total_applied}")
    if all_warnings:
        print(f"Warnings: {len(all_warnings)} findings left untouched —")
        for w in all_warnings:
            print(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
