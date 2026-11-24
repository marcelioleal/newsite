# newsite — marcelioleal.com

Marcelio Leal's personal site, built with Hugo + PaperMod and deployed to Netlify. Bilingual (pt-BR default, en), single-column light aesthetic inspired by [eltonminetto.dev](https://eltonminetto.dev/).

## Clone

```bash
git clone git@github.com:<you>/newsite.git
cd newsite
git submodule update --init --recursive
```

The `git submodule update --init` step is required — the PaperMod theme is pulled in as a Git submodule at `themes/PaperMod/`.

## Local development

```bash
hugo server -D
```

Open <http://localhost:1313/> (pt-BR) and <http://localhost:1313/en/>. Hugo picks the pinned version from `.tool-versions` (requires [`mise`](https://mise.jdx.dev/) or [`asdf`](https://asdf-vm.com/)).

## Updating the theme

```bash
git submodule update --remote --merge themes/PaperMod
hugo server -D   # eyeball the diff before committing
git add themes/PaperMod
git commit -m "chore: bump PaperMod"
```

Never edit anything under `themes/PaperMod/` — override via `assets/css/extended/*.css`, `layouts/partials/extend_head.html`, `layouts/partials/extend_footer.html`, or by copying a theme layout to the matching site-root path (e.g. `layouts/partials/header.html`).

## Deploy

Netlify auto-deploy is wired to `github.com/marcelioleal/newsite`. Pushing to `main` triggers a production build at <https://new.marcelioleal.com/> (Phase 1 staging subdomain). Pull requests get automatic deploy previews. The build command, Hugo version pin, and context-aware `baseURL` all live in `netlify.toml`.

**Manual deploy (fallback)** — when GitHub-to-Netlify sync is paused (e.g. for a hotfix before pushing):

```bash
HUGO_ENV=staging hugo --gc --minify --baseURL "https://new.marcelioleal.com/"
netlify deploy --prod --dir=public --message "manual deploy: <reason>"
```

## Writing posts

For the one-page cheatsheet on creating a new post (incl. front-matter template and the image workflow), see [`docs/POSTING.md`](docs/POSTING.md).

## Images (Cloudflare R2 CDN)

All post images are served from Cloudflare R2 at `https://pub-51dee957ac3e4a038150048d60e57b9c.r2.dev/...` (bucket: `marcelioleal-images`). The `static/images/` directory is deliberately **not tracked in git** — images never land in the repo.

### Adding a new image

1. Drop the file under `static/images-source/<year>/<month>/<filename>` — this directory is gitignored, so the raw image is only ever local.
2. Commit any post changes and push. The `.github/workflows/upload-images.yml` workflow detects new files under `static/images-source/`, uploads them to R2 with the same subpath as the key, and posts the public CDN URLs in the workflow's step summary.
3. Copy the URL from the summary into your post markdown:
   ```
   ![Caption](https://pub-51dee957ac3e4a038150048d60e57b9c.r2.dev/2026/11/my-photo.jpg)
   ```
4. Optionally delete the local file under `static/images-source/` after upload — the CDN is the source of truth.

### Adding an image locally (no CI round-trip)

Use `./scripts/upload-image.sh <path>`. It uploads via rclone with the same env vars and prints the CDN URL.

```bash
# Requires an .env.r2 file (gitignored) or the env vars exported:
#   R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT, R2_PUBLIC_URL

./scripts/upload-image.sh static/images-source/2026/11/my-photo.jpg
# → outputs: https://pub-51dee957ac3e4a038150048d60e57b9c.r2.dev/2026/11/my-photo.jpg
```

### Bulk one-shot migration (already done)

- `scripts/migrate_images_to_r2.sh` — initial upload of the WordPress migration backlog (123 files / ~52MB, 2026-11-24).
- `scripts/rewrite_images_to_r2.py` — rewrote `/images/*` references in content/ and layouts/ to the CDN URL.

### Future: custom domain

Current serving URL is `pub-XXX.r2.dev` because the user's DNS does not sit on Cloudflare. Phase B of the migration will add a CNAME at the registrar pointing `images.marcelioleal.com` → the R2 bucket, then a single `sed` rewrites all references. The workflow and `upload-image.sh` need `R2_PUBLIC_URL` updated at that point.

## Search (Pagefind)

Search is built by [Pagefind](https://pagefind.app/) as a post-Hugo step. The Netlify build runs:

```bash
hugo --gc --minify && npx pagefind --site public --output-subdir pagefind
```

Locally, `hugo server` alone does NOT build the search index — the search field in the header shows disabled. To test search locally, run the two-step build:

```bash
rm -rf public && hugo --minify && npx pagefind --site public --output-subdir pagefind
# then serve public/ with any static server, e.g.:
npx serve public
```

Pagefind is pinned in `package.json` as a devDependency; Netlify caches it between builds.

## Toolchain

- **Hugo** — pinned to `0.170.1` (non-extended) via `.tool-versions` and `netlify.toml`. Install locally with `brew install hugo`, or `mise install` / `asdf install` once the plugin is set up.
- **Node** — `NODE_VERSION=20` pinned in `netlify.toml` for Pagefind (search index builder).
- **PaperMod** — current `master`, tracked as a shallow submodule.

## Project layout

- `content/pt-br/`, `content/en/` — Markdown content per language.
- `i18n/pt-br.yaml`, `i18n/en.yaml` — UI strings (navigation, orphan badge, 404).
- `layouts/` — site-root overrides (header, extend_head, 404s). Never edit `themes/PaperMod/`.
- `assets/css/extended/custom.css` — minimal aesthetic overrides (Hugo auto-concatenates last).
- `static/` — assets copied verbatim (robots.txt, _headers, favicon, og-default.png).
- `netlify.toml` — build, publish, and per-context environment.

See `.aimi/brainstorms/` and `.aimi/tasks/` for the planning record.

## Phase 1 Foundation artifacts

The three artifacts delivered by Phase 1 (per `.aimi/tasks/wordpress-to-hugo-migration/roadmap.json`):

- `hugo_site_skeleton` — this repository: a PaperMod-based Hugo site with the four-layer folder structure (configuration · content · presentation · distribution), bilingual pt-BR/en i18n, and the minimal single-column light aesthetic. See `hugo.toml`, `layouts/`, `assets/css/extended/custom.css`.
- `netlify_staging_deploy` — the Netlify project `newsite-marcelioleal` connected to `github.com/marcelioleal/newsite`, serving the staging subdomain `new.marcelioleal.com`. See `netlify.toml`.
- `language_switcher` — `layouts/partials/header.html` — the bilingual switcher that renders an `aria-disabled` "only in X" badge driven by i18n strings when a translation is missing.
