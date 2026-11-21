---
date: 2026-11-21
agent: best-practices
topic: wordpress-to-hugo-mig-phase-2-content-migration
depth: deep
---

## Best Practices Research Summary

Scope — Phase 2 Content Migration of a WordPress.com → Hugo migration. Source: 107 posts (2007–2026) + 20 pages + 134 media assets on `marcelioleal.com`. Target: Hugo + PaperMod with bilingual pt-br/en, Netlify deploy. The content-fetch channel is **already resolved**: the WordPress.com MCP server supplies the rendered HTML — no third-party exporter plugin is in play. This research locks the seven open decisions the caller named (conversion tool, language detection, bundle vs flat, permalinks, HEIC, VideoPress, WP-HTML cleanup), citing authoritative sources and flagging the trade-offs that bite in practice.

Overall shape of the recommendation, stated up front so the body can defend each piece:

1. **Convert with `pandoc --from html --to gfm --wrap=none`** as the one-shot default, then post-process with a short Python regex pass to normalise Gutenberg comments, Jetpack shortcodes, VideoPress embeds, and image paths. Rationale: pandoc handles the 80% (lists, code fences, tables, links, bold/italic, nested blockquotes) correctly; the last 20% is WP-specific and belongs in a regex layer, not in the converter.
2. **Detect language with `lingua-language-detector` (Python)**, not langdetect or fasttext, because 107 posts × ~98% accuracy means ~2 corrections — tractable to eyeball — and lingua wins decisively on short text, which matters for short posts like "Recomendações" sub-entries. Use the known-English category (22748652) as a prior and let lingua resolve everything else.
3. **Use Hugo page bundles** (`content/{lang}/posts/{slug}/index.md` + co-located media). Flat markdown looks cheaper up front but makes the next twenty years of edits painful; page bundles are the current community default confirmed by every 2026 migration write-up read for this research.
4. **Permalinks**: `[permalinks] posts = '/:slug/'` and `pages = '/:sections[1:]/:slug/'` in `hugo.toml`, matching WordPress's slug-only post URL. Preserve old URLs as the canonical new URLs — avoid redirects where possible and limit Hugo `aliases` to true edge cases.
5. **HEIC → JPEG with `heif-convert -q 92`** from `libheif-examples`. Smaller dependency surface than ImageMagick + delegates, faster, and HEIC → JPEG is lossy no matter what tool runs (JPEG is lossy by definition), so the "lossless" framing doesn't apply.
6. **VideoPress MP4s: download to `static/videos/` and self-host.** The source URL pattern `https://videos.files.wordpress.com/<token>/<filename>.mp4` is a direct-GET and will stop resolving when the WP.com site is decommissioned in Phase 3. For ~8–10 videos the storage cost is negligible; the risk of broken embeds post-cutover is not.
7. **WP-specific HTML cleanup** happens in a documented Python post-process script with ~10 regex rules (Gutenberg `<!-- wp:* -->` comments, `[caption]`, `[gallery]`, `[embed]`, `[youtube]`, `wp-block-image` wrappers, `<pre class="wp-block-code">` → fenced blocks, VideoPress iframe → `{{< video >}}` shortcode, image URL rewrite, trailing `wpautop` artifacts).

### Must Have

Non-negotiable practices — skipping any of these creates rework in Phase 2 or breaks Phase 3 cutover.

#### MH-1. Convert with `pandoc --from html --to gfm --wrap=none` as the default, not turndown or html2text

- Pandoc's GFM output is version-controllable, preserves lists/code/tables correctly, and is the explicit recommendation of multiple 2026 WordPress-to-Hugo migration write-ups:
  > "For converting WordPress content to Markdown with Pandoc, export your WordPress content as HTML and run it through Pandoc to convert to Markdown. The command is: `pandoc -f html -t gfm page.html -o page.md`" — webclaw.io 2026 HTML-to-Markdown guide (`https://webclaw.io/blog/convert-html-to-markdown-2026-guide`)
- `--wrap=none` is the version-control hygiene flag that matters here:
  > "`--wrap=none` means pandoc will not wrap lines at all. This option is recommended for Markdown that will be version-controlled — it produces cleaner Git diffs." — pandoc user guide via glukhov.org (`https://www.glukhov.org/documentation-tools/markdown/gfm-vs-commonmark-vs-pandoc-markdown/`)
- Pandoc's accuracy vs. alternatives on raw numbers alone looks weaker: "Go library html-to-markdown and Python's markdownify are the best HTML to Markdown tools in 2026, tying at 96% accuracy, while pandoc finished at 76%." — webclaw.io 2026 guide (same URL). The reason for the gap is important: `"With the stock GFM target, pandoc scores lower because anything it cannot express in GFM passes straight through as raw HTML."` [INFERRED — this behaviour is pandoc's own documented fallback, and it is a feature for our use case, not a bug: we *want* the un-convertible WP-specific HTML surfaced so the regex post-pass can see it.]
- Turndown is a reasonable Node alternative with one real advantage — `addRule()` for custom block handling:
  > "The Turndown library can be used to convert serialized Gutenberg blocks in the browser … Turndown supports adding custom rules using `addRule()` with a filter to target specific HTML elements like `figcaption` and `figure`." — leadmagic.io HTML-to-Markdown guide (`https://leadmagic.io/blog/how-to-convert-html-to-markdown`)
  But `addRule()` only beats pandoc + regex when you have >20 distinct block types. For a 107-post personal blog, the regex post-pass is simpler and inspectable in a text editor.
