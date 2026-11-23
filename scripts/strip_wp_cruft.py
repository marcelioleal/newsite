#!/usr/bin/env python3
"""Strip WordPress / Jetpack legacy attributes and classes from migrated posts.

Targets non-functional cruft that makes HTML noisier, heavier, and harder to
read, with zero visual effect in Hugo. All removals are idempotent.

Removed:

1. `srcset="..."` and `sizes="..."` on <img> — they reference Jetpack's
   `?resize=NxM&ssl=1` endpoints that Hugo does not implement, so the browser
   just downloads the full file no matter which candidate it picks. Removing
   them makes the browser use `src` directly (same bytes, cleaner HTML).

2. WordPress / Jetpack data-* attributes with no runtime consumer:
   data-attachment-id, data-permalink, data-orig-file, data-orig-size,
   data-comments-opened, data-image-meta, data-image-title,
   data-image-description, data-image-caption, data-large-file,
   data-medium-file, data-recalc-dims, data-lazy-src.

3. `class="wp-image-NNNN"` identifiers and the bare `class="wp-image-NNNN ..."`
   when part of a longer class list — the attribute class remains but drops
   the wp-image token. Also drops `wp-caption` and `wp-block-image` classes.

Keeps:
- `src`, `alt`, `width`, `height`, `loading`, `decoding`, `style` — all
  functional in Hugo.
- Any class the theme or custom.css relies on.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

# WordPress / Jetpack data-* attributes that do nothing in Hugo.
_WP_DATA_ATTRS = [
    "data-attachment-id",
    "data-permalink",
    "data-orig-file",
    "data-orig-size",
    "data-comments-opened",
    "data-image-meta",
    "data-image-title",
    "data-image-description",
    "data-image-caption",
    "data-large-file",
    "data-medium-file",
    "data-recalc-dims",
    "data-lazy-src",
]
_DATA_RE = re.compile(
    r"""\s+(?:""" + "|".join(_WP_DATA_ATTRS) + r""")\s*=\s*["'][^"']*["']""",
    re.IGNORECASE,
)

# srcset and sizes on <img> (and any element) — removed because the Jetpack
# resize URLs they reference are not implemented in Hugo.
_SRCSET_RE = re.compile(r'\s+srcset\s*=\s*"[^"]*"', re.IGNORECASE)
_SIZES_RE = re.compile(r'\s+sizes\s*=\s*"[^"]*"', re.IGNORECASE)

# wp-image-NNNN, wp-caption, wp-block-image classes inside a class="..." list.
_WP_CLASS_TOKEN_RE = re.compile(
    r"""\bclass\s*=\s*(?P<q>["'])(?P<body>[^"']*)(?P=q)""",
    re.IGNORECASE,
)
_WP_CLASS_FRAGMENTS = re.compile(r"\bwp-image-\d+\b|\bwp-caption\b|\bwp-block-image\b", re.IGNORECASE)


def strip_class_tokens(match: re.Match) -> str:
    quote = match.group("q")
    classes = _WP_CLASS_FRAGMENTS.sub("", match.group("body"))
    classes = re.sub(r"\s+", " ", classes).strip()
    if not classes:
        return ""  # drop the whole class="" attribute
    return f'class={quote}{classes}{quote}'


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    text = _DATA_RE.sub("", text)
    text = _SRCSET_RE.sub("", text)
    text = _SIZES_RE.sub("", text)
    text = _WP_CLASS_TOKEN_RE.sub(strip_class_tokens, text)
    # tidy up: collapse runs of whitespace that we may have introduced inside tags
    text = re.sub(r"(\<\w+[^>]*?)\s{2,}([^>]*\>)", r"\1 \2", text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def main() -> None:
    total = 0
    for root in POST_DIRS:
        for md in root.rglob("*.md"):
            if process_file(md):
                total += 1
                print(f"cleaned {md.relative_to(REPO)}")
    print(f"\nTotal: {total} files cleaned.")


if __name__ == "__main__":
    main()
