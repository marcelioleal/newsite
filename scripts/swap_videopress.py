#!/usr/bin/env python3
"""
swap_videopress.py — swap empty VideoPress iframe figures for self-hosted <video> tags.

Pandoc stripped the iframe src from WordPress Gutenberg wp-block-video figures during
Phase 2 migration, leaving empty <div class="iframe"> placeholders. This script:

1. Re-fetches the original WP content for each affected post via the public REST API.
2. Extracts the VideoPress GUID (token) from each <iframe src="https://videopress.com/embed/<TOKEN>?...">.
3. Maps the token to the local video filename via scripts/media-manifest.json
   (where source_url is https://videos.files.wordpress.com/<TOKEN>/<file>.<ext>).
4. Replaces each empty <figure class="wp-block-video"> block in the migrated Markdown
   with a clean HTML5 <video> tag pointing at /videos/<file>, preserving the figcaption.
5. Deletes the orphan 139MB video (static/videos/20250201095728000070.mp4), which no
   migrated post references.

Idempotent: re-running after a successful swap finds no wp-block-video wrappers and
exits cleanly. Pass --dry-run to preview changes without touching disk.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.parse

import requests

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WP_API = "https://public-api.wordpress.com/wp/v2/sites/marcelioleal.com"
ORPHAN_VIDEO = REPO_ROOT / "static" / "videos" / "20250201095728000070.mp4"

# Matches the whole wp-block-video <figure>…</figure> in the migrated Markdown.
_FIGURE_RE = re.compile(
    r'<figure class="wp-block-video[^"]*">.*?</figure>',
    flags=re.DOTALL,
)
# Extracts the figcaption text from a migrated figure (may be empty / missing).
_FIGCAPTION_RE = re.compile(
    r'<figcaption>(.*?)</figcaption>',
    flags=re.DOTALL,
)
# Extracts the VideoPress token from the iframe src in the ORIGINAL WP HTML.
_EMBED_TOKEN_RE = re.compile(
    r'videopress\.com/embed/([A-Za-z0-9]+)',
)
# Finds the whole figure block in the ORIGINAL WP HTML (used to count/order figures).
_WP_FIGURE_RE = re.compile(
    r'<figure class="wp-block-video[^"]*">.*?</figure>',
    flags=re.DOTALL,
)


def load_token_to_file() -> dict[str, str]:
    """Build a map from VideoPress token to local /videos/<file> path."""
    manifest = json.loads((REPO_ROOT / "scripts" / "media-manifest.json").read_text())
    out: dict[str, str] = {}
    for entry in manifest:
        url = entry.get("source_url", "")
        if "videos.files.wordpress.com/" not in url:
            continue
        parts = urllib.parse.urlparse(url).path.lstrip("/").split("/", 1)
        if len(parts) != 2:
            continue
        token, filename = parts
        out[token] = filename
    return out


def fetch_wp_figures(post_slug: str) -> list[tuple[str, str]]:
    """Fetch original WP content for a post, return [(token, figcaption), ...] in document order."""
    # Infer the post id by slug — one extra REST call.
    r = requests.get(f"{WP_API}/posts", params={"slug": post_slug, "_fields": "id"}, timeout=30)
    r.raise_for_status()
    hits = r.json()
    if not hits:
        return []
    post_id = hits[0]["id"]
    r = requests.get(f"{WP_API}/posts/{post_id}", params={"_fields": "content"}, timeout=30)
    r.raise_for_status()
    html = r.json().get("content", {}).get("rendered", "")
    out: list[tuple[str, str]] = []
    for fig in _WP_FIGURE_RE.findall(html):
        m_tok = _EMBED_TOKEN_RE.search(fig)
        m_cap = _FIGCAPTION_RE.search(fig)
        if m_tok:
            cap = (m_cap.group(1).strip() if m_cap else "")
            # Decode a couple of common HTML entities so the caption is readable.
            cap = cap.replace("&#8211;", "–").replace("&#8212;", "—").replace("&#8230;", "…").replace("&amp;", "&")
            out.append((m_tok.group(1), cap))
    return out


def build_video_tag(src: str, caption: str) -> str:
    """Render a Hugo-friendly HTML <figure><video>...</video><figcaption>...</figcaption></figure>."""
    cap_html = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (
        f'<figure class="video">'
        f'<video src="{src}" controls preload="metadata" class="w-full" style="max-width:720px"></video>'
        f"{cap_html}"
        f"</figure>"
    )


def swap_post(path: pathlib.Path, token_map: dict[str, str], dry_run: bool) -> tuple[int, int]:
    """Return (figures_in_file, figures_swapped)."""
    original = path.read_text(encoding="utf-8")
    md_figures = _FIGURE_RE.findall(original)
    if not md_figures:
        return (0, 0)

    # Map post slug (directory name) back to the WP slug.
    slug = path.parent.name
    wp_figures = fetch_wp_figures(slug)
    if len(md_figures) != len(wp_figures):
        print(
            f"WARN {path.relative_to(REPO_ROOT)}: Markdown has {len(md_figures)} figures but "
            f"WP returned {len(wp_figures)} — swapping only matched pairs by index",
            file=sys.stderr,
        )

    swapped = 0
    new_text = original
    for md_fig, (token, caption) in zip(md_figures, wp_figures):
        filename = token_map.get(token)
        if not filename:
            print(
                f"WARN {path.relative_to(REPO_ROOT)}: VideoPress token {token!r} not in media-manifest.json",
                file=sys.stderr,
            )
            continue
        replacement = build_video_tag(f"/videos/{filename}", caption)
        new_text = new_text.replace(md_fig, replacement, 1)
        swapped += 1

    if swapped == 0 or new_text == original:
        return (len(md_figures), 0)
    if dry_run:
        print(f"[dry-run] would swap {swapped}/{len(md_figures)} figures in {path.relative_to(REPO_ROOT)}", file=sys.stderr)
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"swapped {swapped}/{len(md_figures)} figures in {path.relative_to(REPO_ROOT)}", file=sys.stderr)
    return (len(md_figures), swapped)


def iter_affected_posts() -> list[pathlib.Path]:
    """Posts that still carry wp-block-video markers."""
    out: list[pathlib.Path] = []
    for base in ("content/pt-br/posts", "content/en/posts"):
        root = REPO_ROOT / base
        if not root.exists():
            continue
        for md in root.rglob("index.md"):
            if "wp-block-video" in md.read_text(encoding="utf-8"):
                out.append(md)
    return sorted(out)


def delete_orphan(dry_run: bool) -> bool:
    """Delete the 139MB orphan video if it exists (no post references it)."""
    if not ORPHAN_VIDEO.exists():
        return False
    if dry_run:
        print(f"[dry-run] would delete orphan {ORPHAN_VIDEO.relative_to(REPO_ROOT)}", file=sys.stderr)
    else:
        ORPHAN_VIDEO.unlink()
        print(f"deleted orphan {ORPHAN_VIDEO.relative_to(REPO_ROOT)}", file=sys.stderr)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Swap empty VideoPress iframes for self-hosted <video> tags")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without touching disk")
    args = parser.parse_args()

    token_map = load_token_to_file()
    posts = iter_affected_posts()
    if not posts:
        print("no wp-block-video wrappers found — nothing to do", file=sys.stderr)
    total_figs = 0
    total_swapped = 0
    for p in posts:
        a, b = swap_post(p, token_map, args.dry_run)
        total_figs += a
        total_swapped += b

    delete_orphan(args.dry_run)

    verb = "would swap" if args.dry_run else "swapped"
    print(f"done — {verb} {total_swapped}/{total_figs} figures across {len(posts)} posts", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