- `python-html2text` is the weakest of the three for Gutenberg: it mangles nested block structures and does not preserve code-block language hints. [INFERRED from the consistent absence of html2text from 2025–2026 migration write-ups read for this research — every reported migration used pandoc, turndown, or UnifiedJS, never html2text.]
- Custom BeautifulSoup pipelines are a tempting fourth option. They are strictly worse than pandoc + regex for the same reason custom XML parsers lose to `xmllint` + XSLT: you end up re-implementing the Markdown writer, which is the hard part. [INFERRED from the UnifiedJS write-up: `"They built a processing pipeline combining multiple plugins rather than relying on a single converter … The author dedicated significant effort (139 lines of code) to fix malformed <pre> tags."` — Swizec 2024 write-up (`https://swizec.com/blog/how-to-export-a-large-wordpress-site-to-markdown/`). 139 lines for one block type is the warning sign.]

**Decision**: `pandoc --from html --to gfm --wrap=none --markdown-headings=atx` + a ~100-line Python regex post-processor. The regex rules are enumerated in MH-7 below.

#### MH-2. Use Hugo page bundles, not flat markdown, with media co-located in each bundle

- The 2026 Hugo community consensus is explicit:
  > "Page bundles mean each post lives in its own folder with all its assets, and images can use relative paths like `images/screenshot.png` in the Markdown, making posts completely self-contained. The obvious benefit is file colocation — all files related to a single post live in the same directory, and because all links to images follow real relative paths, Markdown previews finally render correctly." — Pawel Grzybek migration write-up (`https://pawelgrzybek.com/migration-from-single-content-files-to-hugo-page-bundles/`)
- Every 2026 WP-to-Hugo migration read for this research used page bundles:
  > "The team adopted page bundles as their organizational approach. Each post became 'a directory with `index.md` and a `featured.*` image sitting next to each other,' enabling Hugo's image processing pipeline to handle resizing and cropping automatically." — banasiak.com 2026 migration (`https://blog.banasiak.com/2026/03/hugo-migration/`)
  > "They adopted page bundles, organizing posts hierarchically with self-contained assets: `content/posts/2025/03/post-name/├── index.md └── images/screenshot.png`. This approach allowed relative image paths within markdown files." — Three Portkeys migration (`https://www.threeportkeys.com/posts/migrating-my-website-from-wordpress-to-hugo-with-claude-code/`)
- The counter-argument for flat markdown + parallel `static/images/YYYY/MM/` is that it preserves WordPress's existing image URLs 1:1 and makes the image rewrite step a no-op. That's real, but:
  - Phase 3 is building 301s anyway — image URLs are one more entry in the redirect table, not a reason to warp the content layout.
  - PaperMod's single-page template supports page-bundle featured images out of the box (via `.Resources`), and losing that means custom theme work.
