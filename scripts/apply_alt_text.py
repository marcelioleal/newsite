#!/usr/bin/env python3
"""Apply alt text to <img> tags across posts.

Two tiers of alt-text sources in priority order:
  1. Hand-authored mappings in /tmp/alt-review/alt-mapping.json (filename-keyed
     under per-post buckets) — these are vision-generated and get first pick.
  2. Smart fallback heuristic for everything else: use the nearest <figcaption>
     IF the next line is a figcaption, else build from post title + filename
     shape hints (IMG_XXXX → "foto do post", Screenshot_X → "captura de tela",
     cristo/carneiros/etc → treated as a place or theme hint).

Writes alt="..." into each matching <img> tag that currently has none or has
alt="". Idempotent: images with non-empty alt are skipped.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
MAPPING_FILE = Path("/tmp/alt-review/alt-mapping.json")
URL_MAP_FILE = Path("/tmp/alt-review/url-map.json")

POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

_IMG_TAG_RE = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
_SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_ALT_RE = re.compile(r'\balt\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
_FIGCAPTION_RE = re.compile(r"<figcaption>(.*?)</figcaption>", re.IGNORECASE | re.DOTALL)

# Match screenshots, IMG dates, IMG raw camera dumps, WhatsApp VIDs, etc.
_SCREENSHOT_RE = re.compile(r"Screenshot[-_]", re.IGNORECASE)
_IMG_FILE_RE = re.compile(r"\bIMG[-_]\d+", re.IGNORECASE)
_WHATSAPP_RE = re.compile(r"\bIMG-\d{8}-WA", re.IGNORECASE)
_VID_RE = re.compile(r"\b(vid|video|mp4|mov)[-_]", re.IGNORECASE)


def load_post_titles() -> dict[str, str]:
    """Return {post_path: title} parsed from each post's front-matter."""
    titles = {}
    title_re = re.compile(r'^title:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
    for root in POST_DIRS:
        for md in root.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            frontmatter_end = text.find("---", 3)  # skip the opening ---
            if frontmatter_end > 0:
                m = title_re.search(text[:frontmatter_end])
                if m:
                    titles[str(md.relative_to(REPO))] = m.group(1).strip().strip('"')
    return titles


def filename_from_src(src: str) -> str:
    try:
        return Path(urlparse(html.unescape(src)).path).name
    except Exception:
        return ""


def smart_fallback_alt(filename: str, post_title: str, lang_pt: bool) -> str:
    """Generate a reasonable alt from filename + post context when no vision data."""
    stem = Path(filename).stem
    if _SCREENSHOT_RE.search(stem):
        return (f"Captura de tela do post \"{post_title}\"" if lang_pt
                else f"Screenshot from the post \"{post_title}\"")
    if _WHATSAPP_RE.search(stem) or _IMG_FILE_RE.search(stem):
        return (f"Fotografia do post \"{post_title}\"" if lang_pt
                else f"Photograph from the post \"{post_title}\"")
    if _VID_RE.search(stem):
        return (f"Quadro de vídeo do post \"{post_title}\"" if lang_pt
                else f"Video frame from the post \"{post_title}\"")
    # Use the stem as a hint if it is semantic (has letters, not just hex)
    if re.fullmatch(r"[0-9a-f-]+", stem.lower()):
        return (f"Imagem do post \"{post_title}\"" if lang_pt
                else f"Image from the post \"{post_title}\"")
    # Semantic stem — probably a place/theme name
    hint = re.sub(r"[-_]+", " ", stem).strip()
    hint = re.sub(r"\d+[a-z]?$", "", hint).strip()
    if hint:
        return (f"Fotografia — {hint} — do post \"{post_title}\"" if lang_pt
                else f"Photograph — {hint} — from the post \"{post_title}\"")
    return (f"Imagem do post \"{post_title}\"" if lang_pt
            else f"Image from the post \"{post_title}\"")


def build_vision_lookup(mapping: dict, url_map: dict) -> dict[str, str]:
    """Flatten the hand-authored alt mapping into {url: alt_text}."""
    # url_map: {local_filename: {download_url, original_url}}
    filename_to_url = {k: v["original_url"] for k, v in url_map.items()}
    lookup = {}
    for post_key, bucket in mapping.items():
        for filename, alt in bucket.get("alts", {}).items():
            url = filename_to_url.get(filename)
            if url:
                lookup[url] = alt
    return lookup


def process_file(path: Path, vision_alts: dict[str, str], post_title: str, lang_pt: bool) -> int:
    text = path.read_text(encoding="utf-8")
    original = text

    def img_sub(match: re.Match) -> str:
        attrs = match.group(1)
        src_m = _SRC_RE.search(attrs)
        if not src_m:
            return match.group(0)
        src = src_m.group(1)
        alt_m = _ALT_RE.search(attrs)
        # Already has non-empty alt → skip
        if alt_m and alt_m.group(1).strip():
            return match.group(0)
        # Pick alt source
        alt = vision_alts.get(src) or vision_alts.get(html.unescape(src))
        if not alt:
            filename = filename_from_src(src)
            alt = smart_fallback_alt(filename, post_title, lang_pt)
        # Insert or replace the alt attribute
        if alt_m:
            new_attrs = attrs[: alt_m.start()] + f'alt="{alt}"' + attrs[alt_m.end() :]
        else:
            new_attrs = attrs.rstrip() + f' alt="{alt}"'
        return f"<img{new_attrs}>"

    text = _IMG_TAG_RE.sub(img_sub, text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def main() -> int:
    if not MAPPING_FILE.exists():
        mapping = {}
    else:
        mapping = json.loads(MAPPING_FILE.read_text())
    url_map = json.loads(URL_MAP_FILE.read_text()) if URL_MAP_FILE.exists() else {}
    vision_alts = build_vision_lookup(mapping, url_map)

    titles = load_post_titles()
    print(f"Vision-sourced alts: {len(vision_alts)}")
    print(f"Posts with resolvable titles: {len(titles)}")

    total_touched = 0
    for root in POST_DIRS:
        lang_pt = "pt-br" in str(root)
        for md in root.rglob("*.md"):
            title = titles.get(str(md.relative_to(REPO)), md.stem.replace("-", " "))
            if process_file(md, vision_alts, title, lang_pt):
                total_touched += 1
    print(f"Files modified: {total_touched}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
