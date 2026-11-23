#!/usr/bin/env python3
"""Convert broken WordPress block embeds (Spotify + Instagram) to clean anchors.

Context: the WP → Hugo migration preserved <figure class="wp-block-embed
is-type-rich is-provider-X ..."> markup for providers whose official embed
widgets inject JS at runtime (Spotify, Instagram). Without that JS the markup
is just non-functional divs + an <a> inside.

This script finds every such figure, extracts the original URL from the first
<a href="..."> inside it, strips tracking params (utm_*, si=, sp_cid=), and
replaces the whole figure with a <p> containing a clean anchor:

  <p><a href="{clean_url}" target="_blank" rel="noopener noreferrer">
      {humanized URL} 🔗
  </a></p>

Idempotent: reruns do nothing when no wp-block-embed figures remain.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

# Matches `<figure class="wp-block-embed is-type-rich is-provider-{provider} ...">
# ...</figure>` as a single multi-line block. Non-greedy on the body so we
# stop at the FIRST </figure> that follows a matching opener.
_FIGURE_RE = re.compile(
    r"<figure\b[^>]*\bwp-block-embed\b[^>]*\bis-provider-(?P<provider>\w+)[^>]*>"
    r"(?P<body>.*?)</figure>",
    re.DOTALL | re.IGNORECASE,
)
_HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

PROVIDER_LABELS = {
    "spotify": "Ouvir no Spotify",
    "instagram": "Ver no Instagram",
}
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
                   "si", "sp_cid", "ref_src", "ref_url", "igshid"}


def clean_url(url: str) -> str:
    """Strip tracking params from a URL."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return url
    kept = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=False)
            if k not in TRACKING_PARAMS]
    new_query = urlencode(kept)
    return urlunparse(parsed._replace(query=new_query))


def replace_embed(match: re.Match) -> str:
    provider = match.group("provider").lower()
    body = match.group("body")
    href_match = _HREF_RE.search(body)
    if not href_match:
        return ""  # no link to recover — drop the broken figure silently
    url = clean_url(href_match.group(1))
    label = PROVIDER_LABELS.get(provider, f"Ver no {provider.capitalize()}")
    return (
        f'<p><a href="{url}" target="_blank" rel="noopener noreferrer">'
        f'{label} ↗</a></p>'
    )


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = _FIGURE_RE.subn(replace_embed, text)
    if n and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> None:
    total_files = 0
    total_embeds = 0
    for root in POST_DIRS:
        for md in root.rglob("*.md"):
            n = process_file(md)
            if n:
                total_files += 1
                total_embeds += n
                print(f"{md.relative_to(REPO)}: {n} embed(s) replaced")
    print(f"\nTotal: {total_embeds} embeds across {total_files} files converted to clean anchors.")


if __name__ == "__main__":
    main()
