#!/usr/bin/env python3
"""
cleanup_jetpack_proxies.py — archive Jetpack-proxied external images locally.

Phase 2 migration left ~157 Jetpack-proxied URLs (https://i[0-9]*.wp.com/<host>/<path>?resize=...)
pointing at external images (imageshack, giphy, medium CDN, old Brazilian sites). Many
of those external hosts are DEAD (imageshack.us shut down, old blogs offline) but
Jetpack has cached copies that still serve.

Strategy: download each image from the Jetpack proxy while it still works, store under
static/images/external/<host>/<basename>, rewrite the URL. Images that 404 or fail to
download have their <img ...> tags removed entirely (the content was already broken).

Idempotent: re-running skips URLs already rewritten. Pass --dry-run to preview.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys
import urllib.parse

import requests

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXT_ROOT = REPO_ROOT / "static" / "images" / "external"

# Matches a full Jetpack-proxied URL and captures (external-host, external-path).
# External-path includes the leading slash through the first ? or whitespace or quote.
_JETPACK_URL = re.compile(
    r'https?://i[0-9]*\.wp\.com/([^/]+)(/[^?#\s"\'<>)]+)(?:\?[^\s"\'<>)]*)?'
)

# Finds <img ...> tags whose src is a Jetpack URL — used to remove dead-image tags.
_IMG_TAG_WITH_JETPACK = re.compile(
    r'<img[^>]+src="(https?://i[0-9]*\.wp\.com/[^"]+)"[^>]*>',
    flags=re.IGNORECASE,
)
# Also match <a href="jetpack-url">...</a> wrappers around a dead image.
_A_TAG_WITH_JETPACK = re.compile(
    r'<a href="(https?://i[0-9]*\.wp\.com/[^"]+)"[^>]*>\s*(.*?)\s*</a>',
    flags=re.IGNORECASE | re.DOTALL,
)


def safe_basename(external_path: str) -> str:
    """Produce a stable filesystem-safe basename from the external URL path."""
    raw = external_path.rsplit("/", 1)[-1] or "image"
    # Decode URL encoding and keep [a-zA-Z0-9._-] only.
    decoded = urllib.parse.unquote(raw)
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", decoded)
    if "." not in cleaned:
        cleaned = f"{cleaned}.img"
    # Guard against very long names.
    if len(cleaned) > 120:
        suffix = pathlib.Path(cleaned).suffix[:8] or ".img"
        stem = cleaned[: 100 - len(suffix)]
        cleaned = stem + suffix
    return cleaned


def target_for(url: str, host: str, ext_path: str) -> pathlib.Path:
    """Compute the local target path. Dedupe collisions via a 6-char URL hash."""
    basename = safe_basename(ext_path)
    host_dir = re.sub(r"[^A-Za-z0-9._-]", "_", host)
    candidate = EXT_ROOT / host_dir / basename
    if candidate.exists():
        # Re-use if the file is already present — keeps idempotency.
        return candidate
    # If a sibling with the same basename exists from a different URL, append hash.
    if (EXT_ROOT / host_dir).exists() and candidate.name in [p.name for p in (EXT_ROOT / host_dir).iterdir()]:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:6]
        stem = pathlib.Path(basename).stem
        suffix = pathlib.Path(basename).suffix
        candidate = EXT_ROOT / host_dir / f"{stem}-{digest}{suffix}"
    return candidate


def try_download(url: str, dest: pathlib.Path) -> bool:
    """Download url → dest. Return True on success, False on any failure."""
    try:
        with requests.get(url, stream=True, timeout=30, allow_redirects=True) as r:
            if r.status_code != 200:
                return False
            # Skip tiny bodies that are likely error pages.
            content_type = r.headers.get("content-type", "").lower()
            if "html" in content_type:
                return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + ".download")
            size = 0
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        size += len(chunk)
            if size < 100:
                tmp.unlink(missing_ok=True)
                return False
            tmp.rename(dest)
            return True
    except (requests.RequestException, OSError):
        return False


def process_text(text: str, dry_run: bool) -> tuple[str, int, int]:
    """Return (new_text, rewrites, removals)."""
    rewrites = 0
    removals = 0

    # Collect every unique Jetpack URL in the text (so we download once).
    urls = set(m.group(0) for m in _JETPACK_URL.finditer(text))
    url_to_replacement: dict[str, str | None] = {}  # None → remove the tag

    for url in urls:
        m = _JETPACK_URL.match(url)
        if not m:
            continue
        host, ext_path = m.group(1), m.group(2)
        target = target_for(url, host, ext_path)
        rel_target = f"/{target.relative_to(REPO_ROOT / 'static').as_posix()}".replace("/images/", "/images/")
        rel_target = f"/images/external/{target.relative_to(EXT_ROOT).as_posix()}"
        if target.exists():
            url_to_replacement[url] = rel_target
            continue
        if dry_run:
            # Pretend download succeeded for preview purposes.
            url_to_replacement[url] = rel_target
            continue
        if try_download(url, target):
            print(f"  downloaded {url} → {target.relative_to(REPO_ROOT)}", file=sys.stderr)
            url_to_replacement[url] = rel_target
        else:
            print(f"  DEAD {url} — removing <img>/<a> tag", file=sys.stderr)
            url_to_replacement[url] = None

    # Walk the text applying replacements. Dead URLs (None) remove the whole <img ...> tag
    # (and if wrapped in <a href="same-url">...</a>, remove that too).
    new_text = text

    # First, remove <a href="jetpack-url"> wrappers whose target is dead.
    def _a_sub(match: re.Match[str]) -> str:
        nonlocal removals
        href = match.group(1)
        inner = match.group(2)
        repl = url_to_replacement.get(href)
        if repl is None:
            # Dead anchor — drop the whole <a>…</a> and any <img> inside.
            removals += 1
            return ""
        # Live anchor — leave for the per-URL substitution below (we'll rewrite the href then).
        return match.group(0)

    new_text = _A_TAG_WITH_JETPACK.sub(_a_sub, new_text)

    # Next, remove <img src="jetpack-url"> tags whose target is dead.
    def _img_sub(match: re.Match[str]) -> str:
        nonlocal removals
        src = match.group(1)
        repl = url_to_replacement.get(src)
        if repl is None:
            removals += 1
            return ""
        return match.group(0)

    new_text = _IMG_TAG_WITH_JETPACK.sub(_img_sub, new_text)

    # Finally, substitute every surviving Jetpack URL with its local path.
    for url, repl in url_to_replacement.items():
        if repl is None:
            continue
        if url in new_text:
            new_text = new_text.replace(url, repl)
            rewrites += 1

    return new_text, rewrites, removals


def iter_markdown() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for base in ("content/pt-br", "content/en"):
        root = REPO_ROOT / base
        if not root.exists():
            continue
        out.extend(root.rglob("*.md"))
    return sorted(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive Jetpack-proxied external images locally")
    parser.add_argument("--dry-run", action="store_true", help="Preview without touching disk")
    args = parser.parse_args()

    files = iter_markdown()
    changed_files = 0
    total_rewrites = 0
    total_removals = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "i0.wp.com" not in text and "i1.wp.com" not in text and "i2.wp.com" not in text:
            continue
        # Skip URLs that point at marcelioleal.com (those are our own, already handled in Phase 2).
        if not re.search(r"https?://i\d*\.wp\.com/(?!marcelioleal\.com)", text):
            continue
        new_text, rewrites, removals = process_text(text, args.dry_run)
        if rewrites == 0 and removals == 0:
            continue
        changed_files += 1
        total_rewrites += rewrites
        total_removals += removals
        if args.dry_run:
            print(f"[dry-run] {path.relative_to(REPO_ROOT)}: +{rewrites} rewrites, -{removals} removals", file=sys.stderr)
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"{path.relative_to(REPO_ROOT)}: +{rewrites} rewrites, -{removals} removals", file=sys.stderr)

    verb = "would change" if args.dry_run else "changed"
    print(
        f"done — {verb} {changed_files} files; {total_rewrites} rewrites, {total_removals} dead-tag removals",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
