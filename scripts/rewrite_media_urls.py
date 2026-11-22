#!/usr/bin/env python3
"""
rewrite_media_urls.py — post-migration URL rewrite pass.

Rewrites WordPress media URLs in migrated Markdown to local static paths:
    https://marcelioleal.com/wp-content/uploads/YYYY/MM/<file>  →  /images/YYYY/MM/<file>
    https://i[0-9]+.wp.com/marcelioleal.com/wp-content/uploads/YYYY/MM/<file>?...  →  /images/YYYY/MM/<file>
    https://videos.files.wordpress.com/<token>/<file>.(mp4|mov)  →  /videos/<file>.$1
    *.heic (image src/href)  →  *.jpg (heif-convert output)

Idempotent: safe to run multiple times. Pass --dry-run to preview without touching disk.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Match https?://marcelioleal.com/wp-content/uploads/YYYY/MM/<file>[?...] as well as
# https?://i0.wp.com/marcelioleal.com/wp-content/uploads/YYYY/MM/<file>?... (Jetpack CDN).
_WP_UPLOAD = re.compile(
    r"https?://(?:i\d+\.wp\.com/)?marcelioleal\.com/wp-content/uploads/(\d{4})/(\d{2})/([^?#\s\"'<>)]+)"
)
# VideoPress MP4/MOV
_VIDEOPRESS = re.compile(r"https?://videos\.files\.wordpress\.com/[A-Za-z0-9]+/([^?#\s\"'<>)]+\.(?:mp4|mov))")
# Any lingering .heic inside a src="..."/href="..." attribute or Markdown ![](...).
_HEIC_SUFFIX = re.compile(r"(\.heic)(?=[\s\"'?)#]|$)", re.IGNORECASE)


def rewrite(text: str) -> tuple[str, int]:
    changes = 0

    def _wp(m: re.Match[str]) -> str:
        nonlocal changes
        changes += 1
        return f"/images/{m.group(1)}/{m.group(2)}/{m.group(3)}"

    def _vid(m: re.Match[str]) -> str:
        nonlocal changes
        changes += 1
        return f"/videos/{m.group(1)}"

    def _heic(_: re.Match[str]) -> str:
        nonlocal changes
        changes += 1
        return ".jpg"

    text = _WP_UPLOAD.sub(_wp, text)
    text = _VIDEOPRESS.sub(_vid, text)
    text = _HEIC_SUFFIX.sub(_heic, text)
    return text, changes


def iter_markdown_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for base in ("content/pt-br", "content/en"):
        root = REPO_ROOT / base
        if not root.exists():
            continue
        out.extend(root.rglob("*.md"))
    return sorted(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rewrite WP media URLs in migrated Markdown")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without touching disk")
    args = parser.parse_args()

    files = iter_markdown_files()
    changed = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        rewritten, count = rewrite(original)
        if count == 0 or rewritten == original:
            continue
        changed += 1
        if args.dry_run:
            print(f"would change {count} URL(s) in {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        else:
            path.write_text(rewritten, encoding="utf-8")
            print(f"changed {count} URL(s) in {path.relative_to(REPO_ROOT)}", file=sys.stderr)

    verb = "would change" if args.dry_run else "changed"
    if changed == 0:
        print("no changes needed", file=sys.stderr)
    else:
        print(f"done — {verb} {changed} files of {len(files)} scanned", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
