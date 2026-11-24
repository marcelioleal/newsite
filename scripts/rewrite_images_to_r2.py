#!/usr/bin/env python3
"""Rewrite /images/ references to the R2 CDN public URL.

After images were uploaded to Cloudflare R2 via migrate_images_to_r2.sh, this
script rewrites every reference in content/** and layouts/** so the browser
loads them from the CDN instead of from the Hugo static/ serving path.

Target patterns (URL prefix only):
  "/images/<path>"   →   "<R2_PUBLIC_URL>/<path>"
  '/images/<path>'   →   same
  (/images/<path>)   →   same     # markdown ![](...)
  =/images/<path>    →   same     # bare attr (rare)
  >/images/<path>    →   same     # text node (rare)

Does NOT touch:
  - "http://example.com/images/..." (external, prefixed with host)
  - "foo/images/bar" (not a URL path, mid-string)

Env var required:
  R2_PUBLIC_URL     — e.g. https://pub-51dee957ac3e4a038150048d60e57b9c.r2.dev

Usage:
  python3 scripts/rewrite_images_to_r2.py --dry-run   # count only
  python3 scripts/rewrite_images_to_r2.py             # rewrite in place
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET_DIRS = [REPO / "content", REPO / "layouts", REPO / "i18n"]
TARGET_EXTS = {".md", ".html", ".yaml", ".yml"}

# Lookbehind for a URL-start boundary: quote, paren, equals, open-angle-bracket,
# or whitespace. Avoids matching foo/images/bar mid-identifier.
URL_RE = re.compile(r'(?<=[="\'(\s>])/images/')


def process_file(path: Path, cdn_base: str, dry_run: bool) -> int:
    text = path.read_text(encoding="utf-8")
    replacements = URL_RE.findall(text)
    if not replacements:
        return 0
    if not dry_run:
        new_text = URL_RE.sub(f"{cdn_base}/", text)
        path.write_text(new_text, encoding="utf-8")
    return len(replacements)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cdn = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")
    if not cdn:
        print("ERROR: R2_PUBLIC_URL env var is empty", file=sys.stderr)
        return 1

    print(f"CDN base: {cdn}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'REWRITE'}")
    print()

    total_files = 0
    total_refs = 0
    for root in TARGET_DIRS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in TARGET_EXTS:
                continue
            n = process_file(path, cdn, args.dry_run)
            if n:
                total_files += 1
                total_refs += n
                print(f"{path.relative_to(REPO)}: {n} refs")

    print()
    print(f"Total: {total_refs} references in {total_files} files"
          f" ({'would be' if args.dry_run else 'were'} rewritten)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
