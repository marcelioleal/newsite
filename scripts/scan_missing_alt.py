#!/usr/bin/env python3
"""Find <img> tags in posts that have no alt or alt="".

For each hit, print: file + line + URL + surrounding context.

Separate decorative-looking images (very small, icons, tracking pixels) from
content images (jpg/png/gif with real content).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

# <img src="..." ...> — may or may not have alt
_IMG_TAG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
_SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_ALT_RE = re.compile(r'\balt\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
# Markdown ![alt](url)
_MD_IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)\)')

# Skip these — decorative/UI only, not content
SKIP_URL_SUBSTRINGS = (
    "pixel.wp.com",
    "/wp-smilies/",
    "wp-emoji",
    "spacer.gif",
    "blank.gif",
    "clear.gif",
)


def should_skip(url: str) -> bool:
    return any(s in url for s in SKIP_URL_SUBSTRINGS)


def main():
    findings = []
    for root in POST_DIRS:
        lang = "pt" if "pt-br" in str(root) else "en"
        for md in root.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            lines = text.split("\n")
            for i, line in enumerate(lines, 1):
                for match in _IMG_TAG_RE.finditer(line):
                    attrs = match.group(1)
                    src_m = _SRC_RE.search(attrs)
                    alt_m = _ALT_RE.search(attrs)
                    if not src_m:
                        continue
                    src = src_m.group(1)
                    if should_skip(src):
                        continue
                    alt = alt_m.group(1) if alt_m else None
                    if alt is None or alt.strip() == "":
                        findings.append({
                            "file": str(md.relative_to(REPO)),
                            "line": i,
                            "src": src,
                            "alt_present": alt_m is not None,
                            "alt_value": alt,
                            "flavour": "html",
                            "lang": lang,
                        })
                for match in _MD_IMG_RE.finditer(line):
                    alt, src = match.group(1), match.group(2)
                    if should_skip(src):
                        continue
                    if not alt.strip():
                        findings.append({
                            "file": str(md.relative_to(REPO)),
                            "line": i,
                            "src": src,
                            "alt_present": True,
                            "alt_value": alt,
                            "flavour": "markdown",
                            "lang": lang,
                        })

    print(f"Total findings: {len(findings)}")
    by_file = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)
    print(f"Files affected: {len(by_file)}")
    print()
    print("By host of src URL:")
    hosts = {}
    for f in findings:
        host = urlparse(f["src"]).hostname or "LOCAL"
        hosts[host] = hosts.get(host, 0) + 1
    for host, n in sorted(hosts.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {host}")

    # Dump to JSON for the alt-text generator to consume
    out = REPO / "scripts" / "missing-alt.json"
    out.write_text(json.dumps(findings, indent=2, ensure_ascii=False))
    print(f"\nWrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
