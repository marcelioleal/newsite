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

## Toolchain

- **Hugo** — pinned to `0.170.1` (non-extended) via `.tool-versions` and `netlify.toml`. Install locally with `brew install hugo`, or `mise install` / `asdf install` once the plugin is set up.
- **Node** — not required; this site has no JavaScript build step.
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
