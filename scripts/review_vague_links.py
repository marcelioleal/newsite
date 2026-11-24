#!/usr/bin/env python3
"""Generate a review file for vague anchor texts across the posts.

Scans content/**/*.md for anchors whose visible text is in the "aqui" / "here"
family (non-descriptive, bad for screen readers + SEO). For each one, extracts:

  - file path
  - a snippet of surrounding context (160 chars)
  - the current link URL
  - the current link text
  - a suggested replacement based on the URL's host/path

Writes a markdown review file the owner can walk through in one sitting and
tick off replacements. The script does NOT modify any post.

Usage:
  python3 scripts/review_vague_links.py
    → writes docs/vague-links-review.md
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
POST_DIRS = [REPO / "content" / "pt-br" / "posts", REPO / "content" / "en" / "posts"]
OUT = REPO / "docs" / "vague-links-review.md"

# Case-insensitive, matches whole-word link texts (surrounded by word boundaries).
VAGUE_TEXTS_RE = re.compile(
    r"\b(aqui|clique\s+aqui|veja\s+aqui|aquele\s+aqui|leia\s+mais|saiba\s+mais|"
    r"link|here|click\s+here|read\s+more|more\s+here|see\s+here)\b",
    re.IGNORECASE,
)

# Markdown anchor:    [text](url)
_MD_ANCHOR_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

# HTML anchor:        <a href="url" ...>text</a>
_HTML_ANCHOR_RE = re.compile(
    r'<a\s+[^>]*href\s*=\s*["\'](?P<url>[^"\']+)["\'][^>]*>(?P<text>[^<]+)</a>',
    re.IGNORECASE,
)


# Host-aware suggestion heuristics ordered by specificity.
def suggest_replacement(url: str, lang_pt: bool) -> str:
    try:
        host = urlparse(url).hostname or ""
        path = urlparse(url).path.lower()
    except ValueError:
        return "linkDeterminar" if lang_pt else "determine link"
    host = host.lower()

    if "youtube.com" in host or "youtu.be" in host:
        return "assistir no YouTube" if lang_pt else "watch on YouTube"
    if "github.com" in host:
        if "/gist/" in path or host == "gist.github.com":
            return "ver gist no GitHub" if lang_pt else "see gist on GitHub"
        return "ver no GitHub" if lang_pt else "see on GitHub"
    if "medium.com" in host:
        return "ler no Medium" if lang_pt else "read on Medium"
    if "substack.com" in host:
        return "ler na newsletter" if lang_pt else "read the newsletter"
    if "linkedin.com" in host:
        return "ver no LinkedIn" if lang_pt else "see on LinkedIn"
    if "twitter.com" in host or host == "x.com":
        return "ver no X (Twitter)" if lang_pt else "see on X (Twitter)"
    if "instagram.com" in host:
        return "ver no Instagram" if lang_pt else "see on Instagram"
    if "open.spotify.com" in host or "spotify.com" in host:
        return "ouvir no Spotify" if lang_pt else "listen on Spotify"
    if "soundcloud.com" in host:
        return "ouvir no SoundCloud" if lang_pt else "listen on SoundCloud"
    if "vimeo.com" in host:
        return "assistir no Vimeo" if lang_pt else "watch on Vimeo"
    if "wikipedia.org" in host:
        return "ver na Wikipedia" if lang_pt else "see on Wikipedia"
    if "slideshare.net" in host:
        return "ver apresentação no SlideShare" if lang_pt else "see slides on SlideShare"
    if path.endswith(".pdf"):
        return "baixar o PDF" if lang_pt else "download the PDF"
    if "stackoverflow.com" in host:
        return "ver no Stack Overflow" if lang_pt else "see on Stack Overflow"
    if "google.com" in host and "docs." in host:
        return "ver no Google Docs" if lang_pt else "see on Google Docs"
    if "maps.google.com" in host or "google.com/maps" in path:
        return "ver no Google Maps" if lang_pt else "see on Google Maps"
    if "news.ycombinator.com" in host:
        return "ver no Hacker News" if lang_pt else "see on Hacker News"
    if "nubank.com" in host:
        return "Nubank"
    if "amazon.com" in host:
        return "Amazon"
    if "getyourguide.com" in host:
        return "GetYourGuide"
    if "qedu.org.br" in host or "qedu.com.br" in host:
        return "QEdu"
    if "beyondtech" in host or "beyond-tech" in host:
        return "Beyond Tech"
    if "google.com" in host:
        return "ver no Google" if lang_pt else "see on Google"
    # Fallback: name-drop the host so screen readers know where the link goes.
    if host:
        clean = host.replace("www.", "")
        return (f"ver em {clean}" if lang_pt else f"see at {clean}")
    return "link" if lang_pt else "link"


def collect_findings():
    findings = []
    for root in POST_DIRS:
        lang_pt = "pt-br" in str(root)
        for md in root.rglob("*.md"):
            text = md.read_text(encoding="utf-8")
            lines = text.split("\n")
            for lineno, line in enumerate(lines, 1):
                for match in _MD_ANCHOR_RE.finditer(line):
                    anchor_text, url = match.group(1), match.group(2)
                    if VAGUE_TEXTS_RE.fullmatch(anchor_text.strip()):
                        findings.append({
                            "file": str(md.relative_to(REPO)),
                            "lineno": lineno,
                            "text": anchor_text,
                            "url": url,
                            "context": line.strip()[:200],
                            "suggestion": suggest_replacement(url, lang_pt),
                            "lang": "pt" if lang_pt else "en",
                            "flavour": "markdown",
                        })
                for match in _HTML_ANCHOR_RE.finditer(line):
                    anchor_text = match.group("text").strip()
                    url = match.group("url")
                    if VAGUE_TEXTS_RE.fullmatch(anchor_text):
                        findings.append({
                            "file": str(md.relative_to(REPO)),
                            "lineno": lineno,
                            "text": anchor_text,
                            "url": url,
                            "context": line.strip()[:200],
                            "suggestion": suggest_replacement(url, lang_pt),
                            "lang": "pt" if lang_pt else "en",
                            "flavour": "html",
                        })
    return findings


def write_review(findings: list[dict]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    counter = Counter(f["text"].lower().strip() for f in findings)
    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    lines = [
        "# Vague anchor text — review",
        "",
        f"Scan date: 2026-11-24. Total findings: **{len(findings)}** across {len(by_file)} posts.",
        "",
        "## How to use this file",
        "",
        "Each finding shows: file + line number, current anchor text, the URL, and a context-aware suggestion. **Mark each finding** by changing the leading `[ ]` to `[x]` once applied.",
        "",
        "To apply all approved changes in one go, after reviewing run:",
        "```bash",
        "python3 scripts/review_vague_links.py --apply   # not yet implemented; ask Claude to produce it once marks are done",
        "```",
        "",
        "## Breakdown by anchor text",
        "",
    ]
    for text, count in counter.most_common():
        lines.append(f"- **{text}**: {count}")
    lines.append("")
    lines.append("## Findings by file")
    lines.append("")
    for filepath, entries in sorted(by_file.items()):
        lines.append(f"### `{filepath}`")
        lines.append("")
        for e in entries:
            flav = "HTML" if e["flavour"] == "html" else "MD"
            lines.append(f"- [ ] L{e['lineno']} ({flav}) — current: **{e['text']}** → `{e['url']}`")
            lines.append(f"  - **Suggest:** `{e['suggestion']}`")
            lines.append(f"  - **Context:** `{e['context'][:140]}…`" if len(e["context"]) > 140 else f"  - **Context:** `{e['context']}`")
            lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    findings = collect_findings()
    write_review(findings)
    print(f"Wrote {OUT} with {len(findings)} findings across {len({f['file'] for f in findings})} posts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
