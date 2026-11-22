# scripts/ — WordPress.com → Hugo migration tooling

Internal tooling for Phase 2 of the WordPress-to-Hugo migration. Fetches content from the WordPress.com public REST API, converts to Hugo page bundles with YAML front-matter, downloads and normalizes media.

## Prerequisites

```bash
# Homebrew: Pandoc for HTML → Markdown, libheif for HEIC → JPEG.
brew install pandoc libheif

# Python packages (via pip with --break-system-packages for brew-managed python).
pip3 install --user --break-system-packages requests pyyaml lingua-language-detector
```

Verify:

```bash
pandoc --version          # 3.14+
heif-convert --help       # libheif 1.23+
python3 -c "from lingua import Language; print(Language.ENGLISH.name)"
```

## wp_to_hugo.py

### Usage

```bash
python3 scripts/wp_to_hugo.py --manifest <path> [--kind post|page|media] [--force] [--dry-run]
```

- `--manifest`: JSON array of entries `{id, slug?, kind, lang?, translationKey?, target_path?, source_url?, mime_type?}`.
- `--kind` (optional): filter the manifest to one kind. Omit to use each entry's own `kind` field.
- `--force`: overwrite existing target files.
- `--dry-run`: print what would be written; touch nothing.

### Manifest shapes

**Posts/pages:**
```json
[
  {"id": 1377, "slug": "eu-deveria-estar-gravando-videos-mas", "kind": "post", "lang": "auto"},
  {"id": 143, "slug": "recomendacoes", "kind": "page", "lang": "pt-br",
   "translationKey": "recomendacoes",
   "target_path": "content/pt-br/recomendacoes/_index.md"}
]
```

- `lang: "auto"` triggers detection: hard override for category 22748652 (Uncategorized-en) + 22748979 (Product Management) → `en`; otherwise `lingua-language-detector` on the body; default `pt-br`.
- `target_path` overrides the default output path (`content/<lang>/posts/<slug>/index.md` for posts, `content/<lang>/<slug>/index.md` for pages). A path ending in `/_index.md` writes a Hugo branch bundle (section listing), otherwise a leaf bundle.

**Media:**
```json
[
  {"id": 1377, "source_url": "https://marcelioleal.com/wp-content/uploads/2026/05/photo.jpg",
   "mime_type": "image/jpeg", "kind": "media"}
]
```

Target routing:
- `image/*` → `static/images/<year>/<month>/<basename>` (year/month parsed from WP upload path).
- `image/heic` → same as above but with `.jpg` suffix after `heif-convert -q 92`.
- `video/*` or `video/videopress` → `static/videos/<basename>`.
- `application/pdf` → `static/assets/<basename>`.

### Conversion pipeline

1. Fetch rendered HTML from `https://public-api.wordpress.com/wp/v2/sites/marcelioleal.com/{posts|pages}/{id}` (unauthenticated, public content only).
2. `pandoc --from=html --to=gfm --wrap=none` on `content.rendered`.
3. Regex post-processor strips 10 WP residue classes:
   - Gutenberg `<!-- wp:* -->` block comments
   - `[caption]` / `[gallery]` / `[embed]` / `[youtube]` shortcodes
   - `<figure class="wp-block-image">...</figure>` wrappers
   - SyntaxHighlighter `[source language=...]` wrappers
   - WordPress smart-quotes/em-dashes/ellipses → UTF-8
   - Triple-plus newlines collapse to double
4. Write Hugo bundle with YAML `---` front-matter (title, date, slug, wp_id, categories, tags, translationKey?).

### Idempotency

The script skips any target that already exists on disk. Pass `--force` to overwrite. `--dry-run` reports what WOULD be written without touching disk.

### Environment

- `WP_SITE` env var overrides the default WordPress.com site slug (`marcelioleal.com`).

## rewrite_media_urls.py

Post-migration pass that rewrites inline WordPress media URLs in migrated Markdown to the local `/images/`, `/videos/`, `/assets/` paths. Called after `wp_to_hugo.py` has downloaded the media. Idempotent: safe to run multiple times.

```bash
python3 scripts/rewrite_media_urls.py
```
