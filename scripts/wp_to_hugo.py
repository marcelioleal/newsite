#!/usr/bin/env python3
"""
wp_to_hugo.py — WordPress.com → Hugo content migration tool.

Fetches posts, pages, and media from the WordPress.com public REST API,
converts rendered HTML to CommonMark via pandoc, applies a ~10-class regex
post-processor to strip Gutenberg/Jetpack residue, and writes Hugo page
bundles (or branch bundles for _index.md targets) with YAML front-matter.

Usage:
    python3 scripts/wp_to_hugo.py --manifest scripts/posts-manifest.json
    python3 scripts/wp_to_hugo.py --manifest scripts/media-manifest.json --kind media
    python3 scripts/wp_to_hugo.py --manifest scripts/recomendacoes-manifest.json --kind page

Prerequisites:
    brew install pandoc libheif
    pip3 install --user --break-system-packages requests pyyaml lingua-language-detector
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass
from typing import Any

import requests
import yaml

try:
    from lingua import Language, LanguageDetectorBuilder
    _LINGUA = LanguageDetectorBuilder.from_languages(Language.ENGLISH, Language.PORTUGUESE).build()
except ImportError:
    _LINGUA = None

WP_SITE = os.environ.get("WP_SITE", "marcelioleal.com")
WP_API = f"https://public-api.wordpress.com/wp/v2/sites/{WP_SITE}"

# Category ids where the content is English (hard override to EN in detection).
EN_CATEGORY_IDS = {22748652, 22748979}  # "Uncategorized-en", "Product Management"

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Regex post-processor for WP residue — 10 classes documented in research.
# ---------------------------------------------------------------------------

_WP_COMMENT = re.compile(r"<!--\s*/?wp:[^>]*-->")
_CAPTION_SC = re.compile(r"\[caption[^\]]*\](.*?)\[/caption\]", re.DOTALL)
_GALLERY_SC = re.compile(r"\[gallery[^\]]*\]")
_EMBED_SC = re.compile(r"\[embed[^\]]*\](.*?)\[/embed\]", re.DOTALL)
_YOUTUBE_SC = re.compile(r"\[youtube[^\]]*\]")
_FIGURE_WP = re.compile(r'<figure class="wp-block-image[^"]*">(.*?)</figure>', re.DOTALL)
_SH_BRUSH = re.compile(r"\[(?:source|code) ?language=['\"]?[a-z]+['\"]?\]", re.IGNORECASE)
_SH_BRUSH_CLOSE = re.compile(r"\[/(?:source|code)\]", re.IGNORECASE)
_SMART_QUOTES = str.maketrans({
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "–": "-", "—": "--",
    "…": "...",
})
_MULTI_NL = re.compile(r"\n{3,}")


def post_process_markdown(md: str) -> str:
    """Strip 10 classes of WP residue from pandoc Markdown output."""
    md = _WP_COMMENT.sub("", md)
    md = _CAPTION_SC.sub(r"\1", md)
    md = _GALLERY_SC.sub("", md)
    md = _EMBED_SC.sub(r"\1", md)
    md = _YOUTUBE_SC.sub("", md)
    md = _FIGURE_WP.sub(r"\1", md)
    md = _SH_BRUSH.sub("", md)
    md = _SH_BRUSH_CLOSE.sub("", md)
    md = md.translate(_SMART_QUOTES)
    md = _MULTI_NL.sub("\n\n", md)
    return md.strip() + "\n"


# ---------------------------------------------------------------------------
# WordPress.com public REST API client (unauthenticated, public posts only).
# ---------------------------------------------------------------------------


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{WP_API}/{path}"
    resp = requests.get(url, params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_item(kind: str, item_id: int) -> dict[str, Any]:
    """Fetch a single post or page by id."""
    endpoint = {"post": "posts", "page": "pages"}[kind]
    return _get(f"{endpoint}/{item_id}")


_CATEGORY_CACHE: dict[int, dict[str, Any]] = {}
_TAG_CACHE: dict[int, dict[str, Any]] = {}


def _load_term_caches() -> None:
    """One-shot load of all categories and tags (paginated)."""
    if _CATEGORY_CACHE:
        return
    for endpoint, cache in (("categories", _CATEGORY_CACHE), ("tags", _TAG_CACHE)):
        page = 1
        while True:
            try:
                batch = _get(endpoint, {"per_page": 100, "page": page, "hide_empty": False})
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 400:
                    break
                raise
            if not batch:
                break
            for term in batch:
                cache[term["id"]] = term
            if len(batch) < 100:
                break
            page += 1


def resolve_terms(ids: list[int], kind: str) -> list[str]:
    """Return slugs for a list of category/tag ids. Unknown ids drop."""
    _load_term_caches()
    cache = _CATEGORY_CACHE if kind == "category" else _TAG_CACHE
    return [cache[i]["slug"] for i in ids if i in cache]


# ---------------------------------------------------------------------------
# Language detection: hard override by category, else lingua, else 'pt-br'.
# ---------------------------------------------------------------------------


_HTML_TAG = re.compile(r"<[^>]+>")
_HTML_ATTR_LINE = re.compile(r"\b(class|src|href|srcset|alt|data-[a-z-]+|sizes|width|height|style|rel|target|loading|decoding|id)\s*=\s*\"[^\"]*\"")


def detect_language(categories: list[int], title: str, body_text: str) -> str:
    """Return 'pt-br' or 'en'.

    Strategy:
    1. Hard override by category (22748652, 22748979) → en.
    2. Clean the body of HTML tags + attribute cruft so lingua sees real prose.
    3. Build detection sample = title repeated 3x + first 1000 chars of cleaned body.
       Weighting the title helps when the body is HTML-heavy but the title is clear.
    4. Fall back to pt-br when lingua is unavailable or the sample is too short.
    """
    if any(c in EN_CATEGORY_IDS for c in categories):
        return "en"
    if _LINGUA is None:
        return "pt-br"
    cleaned = _HTML_ATTR_LINE.sub("", body_text)
    cleaned = _HTML_TAG.sub(" ", cleaned)
    cleaned = re.sub(r"https?://\S+", "", cleaned)  # strip URLs
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    sample = (title + " ") * 3 + cleaned[:1000]
    if len(sample.strip()) < 20:
        return "pt-br"
    lang = _LINGUA.detect_language_of(sample)
    return "en" if lang is not None and lang.name == "ENGLISH" else "pt-br"


# ---------------------------------------------------------------------------
# pandoc HTML → GFM Markdown.
# ---------------------------------------------------------------------------


def pandoc_html_to_md(html: str) -> str:
    proc = subprocess.run(
        ["pandoc", "--from=html", "--to=gfm", "--wrap=none"],
        input=html,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


# ---------------------------------------------------------------------------
# Hugo bundle writer.
# ---------------------------------------------------------------------------


@dataclass
class HugoPage:
    title: str
    date: str
    slug: str
    wp_id: int
    lang: str
    body: str
    categories: list[str]
    tags: list[str]
    translation_key: str | None = None
    target_path: str | None = None  # relative repo path; overrides default


def _front_matter(page: HugoPage) -> str:
    fm: dict[str, Any] = {
        "title": page.title,
        "date": page.date,
        "slug": page.slug,
        "wp_id": page.wp_id,
    }
    if page.categories:
        fm["categories"] = page.categories
    if page.tags:
        fm["tags"] = page.tags
    if page.translation_key:
        fm["translationKey"] = page.translation_key
    return yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)


def _default_target(page: HugoPage, kind: str) -> pathlib.Path:
    if kind == "post":
        return REPO_ROOT / "content" / page.lang / "posts" / page.slug / "index.md"
    # page: default to content/<lang>/<slug>/index.md
    return REPO_ROOT / "content" / page.lang / page.slug / "index.md"


def write_bundle(page: HugoPage, kind: str, force: bool, dry_run: bool) -> tuple[pathlib.Path, bool]:
    """Write the page bundle; return (path, written)."""
    if page.target_path:
        target = REPO_ROOT / page.target_path
    else:
        target = _default_target(page, kind)
    # Branch-bundle detection: if target path ends in _index.md, it's a branch bundle.
    # Otherwise it's a leaf bundle at index.md inside a per-slug dir.
    if target.exists() and not force:
        return target, False
    if dry_run:
        return target, False
    target.parent.mkdir(parents=True, exist_ok=True)
    fm = _front_matter(page)
    content = f"---\n{fm}---\n\n{page.body}"
    target.write_text(content, encoding="utf-8")
    return target, True


# ---------------------------------------------------------------------------
# Media handling.
# ---------------------------------------------------------------------------


_UPLOAD_PATH = re.compile(r"/wp-content/uploads/(\d{4})/(\d{2})/([^?#]+)$")


def _media_target(source_url: str, mime_type: str) -> pathlib.Path:
    """Compute static/ target path from a WP media source_url + mime_type."""
    parsed = urllib.parse.urlparse(source_url)
    basename = os.path.basename(parsed.path)
    if mime_type.startswith("video/"):
        return REPO_ROOT / "static" / "videos" / basename
    if mime_type == "application/pdf":
        return REPO_ROOT / "static" / "assets" / basename
    # images: preserve year/month from the WP upload path
    m = _UPLOAD_PATH.search(parsed.path)
    if m:
        year, month, fname = m.groups()
        return REPO_ROOT / "static" / "images" / year / month / fname
    return REPO_ROOT / "static" / "images" / basename


def download_media(entry: dict[str, Any], force: bool, dry_run: bool) -> tuple[pathlib.Path, bool]:
    source_url = entry["source_url"]
    mime_type = entry.get("mime_type", "application/octet-stream")
    target = _media_target(source_url, mime_type)
    if mime_type == "image/heic":
        target = target.with_suffix(".jpg")
    if target.exists() and not force:
        return target, False
    if dry_run:
        return target, False
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".download")
    with requests.get(source_url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
    if mime_type == "image/heic":
        heic = tmp.with_suffix(".heic")
        tmp.rename(heic)
        subprocess.run(
            ["heif-convert", "-q", "92", str(heic), str(target)],
            check=True,
            capture_output=True,
        )
        heic.unlink()
    else:
        tmp.rename(target)
    return target, True


# ---------------------------------------------------------------------------
# Content pipeline for post/page kinds.
# ---------------------------------------------------------------------------


def _strip_html_entities(s: str) -> str:
    """Decode a few common WP HTML entities in titles."""
    return (
        s.replace("&#8211;", "–")
        .replace("&#8212;", "—")
        .replace("&#8230;", "…")
        .replace("&#8216;", "'")
        .replace("&#8217;", "'")
        .replace("&#8220;", '"')
        .replace("&#8221;", '"')
        .replace("&amp;", "&")
        .replace("&nbsp;", " ")
        .replace("&#039;", "'")
    )


def migrate_content(entry: dict[str, Any], kind: str, force: bool, dry_run: bool) -> tuple[pathlib.Path, bool]:
    item_id = entry["id"]
    data = fetch_item(kind, item_id)
    html = data.get("content", {}).get("rendered", "")
    md = pandoc_html_to_md(html)
    md = post_process_markdown(md)
    title = _strip_html_entities(data.get("title", {}).get("rendered", ""))
    slug = entry.get("slug") or data.get("slug", str(item_id))
    date = data.get("date", "")
    categories = data.get("categories", []) or []
    tags = data.get("tags", []) or []
    lang = entry.get("lang", "auto")
    if lang == "auto":
        lang = detect_language(categories, title, md)
    page = HugoPage(
        title=title,
        date=date,
        slug=slug,
        wp_id=item_id,
        lang=lang,
        body=md,
        categories=resolve_terms(categories, "category"),
        tags=resolve_terms(tags, "tag"),
        translation_key=entry.get("translationKey"),
        target_path=entry.get("target_path"),
    )
    return write_bundle(page, kind, force, dry_run)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="WordPress.com → Hugo migration")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON (list of entries)")
    parser.add_argument(
        "--kind",
        choices=("post", "page", "media"),
        help="Optional: filter manifest to entries of this kind (otherwise uses each entry's own 'kind')",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing targets")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written; do not touch disk")
    args = parser.parse_args()

    manifest_path = pathlib.Path(args.manifest)
    if not manifest_path.exists():
        print(f"error: manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))

    counts = {"fetched": 0, "written": 0, "skipped": 0, "failed": 0}
    for entry in entries:
        entry_kind = args.kind or entry.get("kind", "post")
        if args.kind and entry.get("kind") and entry["kind"] != args.kind:
            continue
        try:
            counts["fetched"] += 1
            if entry_kind == "media":
                target, written = download_media(entry, args.force, args.dry_run)
            else:
                target, written = migrate_content(entry, entry_kind, args.force, args.dry_run)
            if written:
                counts["written"] += 1
                print(f"wrote {target.relative_to(REPO_ROOT)}", file=sys.stderr)
            else:
                counts["skipped"] += 1
        except Exception as exc:
            counts["failed"] += 1
            print(f"FAIL id={entry.get('id','?')} kind={entry_kind}: {exc}", file=sys.stderr)

    print(
        f"done — fetched={counts['fetched']} written={counts['written']} "
        f"skipped={counts['skipped']} failed={counts['failed']}",
        file=sys.stderr,
    )
    return 0 if counts["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
