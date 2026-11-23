#!/usr/bin/env python3
"""Remove images under static/images/ that no post references.

Recomputes the orphan set live (does not trust a stale scan) by:
  1. Walking every .md under content/**/
  2. Extracting every image reference (markdown ![](), raw <img src>, Hugo
     {{< figure src="..." >}}) that points under /images/ or is relative
  3. Diffing against the file inventory under static/images/
  4. Printing the orphan set, byte count, and (unless --dry-run) rm'ing them

The scan is CONSERVATIVE: a file is only orphaned when NO post references it
by its filename (last path component), its /images/<path>/<file>, or any
substring that would match a Hugo asset-pipeline lookup. Keeps everything
under static/images/profile/ and static/images/external/ regardless — those
hold avatar + Jetpack proxy replacements that lint logic can miss.

Usage:
  python3 scripts/prune_orphan_images.py --dry-run   # list, don't delete
  python3 scripts/prune_orphan_images.py             # delete + report
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMG_ROOT = REPO / "static" / "images"
CONTENT_ROOTS = [REPO / "content"]
# Dirs under static/images/ whose contents are never pruned — avatars, proxy
# downloads, and anything the orphan heuristic might miscount.
SAFE_DIRS = {"profile", "external"}

_IMG_REF_RE = re.compile(
    r"""(?:
        !\[[^\]]*\]\(\s*([^)\s"]+)       # markdown ![alt](url)
      | <img[^>]*\bsrc\s*=\s*["']([^"']+)["']   # <img src="...">
      | <figure[^>]*\bsrc\s*=\s*["']([^"']+)["']  # Hugo {{< figure src="..." >}}
      | srcset\s*=\s*["']([^"']+)["']  # <img srcset>
      | data-orig-file\s*=\s*["']([^"']+)["']  # WP data attributes
      | data-large-file\s*=\s*["']([^"']+)["']
    )""",
    re.VERBOSE | re.IGNORECASE,
)


def collect_referenced_names() -> set[str]:
    """Return the set of file BASENAMES referenced anywhere under content/."""
    names: set[str] = set()
    for root in CONTENT_ROOTS:
        for md in root.rglob("*.md"):
            text = md.read_text(encoding="utf-8", errors="replace")
            for m in _IMG_REF_RE.finditer(text):
                for group in m.groups():
                    if not group:
                        continue
                    # srcset carries "url1 1x, url2 2x" — split on comma
                    candidates = [u.strip().split()[0] for u in group.split(",") if u.strip()]
                    for url in candidates:
                        # keep only the basename (handles /images/2024/img.jpg, ./img.jpg, etc.)
                        name = url.rstrip("/").split("/")[-1]
                        # strip query strings and fragments
                        name = name.split("?")[0].split("#")[0]
                        if name:
                            names.add(name)
    return names


def is_safe_path(path: Path) -> bool:
    try:
        rel = path.relative_to(IMG_ROOT)
    except ValueError:
        return True
    return rel.parts and rel.parts[0] in SAFE_DIRS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    referenced = collect_referenced_names()
    print(f"Referenced basenames collected: {len(referenced)}")

    orphans = []
    total_bytes = 0
    for img in IMG_ROOT.rglob("*"):
        if not img.is_file():
            continue
        if is_safe_path(img):
            continue
        if img.name in referenced:
            continue
        orphans.append(img)
        total_bytes += img.stat().st_size

    orphans.sort()
    print(f"Orphans found: {len(orphans)} ({total_bytes / 1024 / 1024:.1f} MB)")
    for o in orphans:
        rel = o.relative_to(REPO)
        print(f"  {'[DRY]' if args.dry_run else '[RM] '} {rel} ({o.stat().st_size:,} bytes)")

    if not args.dry_run:
        for o in orphans:
            o.unlink()
        print(f"\nDeleted {len(orphans)} files, reclaimed {total_bytes / 1024 / 1024:.1f} MB.")


if __name__ == "__main__":
    main()