- **Target shape for this repo**:
  ```
  content/pt-br/posts/<slug>/index.md
  content/pt-br/posts/<slug>/cover.jpg
  content/pt-br/posts/<slug>/screenshot-01.jpg
  content/en/posts/<slug>/index.md        # when translation exists
  content/pt-br/recomendacoes/_index.md
  content/pt-br/recomendacoes/livros/_index.md
  content/pt-br/recomendacoes/livros/<book-slug>/index.md
  ```
  Nested `_index.md` section pages are how Hugo renders the Recomendações landing + sub-category pages. [INFERRED from Hugo's documented `_index.md` section-page contract — see MH-4 permalinks for the matching URL shape.]
- **Shared media** (anything referenced from more than one post, or branding assets) still goes to `static/images/` — the bundle rule is per-post, not absolute.

#### MH-3. Fetch Gutenberg raw block markup via the WordPress.com MCP, then hand pandoc the rendered HTML

The WP.com MCP's post-read tools (`wpcom-mcp-posts-get`, `wpcom-mcp-posts-list`) route through the WP.com REST API. Two output modes matter here:

> "By default the REST API returns rendered content (HTML with shortcodes processed) … With `context=edit`, you get the raw block markup as it lives in the database, which is what you want for round-trips that update content. The default rendered response provides processed HTML suitable for displaying on the front-end, while the raw format contains the original Gutenberg block structure with HTML comments for further processing." — smartwp.com WordPress REST API 2026 guide (`https://smartwp.com/wordpress-rest-api/`)

**Decision**: use the **rendered** HTML (the default), not the raw block markup. Reasons:

- Rendered HTML has shortcodes **already expanded**, which means `[caption id="…"]...[/caption]` is already a `<figure class="wp-caption">`, `[gallery ids="…"]` is already an `<img>` grid, and `[youtube]` is already an `<iframe>`. Pandoc knows what to do with figures and iframes; it doesn't know what `[caption]` means.
- Raw block markup requires a WordPress block parser (`@wordpress/block-serialization-default-parser` or equivalent) to turn `<!-- wp:paragraph --><p>…</p><!-- /wp:paragraph -->` into something pandoc can read. That's a second converter layer with its own bug surface.
- The 2026 Kinsta headless-WP write-up makes the same call: the rendered branch is the one with the fewer steps unless you're planning to re-publish back to a block editor, which we are not. (`https://kinsta.com/blog/headless-wordpress-gutenberg/`)

The one thing rendered HTML doesn't give us cleanly is **the Gutenberg `<!-- wp:paragraph -->` HTML comments** — but WP.com's rendered output strips those by default, so we only see them if a post was saved mid-draft in a way that leaked the raw comment into the published HTML. Treat residual `<!-- wp:*[^-]*-->` as a single-line regex strip in the post-process (see MH-7).

#### MH-4. Permalinks: slug-only posts, match WordPress exactly, no date prefix

WordPress.com's current permalink structure on `marcelioleal.com` is slug-only (`/{slug}/`). Hugo must match this exactly, or every inbound link, SEO signal, and social-share preview from 19 years of the blog breaks.

- The canonical Hugo configuration for slug-only post URLs:
  > "You can configure Hugo to match WordPress URLs using the `[Permalinks]` section in `config.toml` with patterns like `/categoryname/:slug`." — gohugo.io permalinks docs (`https://gohugo.io/configuration/permalinks/`)
- Exact tokens that matter for this migration (from the same doc):
  - `:slug` — "uses the slug as defined in front matter, else the title as defined in front matter, else the automatic title."
  - `:sections` / `:sections[1:]` — slice syntax for nested sections; `:sections[1:]` skips the first section, which is how to drop a leading `posts/` from a URL while keeping the section structure in `content/`.
  - `url` front matter — overrides any permalink pattern entirely, and is the escape hatch for the rare post whose slug cannot be made to match.
- **Target `hugo.toml` additions**:
  ```toml
  [permalinks]
    [permalinks.page]
      posts = "/:slug/"
    [permalinks.section]
      recomendacoes = "/recomendacoes/"
      recommendations = "/recommendations/"
  ```
  Posts get `/{slug}/`. Pages under `recomendacoes/livros/<book-slug>/` naturally render at `/recomendacoes/livros/<book-slug>/` because Hugo's default for pages is `/:sections/:slug/`.
- **Bilingual nuance** — when `defaultContentLanguageInSubdir = false` (as in this repo's current `hugo.toml`), the default language (pt-br) renders at root (`/<slug>/`) and the alternate language (en) renders under `/en/<slug>/`. This matches WordPress.com's shape exactly and is the right call. Confirmed by the Hugo multilingual example repo (`https://github.com/jmooring/hugo-multilingual-example`).
- **Per-language permalinks** are supported if needed:
  > "Nest the `permalinks` configuration under language keys: `[languages.de.permalinks]...`" — gohugo.io permalinks docs (`https://gohugo.io/configuration/permalinks/`). Not needed for this migration since both languages share slug-only shape, but worth knowing as an escape hatch for the TCC/ClassGenerator pair if their slugs end up different per language.

#### MH-5. HEIC → JPEG via `heif-convert -q 92`, batch via shell loop

- The 2026 Linux HEIC-to-JPG comparison is decisive:
  > "heif-convert from the libheif package is the fastest method … heif-convert from libheif works perfectly as the cleanest minimal tool. It decodes HEIC natively without depending on ImageMagick delegates, making it lightweight and efficient." — howtoconvert.co 2026 guide (`https://howtoconvert.co/blog/how-to-convert-heic-to-jpg-on-linux`)
- Install on macOS: `brew install libheif` ships the `heif-convert` binary. On Debian/Ubuntu CI: `sudo apt install libheif-examples`.
- Command shape:
  ```bash
  find static/images -iname '*.heic' -print0 | while IFS= read -r -d '' f; do
    heif-convert -q 92 "$f" "${f%.heic}.jpg"
  done
  ```
  `-q 92` matches the quality setting recommended by the 2026 kbmisc guide (`https://kbmisc.com/blog/convert-heif-images-to-jpg-or-png-on-linux`) — high enough to be visually indistinguishable from the HEIC source, low enough to keep file sizes reasonable.
- **"Lossless" caveat**: the caller asked about lossless HEIC conversion. Strictly speaking this is not achievable to JPEG:
  > "JPEG itself is a lossy format, so converting HEIC to JPEG cannot be truly lossless by definition." — howtoconvert.co 2026 guide (same URL)
  If true-lossless is required, convert to **lossless WebP** instead (`cwebp -lossless -q 100 input.heic.jpg output.webp` after an initial HEIC→PNG hop) or keep PNG. For a personal blog, `-q 92` JPEG is the right trade.
- **EXIF preservation**: heif-convert preserves EXIF (camera, GPS, timestamps) by default. ImageMagick also preserves EXIF by default. [INFERRED from the 2026 Linux guides consistently reporting EXIF retention for both tools — only a `-strip` or equivalent flag drops it.]
- **ImageMagick as fallback** — only if a HEIC variant (e.g. Apple's live-photo HEIC with motion payload) fails heif-convert. ImageMagick with the libheif delegate reads these, at the cost of a heavier dependency. The `magick input.heic -quality 90 output.jpg` syntax works per the cleverutils.com guide (`https://cleverutils.com/heic-to-jpg/command-line`).

#### MH-6. Download VideoPress MP4s to `static/videos/` and self-host — do not leave `videos.files.wordpress.com` URLs in the content

- The URL pattern is a direct-GET MP4:
  > "VideoPress videos hosted at videos.videopress.com can be accessed directly in browser — for example, URLs like `http://videos.videopress.com/[video-id]/[filename].mp4` can be played or downloaded in a web browser." — swarmify.com 2026 (`https://swarmify.com/blog/never-upload-video-to-wordpress-website/`)
  The same holds for the `videos.files.wordpress.com/<token>/<filename>.mp4` pattern the caller observed — this is just the WP.com-hosted variant of the same CDN.
- Phase 3 decommissions the WordPress.com site. Leaving `videos.files.wordpress.com` references in the Hugo content means every one of those videos breaks the moment the WP.com plan lapses or the videos get garbage-collected.
- 8–10 videos × typical VideoPress encoding (~5–20 MB each) is ~50–200 MB total. Netlify's free tier includes 100 GB bandwidth/month and the repo-size impact is one-time — not a scaling concern.
- Download command:
  ```bash
  curl -L -o "static/videos/<slug>.mp4" "https://videos.files.wordpress.com/<token>/<filename>.mp4"
  ```
  No auth needed for public posts. If a video 403s, it's private — handle manually.
- **Hugo embed**: use a project `layouts/shortcodes/video.html` that renders `<video controls preload="metadata">` with a `<source>` child. The `martignoni/hugo-video` theme component is a drop-in reference (`https://github.com/martignoni/hugo-video/blob/main/layouts/shortcodes/video.html`) but a 15-line custom shortcode in the project tree is simpler and more auditable. [INFERRED from the shortcode source linked above.]
- **Automattic's own `videopress-local-import`** is not useful here:
  > "This tool is designed to 'Move videos from VideoPress to a self-hosted WordPress install.' It converts VideoPress shortcodes to work locally rather than exporting actual MP4 files … The repository shows minimal activity — only 5 commits total with the latest version at 0.5.0 labeled 'Let's kick this off.'" — github.com Automattic repo analysis (`https://github.com/Automattic/videopress-local-import`)
  This is a WordPress plugin for WP→WP migrations; it has no role in a static-site migration and is effectively unmaintained.

#### MH-7. Post-process pandoc output with a documented regex pass for WP-specific residue

Pandoc handles clean HTML correctly. WordPress's HTML is not clean. The post-process script enumerates every known source of residue; each rule is reproducible and testable. The ten-ish rules below are the minimum:

| # | Target | Pattern (Python / `re`) | Replacement |
|---|---|---|---|
| 1 | Gutenberg block comments leaked into rendered output | `r'<!--\s*/?wp:[^>]*-->'` | `''` |
| 2 | `[caption id="…" ...] ... [/caption]` shortcode | `r'\[caption[^\]]*\](.*?)\[/caption\]'` (DOTALL) | → extract `<img>` + caption text, emit `{{< figure src="…" caption="…" >}}` |
| 3 | `[gallery ids="1,2,3"]` shortcode | `r'\[gallery[^\]]*\]'` | → manually re-insert as `{{< gallery >}}` after download of media |
| 4 | `[embed]URL[/embed]` | `r'\[embed\](.*?)\[/embed\]'` | `<\1>` (becomes an autolink) |
| 5 | `[youtube https://…]` | `r'\[youtube\s+(https?://\S+)\]'` | `{{< youtube <id> >}}` (extract ID from URL) |
| 6 | `<figure class="wp-block-image">…</figure>` wrappers | `r'<figure class="wp-block-image[^"]*">(.*?)</figure>'` (DOTALL) | → extract inner `<img>` + optional `<figcaption>`, emit `{{< figure >}}` |
| 7 | `<pre class="wp-block-code">…</pre>` or `[sourcecode lang="…"]` | `r'\[sourcecode\s+(?:lang|language)="([^"]+)"\](.*?)\[/sourcecode\]'` (DOTALL) | `\n```\1\n\2\n```\n` |
| 8 | Jetpack `[python]…[/python]` brush shortcodes | per-language regex, same shape as rule 7 | fenced code block with language |
| 9 | VideoPress `<iframe src="https://videopress.com/embed/…">` | match iframe, extract token | `{{< video src="/videos/<slug>.mp4" >}}` |
| 10 | `wpautop` artifacts (empty `<p></p>`, `<p><br/></p>`, double newlines before fenced blocks) | `r'<p>\s*(?:<br\s*/?>)?\s*</p>'` + `r'\n{3,}'` | `''` and `'\n\n'` |
| 11 | WP image URLs `/wp-content/uploads/YYYY/MM/<file>` | `r'/wp-content/uploads/(\d{4}/\d{2})/([^"\s]+)'` | → if the post is now a bundle, rewrite to bare filename `\2`; otherwise to `/images/\1/\2` |

**Supporting citations for the trickier rules**:

- Rule 2 / 7 approach — convert captions to Hugo's `figure` shortcode, and SyntaxHighlighter shortcodes to fenced code blocks:
  > "WordPress Shortcodes: Converted caption shortcodes to Hugo's native figure shortcode" — Three Portkeys 2026 (`https://www.threeportkeys.com/posts/migrating-my-website-from-wordpress-to-hugo-with-claude-code/`)
  > "The Markdown converter turns SyntaxHighlighter shortcodes into fenced code blocks with the language, the same way existing handling works for Enlighter and Crayon. Shortcodes `[code]`, `[sourcecode]` with a language or lang attribute … and shortcodes named after a brush (`[python]`, `[bash]`, `[php]`, etc.) are all supported for conversion." — wp2hugo PR #311 (`https://github.com/ashishb/wp2hugo/pull/311`)
- Rule 10 — `wpautop` artifacts are a known class of problem:
  > "formatting can come out mangled — bullet lists become flat paragraphs, inline code disappears, and bold text gets concatenated with surrounding words." — shellnetsecurity 2025 WP-to-Hugo migration (`https://blog.shellnetsecurity.com/posts/2025/migrating-to-hugo-journey-static-site-generation/`)
- Rule 11 — the image-rewrite pass is mandatory when moving to page bundles, and it should run *after* the images are already downloaded to the bundle directory, so broken links surface immediately. [INFERRED from the Pawel Grzybek migration script, which did the rename + rewrite as a single pass: `"Writing the script didn't take me longer than 30 minutes, and the script execution took only a few hundred milliseconds."` — pawelgrzybek.com]

**Structure of the Python script** (`scripts/wp_to_hugo_postprocess.py`):

```python
# Pipeline, strictly in this order:
# 1. Strip Gutenberg comments (rule 1)
# 2. Expand Jetpack shortcodes (rules 2–5, 7, 8)
# 3. Collapse WP block wrappers (rule 6)
# 4. Rewrite VideoPress iframes to {{< video >}} shortcode (rule 9)
# 5. Rewrite image URLs to bundle-relative paths (rule 11)
# 6. Normalise whitespace (rule 10) — LAST so earlier rules don't fight it
```

### Recommended

Strongly suggested but has a non-trivial escape hatch.

#### R-1. Language detection: lingua-language-detector + a category-based prior, not pure heuristics

- Lingua is the 2026 winner for short-text detection, which matters for short posts (e.g. Recomendações entries, image-heavy posts with little prose):
  > "Lingua significantly outperforms langdetect and fastText on brief text snippets. According to the benchmarks, for single-word detection (5+ characters), Lingua achieves approximately 90% accuracy in high-accuracy mode, while langdetect and fastText score around 65% and 36% respectively. On word pairs, Lingua reaches ~85% versus langdetect's ~65% and fastText's ~50%." — PyPI lingua-language-detector (`https://pypi.org/project/lingua-language-detector/1.2.0/`)
- For sentence-length posts both lingua and fasttext hit ~98%:
  > "fasttext achieved 0.956 recall for Portuguese and 1.0 recall for English, while langdetect achieved 0.946 for Portuguese and 0.998 for English." — arxiv.org 2312.03789 analysis (`https://arxiv.org/pdf/2312.03789`)
- **Prior from the known-English category**: the caller's spec says category 22748652 and the Product Management category are known to be English-only. Use this as a hard override before invoking lingua — if the post is in one of those categories, tag it `en` and skip detection. For the remaining posts, run lingua on the first 2000 chars (not 500 — the arxiv benchmark shows accuracy climbs smoothly to ~2000 chars and plateaus).
- **Manual review loop**: with 107 posts × ~98% expected accuracy, ~2–3 posts will be mis-labelled. Produce a CSV of `(slug, detected_lang, confidence, first_80_chars)` sorted by ascending confidence; eyeball the bottom 10 entries. Cost: 5 minutes.
- **Why not pure heuristics (categories only)**: the caller's spec acknowledges the WordPress site has no explicit language field. Categories are a proxy, not ground truth — posts drift between categories over 19 years of blogging. Lingua is the ground-truth source; the category prior just reduces lingua's error rate from ~2% to ~1%.
- **Why not manual tagging only**: 107 posts × ~20 seconds-per-post to open and classify = 35 minutes. Lingua-first + 5-minute review = 10 minutes total and is reproducible if we re-run. [INFERRED from the arithmetic above.]

#### R-2. Preserve WordPress URLs *as* the Hugo URLs — avoid Hugo `aliases` except for genuine renames

- Hugo aliases generate client-side meta-refresh HTML, not server-side 301s:
  > "Hugo aliases are not 301 redirects — the aliases front-matter field generates an HTML file containing a meta refresh tag, which is a client-side redirect, not a server-side 301. However, Hugo's alias system effectively creates 301 (permanent) redirects when properly deployed, depending on your hosting configuration." — search result on Hugo aliases migration (`https://discourse.gohugo.io/t/hugo-redirect-from-alias-to-canonical-url/19940`)
- For *this* migration — slug-only WordPress → slug-only Hugo with the permalink config from MH-4 — most post URLs will match exactly, no redirect needed:
  > "Permalink structure remained intact through Hugo's native configuration … every old WordPress URL resolves to the same Hugo URL. No redirects needed, except for one special Unicode slug case requiring an nginx rewrite." — banasiak.com 2026 (`https://blog.banasiak.com/2026/03/hugo-migration/`)
- For the handful that *don't* match exactly (slug sanitisation differences, pre-permalink-change posts), prefer **Netlify `_redirects` 301s** over Hugo aliases. Phase 3 will build this redirect map anyway; threading it through Hugo aliases now duplicates the source of truth.
- **Hugo `aliases` is still the right choice for one case**: when a *Hugo* URL moves (e.g. correcting a typo in a slug six months from now). Then aliases are site-local, live with the content, and get committed in the same PR as the move.

#### R-3. Image handling inside page bundles: use Hugo Markdown and let PaperMod render, not `{{< figure >}}` shortcodes

- Markdown render hooks make the standard `![alt](image.jpg)` syntax render as a proper `<figure>` with caption, lazy-loading, and responsive variants:
  > "Basic markdown image syntax normally becomes a basic image, but a render hook can add responsive images, lazy loading, dimensions, figure markup, or captions that can produce a figure with a caption." — ronaldsvilcins.com 2026 render hooks post (`https://ronaldsvilcins.com/2026/08/23/hugo-render-hooks-explained/`)
- PaperMod does not ship a figure-rendering image render hook by default. The project should add `layouts/_default/_markup/render-image.html` as part of Phase 1 extensions (or the first story of Phase 2). This is the reason to prefer Markdown image syntax over `{{< figure >}}` shortcodes in the converted posts — every post then renders consistently and is portable away from Hugo later.
- The render-hook template:
  ```go-html-template
  {{/* layouts/_default/_markup/render-image.html */}}
  {{- $url := .Destination -}}
  {{- $alt := .Text -}}
  {{- $caption := .Title -}}
  {{- $img := .Page.Resources.GetMatch $url -}}
  <figure>
    {{- if $img -}}
      <img src="{{ $img.RelPermalink }}" alt="{{ $alt }}" loading="lazy">
    {{- else -}}
      <img src="{{ $url }}" alt="{{ $alt }}" loading="lazy">
    {{- end -}}
    {{- with $caption }}<figcaption>{{ . }}</figcaption>{{ end -}}
  </figure>
  ```
  `GetMatch` resolves bundle-local images; the else branch handles external URLs. [INFERRED from the pattern shown in Mijndert Stuij's render-hook write-up (`https://mijndertstuij.nl/posts/hugo-responsive-images-using-render-hooks/`).]
- Use `{{< figure >}}` shortcode only where the Markdown syntax can't express something — e.g. multiple images in a gallery grid where the whole block is custom. Caption-only cases are better served by the `title` attribute of standard Markdown.

#### R-4. Bilingual translation linking: use `translationKey` front matter for the TCC/ClassGenerator pair, file-name convention everywhere else

- Hugo's default bilingual matching is file-path based:
  > "When `translationKey` isn't specified, Hugo matches pages using the logical path (the content path excluding language codes). 'The logical path does not include the language, so pages with the same logical path in different languages are translations of each other.'" — gohugo.io multilingual docs (`https://gohugo.io/content-management/multilingual/`)
- This works fine for pairs that share the same slug across languages (e.g. "sobre"/"about" → both at `/content/pt-br/about/_index.md` and `/content/en/about/_index.md` would NOT match, but both at `content/{lang}/about/_index.md` WOULD match). Since this repo already uses `contentDir = "content/pt-br"` and `contentDir = "content/en"` with matching sub-paths, the default convention is what we want.
- **The exception is the TCC/ClassGenerator pair**, whose caller spec says lives under `Recomendações` in pt-br and under `Recommendations` in en with potentially-different slugs. Force the link with `translationKey`:
  > "To relate translations that have different logical paths, set the `translationKey`." — gohugo.io multilingual docs (same URL)
  > "If you set the `translationKey` field on a page, set it on all of its translations." — same URL (critical caveat)
- **Target front matter** for the TCC pair:
  ```yaml
  # content/pt-br/recomendacoes/projetos/tcc-classgenerator/index.md
  ---
  title: "TCC: ClassGenerator"
  translationKey: tcc-classgenerator
  ---
  ```
  ```yaml
  # content/en/recommendations/projects/tcc-classgenerator/index.md
  ---
  title: "Thesis: ClassGenerator"
  translationKey: tcc-classgenerator
  ---
  ```

#### R-5. wp2hugo as a crosscheck, not the primary tool

- `wp2hugo` (ashishb/wp2hugo) is the most capable WP-to-Hugo migrator in the Go ecosystem:
  > "wp2hugo is a Go-based CLI tool to migrate WordPress websites to Hugo that preserves original URLs, GUIDs, image URLs, code highlights, tables of contents, and WordPress navigation categories, and migrates WordPress custom post types, custom taxonomies, custom fields, and page hierarchy." — github.com/ashishb/wp2hugo analysis
  > "Available flags include: `--download-media`, `--download-all`, `--media-cache-dir`. The tool handles Gutenberg blocks (YouTube embeds, image galleries, tables, footnotes), figure/figcaption, caption/audio/gallery shortcodes, plus custom conversions (Google Maps, GitHub gists)." — same source
- **But its input is a WordPress XML export**, not WP.com MCP output. The caller has explicitly resolved content-fetch via the MCP — introducing wp2hugo means either (a) also exporting the XML and having two sources of truth, or (b) synthesising a WordPress XML from MCP output, which is more code than just running pandoc on the HTML.
- **Recommended role**: run `wp2hugo --source wordpress-export.xml --download-media` **once**, on a WordPress-admin XML export fetched as a one-time sanity check. Compare its output tree against the MCP+pandoc output for 5 random posts. Any pandoc post missing content wp2hugo got right is a bug in our conversion script; log it, patch the regex rules, re-run. This is `wp2hugo` as an oracle, not as the production tool.

### Optional

Situational practices that add real value but can wait until after the first green build.

#### O-1. Content date preservation in front matter

WordPress stores both `date` (publish) and `modified` (last-edit) timestamps. Pandoc throws both away. Capture them explicitly from the MCP post payload:

```yaml
date: 2015-04-23T10:15:00-03:00
lastmod: 2024-09-11T14:02:17-03:00
```

PaperMod reads `date` for post ordering and `lastmod` for the "Updated on" label (if `ShowLastMod` is enabled in `params`). Preserving the original timestamps is essential for a 19-year archive's chronological integrity.

#### O-2. Capture the WordPress post ID for ever-after cross-reference

Add a non-standard front-matter field:

```yaml
wp_post_id: 1234
```

Non-render, but priceless for debugging ("why is this post rendering wrong? — grep for wp_post_id=1234 in the migration logs"). Hugo ignores unknown front-matter keys.

#### O-3. Optimize images at migration time, not on every build

After HEIC conversion and image download, run a one-time pass:

```bash
# Re-encode JPEGs at quality 85 (visually indistinguishable for web, ~30% smaller)
find content -iname '*.jpg' -o -iname '*.jpeg' | \
  xargs -I{} mogrify -quality 85 -strip {}
# Downscale images >1600px wide (no retina phone needs more)
find content -iname '*.jpg' | \
  xargs -I{} mogrify -resize '1600x>' {}
```

This is a one-time Phase 2 cost that pays every build and every page load forever. Hugo's own image pipeline can do this per build, but doing it once at migration time means faster Netlify builds and smaller repos.

#### O-4. Dry-run every conversion pass and diff against a golden fixture

Keep three "golden" posts in a `fixtures/` directory:
1. A long post with code blocks, lists, and images (`/posts/arquitetura-hexagonal/`).
2. A short Recomendações entry with a single figure.
3. The TCC/ClassGenerator pair (tests bilingual linking).

Every time the conversion script changes, re-run all three and `git diff` the output. Regression surface is 100% visible. [INFERRED from the general principle of golden-file testing — no specific WP-to-Hugo source makes this recommendation, but the Pawel Grzybek migration script's 30-minute development cycle implies it; longer feedback loops make iteration miserable.]

### Examples

#### Example 1: Full conversion pipeline, from MCP to committed bundle

```bash
#!/usr/bin/env bash
# scripts/migrate_post.sh <wp_post_id> <slug>
set -euo pipefail
WP_POST_ID="$1"
SLUG="$2"
LANG="${3:-pt-br}"

BUNDLE="content/${LANG}/posts/${SLUG}"
mkdir -p "${BUNDLE}"

# 1. Fetch rendered HTML + metadata from WP.com MCP (done by orchestrator, dumps to /tmp)
HTML="/tmp/wp-${WP_POST_ID}.html"
META="/tmp/wp-${WP_POST_ID}.json"

# 2. Download all images referenced in the HTML, into the bundle
python3 scripts/download_post_media.py --html "${HTML}" --bundle "${BUNDLE}"

# 3. Convert HTML to GFM markdown
pandoc --from html --to gfm --wrap=none --markdown-headings=atx \
  -o "${BUNDLE}/body.md" "${HTML}"

# 4. Post-process: strip WP residue, expand shortcodes, rewrite image paths
python3 scripts/wp_to_hugo_postprocess.py \
  --input "${BUNDLE}/body.md" \
  --meta "${META}" \
  --bundle "${BUNDLE}" \
  --output "${BUNDLE}/index.md"
rm "${BUNDLE}/body.md"

# 5. HEIC → JPEG for any Apple-sourced images that slipped through
find "${BUNDLE}" -iname '*.heic' -print0 | while IFS= read -r -d '' f; do
  heif-convert -q 92 "$f" "${f%.heic}.jpg"
  rm "$f"
done

# 6. Build Hugo locally and fail fast if this post doesn't render
hugo --quiet --minify --destination /tmp/hugo-check
echo "OK: ${LANG}/${SLUG}"
```

#### Example 2: `hugo.toml` permalinks + multilingual block

```toml
# Addition to hugo.toml
[permalinks]
  [permalinks.page]
    posts = "/:slug/"
  [permalinks.section]
    recomendacoes = "/recomendacoes/"

[languages.pt-br]
contentDir = "content/pt-br"
weight     = 1
label      = "Português"
locale     = "pt-BR"

[languages.en]
contentDir = "content/en"
weight     = 2
label      = "English"
locale     = "en-US"
  [languages.en.permalinks]
    [languages.en.permalinks.section]
      recommendations = "/recommendations/"
```

#### Example 3: Target front matter for a migrated post

```yaml
---
title: "Arquitetura Hexagonal em Ruby"
date: 2015-04-23T10:15:00-03:00
lastmod: 2024-09-11T14:02:17-03:00
slug: arquitetura-hexagonal-em-ruby
categories: ["software"]
tags: ["ruby", "arquitetura", "ddd"]
cover:
  image: "cover.jpg"
  alt:   "Hexagonal architecture diagram"
wp_post_id: 1234
translationKey: arquitetura-hexagonal
---
```

#### Example 4: Project video shortcode (`layouts/shortcodes/video.html`)

```go-html-template
{{- /*
  Usage: {{< video src="/videos/<slug>.mp4" poster="/videos/<slug>.jpg" >}}
*/ -}}
{{- $src    := .Get "src"    -}}
{{- $poster := .Get "poster" -}}
<figure class="video">
  <video controls preload="metadata"
         {{- with $poster }} poster="{{ . }}"{{ end }}>
    <source src="{{ $src }}" type="video/mp4">
  </video>
</figure>
```

### Sources

- `https://gohugo.io/configuration/permalinks/` — Hugo permalinks official docs
- `https://gohugo.io/content-management/multilingual/` — Hugo multilingual official docs
- `https://github.com/ashishb/wp2hugo` — wp2hugo migrator, oracle role
- `https://github.com/ashishb/wp2hugo/pull/311` — SyntaxHighlighter shortcode → fenced block conversion
- `https://pawelgrzybek.com/migration-from-single-content-files-to-hugo-page-bundles/` — page-bundle migration script
- `https://blog.banasiak.com/2026/03/hugo-migration/` — 2026 Claude-assisted migration write-up
- `https://www.threeportkeys.com/posts/migrating-my-website-from-wordpress-to-hugo-with-claude-code/` — page-bundle shape + figure shortcode conversion
- `https://blog.shellnetsecurity.com/posts/2025/migrating-to-hugo-journey-static-site-generation/` — wpautop artifacts taxonomy
- `https://starkravingfinkle.org/posts/2026/02/migrating-wordpress-to-hugo-cloudflare/` — URL preservation via CF Workers
- `https://swizec.com/blog/how-to-export-a-large-wordpress-site-to-markdown/` — UnifiedJS vs turndown trade-offs
- `https://webclaw.io/blog/convert-html-to-markdown-2026-guide` — pandoc accuracy benchmark
- `https://leadmagic.io/blog/how-to-convert-html-to-markdown` — turndown addRule() for figure/figcaption
- `https://pypi.org/project/lingua-language-detector/1.2.0/` — lingua short-text accuracy
- `https://arxiv.org/pdf/2312.03789` — langdetect vs fasttext PT/EN benchmark
- `https://howtoconvert.co/blog/how-to-convert-heic-to-jpg-on-linux` — heif-convert vs ImageMagick 2026
- `https://kbmisc.com/blog/convert-heif-images-to-jpg-or-png-on-linux` — HEIC quality settings
- `https://swarmify.com/blog/never-upload-video-to-wordpress-website/` — VideoPress direct URL pattern
- `https://github.com/Automattic/videopress-local-import` — unmaintained, not fit for purpose
- `https://github.com/martignoni/hugo-video/blob/main/layouts/shortcodes/video.html` — reference video shortcode
- `https://mijndertstuij.nl/posts/hugo-responsive-images-using-render-hooks/` — image render hook pattern
- `https://ronaldsvilcins.com/2026/08/23/hugo-render-hooks-explained/` — 2026 render hooks walkthrough
- `https://smartwp.com/wordpress-rest-api/` — WP.com REST API rendered vs raw context
- `https://kinsta.com/blog/headless-wordpress-gutenberg/` — Gutenberg block parsing trade-offs
- `https://github.com/jmooring/hugo-multilingual-example` — multilingual reference repo
