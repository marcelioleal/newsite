#!/usr/bin/env python3
"""Add rel="noopener noreferrer" to <a target="_blank"> tags in migrated posts.

Scope: every .md under content/pt-br/posts/ and content/en/posts/.
Rule: if an anchor already has target="_blank" but no rel=, add it.
      If rel= exists but is missing "noopener", append it.
Idempotent: safe to re-run.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

# Match <a ... target="_blank" ...> and optionally existing rel="..."
# Group 1 = anchor opening up to target="_blank"
# We rebuild the tag with rel merged.
_ANCHOR_RE = re.compile(
    r"<a\b([^>]*\btarget\s*=\s*[\"']_blank[\"'][^>]*)>",
    re.IGNORECASE,
)
_REL_RE = re.compile(r"\brel\s*=\s*[\"']([^\"']*)[\"']", re.IGNORECASE)

REQUIRED = {"noopener", "noreferrer"}


def patch_anchor(match: re.Match) -> str:
    attrs = match.group(1)
    rel_match = _REL_RE.search(attrs)
    if rel_match:
        current = {v.strip() for v in rel_match.group(1).split() if v.strip()}
        if REQUIRED.issubset(current):
            return match.group(0)  # already good
        merged = current | REQUIRED
        new_rel = f'rel="{" ".join(sorted(merged))}"'
        new_attrs = attrs[: rel_match.start()] + new_rel + attrs[rel_match.end() :]
    else:
        new_attrs = attrs.rstrip() + ' rel="noopener noreferrer"'
    return f"<a{new_attrs}>"


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = _ANCHOR_RE.subn(patch_anchor, text)
    if n and new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return n
    return 0


def main() -> None:
    total_files = 0
    total_patches = 0
    for root in POST_DIRS:
        for md in root.rglob("*.md"):
            n = process_file(md)
            if n:
                total_files += 1
                total_patches += n
                print(f"{md.relative_to(REPO)}: +{n}")
    print(f"\nTotal: {total_patches} anchors patched across {total_files} files.")


if __name__ == "__main__":
    main()
