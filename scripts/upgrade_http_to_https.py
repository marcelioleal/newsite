#!/usr/bin/env python3
"""Rewrite http:// → https:// in post content for domains known to support TLS.

Mixed HTTP content on an HTTPS site either gets blocked by the browser
(images, scripts) or shows "Not Secure" warnings (links). This script only
upgrades a curated whitelist of domains confirmed to serve HTTPS, so legacy
posts stop triggering those warnings without breaking links to actually-dead
HTTP-only resources.

Leaves alone:
  - domains known to be dead (imageshack, 2.download-1.files-upload)
  - domains that may not support HTTPS at the time of this migration

Idempotent.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]

# Domains verified (as of 2026-11) to serve HTTPS. Each entry matches the
# bare host OR any subdomain.
HTTPS_READY = [
    "google.com", "maps.google.com",
    "wikipedia.org",
    "github.com", "gist.github.com",
    "twitter.com", "x.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com", "youtu.be",
    "medium.com", "cdn-images-1.medium.com",
    "stackoverflow.com",
    "amazon.com", "amazon.com.br",
    "facebook.com",
    "spotify.com", "open.spotify.com",
    "soundcloud.com",
    "vimeo.com", "player.vimeo.com",
    "slideshare.net", "image.slidesharecdn.com",
    "flickr.com",
    "infoworld.com", "www.infoworld.com",
    "nytimes.com",
    "bbc.co.uk", "bbc.com",
    "theguardian.com",
    "reddit.com",
    "producthunt.com",
    "elevenlabs.io",
    "openai.com",
    "anthropic.com",
    "mozilla.org", "developer.mozilla.org",
    "w3.org",
]

# Build a regex matching http://<host> where host is in HTTPS_READY or a
# subdomain of one of those. Longest patterns first to avoid partial matches
# (e.g. "amazon.com.br" before "amazon.com").
_hosts = sorted(HTTPS_READY, key=len, reverse=True)
_HOST_PATTERN = "|".join(re.escape(h) for h in _hosts)
_URL_RE = re.compile(rf"http://((?:[a-z0-9-]+\.)*(?:{_HOST_PATTERN}))(?=[/\"'\s?#>])", re.IGNORECASE)


def process_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = _URL_RE.subn(lambda m: f"https://{m.group(1)}", text)
    if n and new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> None:
    total_files = 0
    total_upgrades = 0
    for root in POST_DIRS:
        for md in root.rglob("*.md"):
            n = process_file(md)
            if n:
                total_files += 1
                total_upgrades += n
                print(f"{md.relative_to(REPO)}: {n} URL(s) upgraded")
    print(f"\nTotal: {total_upgrades} http:// → https:// upgrades across {total_files} files.")


if __name__ == "__main__":
    main()
