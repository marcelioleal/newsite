#!/usr/bin/env python3
"""Remove <img> tags and markdown images pointing at verified-dead external hosts.

Dead hosts (verified 2026-11-23 via curl -I):
  - *.imageshack.us          → 404
  - antoniofonseca.files.wordpress.com → 410 Gone
  - taroba.fm.br             → connect failure

Behaviour:
  - For each dead host, remove any <img ... src="...<host>..."> tag (self-closing
    or paired). Removes the enclosing <a> wrapper if the anchor's only child is
    the img. Leaves surrounding text alone.
  - For markdown images `![alt](http://dead-host/...)`, drop the whole expression.
  - Reports counts.

Irreversible but recoverable via git; the <img>s are dead anyway.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

DEAD_HOSTS = [
    r"img\d+\.imageshack\.us",
    r"antoniofonseca\.files\.wordpress\.com",
    r"taroba\.fm\.br",
]
HOST_ALT = "|".join(DEAD_HOSTS)

# <img ... src="http(s)://<dead-host>...">  (void element)
_IMG_RE = re.compile(
    rf'<img\b[^>]*\bsrc\s*=\s*["\']https?://(?:{HOST_ALT})[^"\']*["\'][^>]*/?>',
    re.IGNORECASE,
)

# <a ...><img...></a>  — if the anchor wraps only an img we just removed, drop the anchor too.
_ANCHOR_WRAPS_REMOVED = re.compile(r"<a\b[^>]*>\s*</a>", re.IGNORECASE)

# markdown ![alt](http://<dead>/...)
_MD_IMG_RE = re.compile(
    rf"!\[[^\]]*\]\(\s*https?://(?:{HOST_ALT})[^)\s]*\s*\)",
    re.IGNORECASE,
)


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    text, n_img = _IMG_RE.subn("", text)
    text, n_md = _MD_IMG_RE.subn("", text)
    text, n_a = _ANCHOR_WRAPS_REMOVED.subn("", text)
    if text != original:
        path.write_text(text, encoding="utf-8")
    return n_img + n_md + n_a


def main() -> None:
    total = 0
    for root in POST_DIRS:
        for md in root.rglob("*.md"):
            n = process_file(md)
            if n:
                total += n
                print(f"{md.relative_to(REPO)}: {n} dead refs removed")
    print(f"\nTotal: {total} dead-external-image tags/links removed.")


if __name__ == "__main__":
    main()
