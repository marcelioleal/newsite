---
date: 2026-11-21
agent: aimi-foundation-architect
topic: wordpress-to-hugo-migration-phase-1-foundation
mode: greenfield
---

> **MIT Attribution:** Portions of the Decision Rules this proposal relies on adapt condensed guidance from the `agent-rules-books` project's Clean Architecture and Domain-Driven Design mini-guides, Copyright (c) 2026 Maciej Ciemborowicz, MIT License. They are rewritten as proposal-oriented recommendations, not reproduced verbatim.

## Stack

**Decision:** Hugo v0.170.1 (non-extended) static site generator + PaperMod theme pinned as a `--depth=1` git submodule at `themes/PaperMod/`, deployed to Netlify via `netlify.toml`. Content is Markdown under per-language `contentDir`; UI strings are YAML under `i18n/`; CSS overrides live under `assets/css/extended/`. No Go toolchain, no Node toolchain, no Sass pipeline — pure Hugo.
**Rationale:** Every element is already fixed by `resolvedDecisions` or `stackHints`; this proposal codifies them as the primary stack choice so Clean-Architecture-style layering (which does not apply to a static-site generator) is not forced onto a content project.

## Layering

The Clean Architecture "dependencies point inward" model does not map onto a Hugo static site — there is no runtime business logic, no use-case layer, and no infrastructure to adapter. The project's real layering is a **content/presentation/configuration/distribution** separation, enforced by directory ownership rather than by package imports. Each layer has exactly one place that writes to it, and every subsequent layer reads from the previous without the reverse ever being true.

**Decision:** Four layers, outermost (distribution) at the bottom, innermost (configuration/data) at the top:

1. **Configuration** — `hugo.toml`, `netlify.toml`, `.gitmodules`, `.gitignore`. Declares every structural choice (languages, baseURL, theme, build command, pinned versions). Nothing else reads from the repo root for structural knowledge.
2. **Content** — `content/pt-br/**`, `content/en/**`, `i18n/*.yaml`, `data/**`. Pure authored data: Markdown bodies, front-matter, UI strings, structured datasets. Never imports a layout, never references a CSS class.
3. **Presentation** — `layouts/**`, `assets/css/extended/**`, `static/**`. Consumes Content via Hugo's rendering pipeline; overrides the PaperMod theme only through documented override seams (never by editing `themes/PaperMod/`). Depends on Configuration for language keys and params.
4. **Distribution** — `public/` (generated, gitignored) + Netlify build/deploy context. Pure output; nothing in the repo reads from it.

**Rationale:** Matches Hugo's built-in cascade (site-root beats theme, config drives rendering, content drives output) and gives every future contributor one unambiguous answer to "where does this file go?" — a small, enforceable boundary that pays off every time a translation lands, a style tweaks, or a deploy context is added.

## Folder Layout

```
newsite/
├── .git/                             # created by `git init` (Phase 1)
├── .gitignore                        # ignores /public/, /resources/, .hugo_build.lock
├── .gitmodules                       # created by `git submodule add` (Phase 1)
├── CLAUDE.md                         # human-facing conventions (saved from `## CLAUDE.md Draft`)
├── AGENTS.md                         # agent-facing conventions (saved from `## AGENTS.md Draft`)
├── README.md                         # one-page quickstart (optional Phase 1)
├── hugo.toml                         # flat config (Phase 1 — see decision in researchSummary)
├── netlify.toml                      # build + deploy-context config
├── archetypes/
│   └── default.md                    # front-matter template for `hugo new`
├── assets/
│   └── css/
│       └── extended/
│           └── custom.css            # Phase 1 — minimal-aesthetic overrides
├── content/
│   ├── pt-br/                        # Phase 1 owns: _index.md, about/
│   │   ├── _index.md                 # home (PT-BR)
│   │   └── about/
│   │       └── index.md              # /about/
│   │   # Phase 2 adds: posts/
│   └── en/                           # Phase 1 owns: _index.md, about/
│       ├── _index.md                 # home (EN)
│       └── about/
│           └── index.md              # /en/about/
│       # Phase 2 adds: posts/
├── data/                             # reserved; Phase 2+ may use (e.g. Recomendações)
├── i18n/
│   ├── pt-br.yaml                    # UI strings + orphan-badge string (PT)
│   └── en.yaml                       # UI strings + orphan-badge string (EN)
├── layouts/
│   ├── 404.pt-br.html                # Phase 1 — PT 404 (verbatim path)
│   ├── 404.en.html                   # Phase 1 — EN 404 (verbatim path)
│   └── partials/
│       ├── header.html               # Phase 1 — overrides theme switcher w/ orphan badge
│       ├── extend_head.html          # Phase 1 — theme-safe <head> injection seam
│       └── extend_footer.html        # Phase 1 — theme-safe pre-</body> injection seam
├── static/
│   ├── favicon.ico                   # Phase 1
│   # Phase 2 adds: images/           # migrated WP media
│   # Phase 3 adds: _redirects        # SEO permalink preservation
└── themes/
    └── PaperMod/                     # git submodule, pinned --depth=1; NEVER edit
```

**Phase ownership (verbatim mapping from the spawn prompt):**

| Phase | Owns |
|---|---|
| Phase 1 (this foundation) | `themes/**` (via submodule), `layouts/**`, `content/pt-br/{_index.md, about/}`, `content/en/{_index.md, about/}`, `hugo.toml`, `netlify.toml`, `i18n/*`, `assets/css/extended/*`, `static/*` (except Phase 2/3 additions below). 404s live at `layouts/404.pt-br.html` + `layouts/404.en.html` — **no `content/404.md`, no `layouts/_default/404.html`**. |
| Phase 2 (Content Migration) | `content/pt-br/posts/`, `content/en/posts/`, `static/images/*`. |
| Phase 3 (SEO Preservation & Cutover) | `static/_redirects`. |

**Rationale:** Mirrors Hugo + PaperMod convention exactly, uses per-language `contentDir` (already locked in `resolvedDecisions`), reserves the theme directory as untouched vendored code, and separates each phase's write-scope with zero overlap so Phase 2 and Phase 3 can land additively without re-opening Phase 1 files.

### Submodule, overrides, and 404s — verbatim paths

- **PaperMod submodule location:** `themes/PaperMod/` (site-root relative). Never edited. Updated via `git submodule update --remote --merge` when PaperMod ships a new release.
- **Override seams (all at site root — never under `themes/PaperMod/`):**
  - CSS: `assets/css/extended/custom.css` — bundled + minified with theme CSS automatically.
  - `<head>` injection: `layouts/partials/extend_head.html` — runs after theme CSS, before `</head>`.
  - Pre-`</body>` injection: `layouts/partials/extend_footer.html` — runs at end of `<body>`.
  - Header override (language switcher + orphan badge): `layouts/partials/header.html` — overrides PaperMod's `layouts/_partials/header.html` wholesale. The partial reads `site.Languages` and `.AllTranslations` (per researchSummary and Contract C5/C6) and renders either a translation link or the orphan badge string from `i18n/<lang>.yaml`.
- **404 locations (verbatim):** `layouts/404.pt-br.html` and `layouts/404.en.html`. **Not** `layouts/_default/404.html`. **Not** `content/404.md`. Netlify serves `/404.html` automatically for unmatched paths; no `_redirects` rule needed in Phase 1 for 404 routing (Phase 3 may add per-language redirect rules if `/en/*` unmatched traffic should land on `/en/404.html` specifically).

### Language-switcher partial — what it reads

**Decision:** `layouts/partials/header.html` is the single site-owned partial responsible for rendering the switcher + orphan badge. It iterates `site.Languages`, skips the current `.Lang`, and for each other language branches on `.AllTranslations` (the page-level set that includes the current page) vs `.Translations` (the set excluding the current page): if a translation exists in the other language, link to it; otherwise render `{{ i18n "only_in_language" }}` as a badge. All visible strings come from `i18n/pt-br.yaml` / `i18n/en.yaml` — never hardcoded in the template.
**Rationale:** Keeps every visible string translatable (satisfies the Ubiquitous-Language-in-code rule adapted from the DDD mini-guide), keeps the switcher policy in one file (satisfies the "humble adapter" rule — the partial renders, it does not decide translation strategy outside what Hugo already exposes), and inverts PaperMod's default `site.Home.Translations` behavior (which silently hides orphans) with a single file override.

## Module Template

A Hugo site has no runtime "modules" in the Clean Architecture sense; the directly analogous unit is a **feature page bundle** — one directory under a language root that owns its Markdown body, any colocated assets, and (where translated) its sibling in the other language. The About page is the Phase 1 template.

**Decision:** Every non-home content unit is a **page bundle directory** containing `index.md` (body) and any colocated images, with a matching sibling in the other language sharing a `translationKey` front-matter field when the pages are true translations of each other. Orphan pages (exist in only one language) simply omit the sibling — the switcher's badge logic handles the UX.

**Worked example — the About page bundle (Phase 1):**

```
content/
├── pt-br/
│   └── about/
│       └── index.md                  # front-matter below
└── en/
    └── about/
        └── index.md                  # front-matter below
```

`content/pt-br/about/index.md`:

```yaml
---
title: "Sobre"
date: 2026-11-21
draft: false
translationKey: "about"
---

Markdown body in Portuguese...
```

`content/en/about/index.md`:

```yaml
---
title: "About"
date: 2026-11-21
draft: false
translationKey: "about"
---

Markdown body in English...
```

**Rationale:** Bundle-per-page keeps colocated assets next to the content that references them (Phase 2 migrated WP images follow the same pattern), `translationKey` is the Hugo-idiomatic way to pair translations when filenames differ (`about/` in both is fine; `sobre/` + `about/` would still pair via the shared key), and omitting a sibling is how orphans are expressed — the switcher partial already handles the rest.

## Naming Conventions

**Decision:**

- **Language keys** — lowercase with hyphen: `pt-br`, `en`. Used in config headers (`[languages.pt-br]`), directory names (`content/pt-br/`, `i18n/pt-br.yaml`), and layout suffixes (`404.pt-br.html`). Hugo lowercases these regardless; be explicit.
- **Locale codes (BCP 47)** — mixed case in `languageCode`: `"pt-BR"`, `"en-US"`. Used for `<html lang>`, `hreflang`, Open Graph `og:locale`.
- **Content directories** — kebab-case bundle names matching the final URL slug. About page is `about/` in both languages (not `sobre/` in PT) to keep URLs symmetrical; override via `slug:` front-matter only when the brand demands a translated URL.
- **Content filenames** — bundle entry point is always `index.md`; a non-bundle singleton (e.g. `content/pt-br/_index.md` for the home) uses the `_index.md` list-page name Hugo requires. No other filenames inside `content/<lang>/<bundle>/` need special naming.
- **Front-matter keys** — lowercase, Hugo-standard: `title`, `date`, `draft`, `summary`, `tags`, `translationKey`. No custom keys in Phase 1.
- **i18n string IDs** — snake_case, intent-revealing: `only_in_language`, `language_switcher_label`, `read_more`, `home`, `toc`. Never UI-copy-shaped (no `click_here`, no `the_button_text`).
- **Layout and partial filenames** — lowercase with underscores, matching PaperMod's existing names when overriding: `header.html`, `extend_head.html`, `extend_footer.html`. Per-language layouts use dotted suffix: `404.pt-br.html`, `404.en.html` (Hugo convention; **not** `404_ptbr.html`).
- **CSS class names** — BEM-ish when adding new classes under `assets/css/extended/custom.css`; scope anything new under a top-level `.site-` prefix to avoid colliding with PaperMod's own classes (`.site-header-min`, `.site-lang-badge`).

**Rationale:** Every rule is already enforced by Hugo or PaperMod convention — codifying them here just removes "should this be kebab or snake?" as a future question. The `.site-` CSS prefix is the one project-invented convention and it exists to make a PaperMod upgrade safe (no accidental shadowing of a new upstream class).

## Lint and Format Config

Phase 1 ships four narrow checks — no JS tooling, no Prettier, no Markdown-wide formatter. The site is small and the editorial workflow is direct Markdown; heavy linting adds friction without catching real bugs.

**Decision:**

1. **`.editorconfig`** at repo root — `indent_style = space`, `indent_size = 2`, `end_of_line = lf`, `charset = utf-8`, `trim_trailing_whitespace = true`, `insert_final_newline = true`. Applies to `*.{toml,yaml,yml,html,md,css}`.
2. **`hugo --gc --minify`** in CI (Netlify build) acts as the structural lint — any broken template reference, missing translation, or malformed front-matter fails the build.
3. **No Markdown linter in Phase 1.** Blog post volume is low and the content is prose, not technical documentation. Revisit in Phase 2 if a specific reader experience issue surfaces.
4. **No CSS linter in Phase 1.** `assets/css/extended/custom.css` is expected to stay under ~200 lines; a linter would catch nothing worth catching at that size.

**Rationale:** EditorConfig alone covers the only cross-editor churn a two-person-maximum content workflow actually sees (CRLF-on-Windows, tab-vs-space); Hugo's own build is the real validator, and dragging in Node tooling for a pure-Hugo site would add a `node_modules/` the project otherwise does not need.

## CLAUDE.md Draft

The content below is the ready-to-save draft for the repository's `CLAUDE.md`. Per the artifact-language rule, `featureDescription` and `researchSummary` are authored in English and the project's primary audience language (as stated in the brainstorm and in `resolvedDecisions`) is Portuguese for the final site, but the project's own working documents and code comments default to **English** — `resolvedDecisions` does not mention a prose-language choice for repo docs, and English is the Hugo + PaperMod ecosystem's lingua franca.

```markdown
# CLAUDE.md

Project conventions for the `newsite` (marcelioleal.com) Hugo bilingual migration.

## Prose language
**Decision:** English for repository documentation (`README.md`, `CLAUDE.md`, `AGENTS.md`, code comments, commit messages).
**Rationale:** Default; site content itself is bilingual (pt-BR + en) and lives under `content/`.

## Stack
- Hugo v0.170.1 (non-extended) — pinned in `netlify.toml` via `HUGO_VERSION`.
- PaperMod theme — pinned as a `--depth=1` git submodule at `themes/PaperMod/`. **Never edit `themes/PaperMod/`.**
- Netlify host — one site, staging subdomain `new.marcelioleal.com`.
- No Node, no Go, no Sass. Pure Hugo + Markdown + YAML.

## Layering
Four layers, outermost down:
1. **Configuration** — `hugo.toml`, `netlify.toml`, `.gitmodules`, `.gitignore`.
2. **Content** — `content/pt-br/**`, `content/en/**`, `i18n/*.yaml`, `data/**`.
3. **Presentation** — `layouts/**`, `assets/css/extended/**`, `static/**`.
4. **Distribution** — `public/` (generated, gitignored), Netlify deploy contexts.

Content never imports a layout. Presentation never writes to content. Configuration never references a specific page.

## Override seams (PaperMod)
All at site root — never inside `themes/PaperMod/`:
- `assets/css/extended/custom.css` — minimal-aesthetic CSS overrides (single-column ~720px max-width, system sans-serif).
- `layouts/partials/extend_head.html` — safe `<head>` injection.
- `layouts/partials/extend_footer.html` — safe pre-`</body>` injection.
- `layouts/partials/header.html` — site-owned override of PaperMod's header; renders language switcher + orphan badge.

## Language switcher + orphan badge
`layouts/partials/header.html` iterates `site.Languages`, skips current `.Lang`, and for each other language branches on `.AllTranslations` / `.Translations`: translation link if present, otherwise an "only in PT/EN" badge whose string comes from `i18n/<lang>.yaml`. Never hardcode visible strings in templates.

## 404 pages
Per-language 404 templates at the root of `layouts/`:
- `layouts/404.pt-br.html` (PT)
- `layouts/404.en.html` (EN)

**Not** `layouts/_default/404.html`. **Not** `content/404.md`.

## Content units
Every non-home page is a bundle directory containing `index.md`:
```
content/<lang>/<slug>/index.md
```
Translated siblings share a `translationKey` front-matter value. Orphan pages omit the sibling; the switcher badge handles the UX.

## Naming
- Language keys: `pt-br`, `en` (lowercase, hyphen).
- Locale codes (BCP 47): `pt-BR`, `en-US` (mixed case, in `languageCode` only).
- Content slugs: kebab-case, symmetric across languages when possible.
- i18n string IDs: snake_case (`only_in_language`, `read_more`).
- CSS classes added by this project: prefixed `.site-` to avoid shadowing PaperMod.

## Lint and format
- `.editorconfig` governs whitespace / line endings / final newline.
- `hugo --gc --minify` in Netlify's build is the real validator.
- No Markdown linter, no Prettier, no CSS linter in Phase 1.

## Phase ownership
- **Phase 1 (this foundation)** owns: `themes/**`, `layouts/**`, `content/<lang>/{_index.md, about/}`, `hugo.toml`, `netlify.toml`, `i18n/*`, `assets/css/extended/*`, `static/*` (except below).
- **Phase 2 (Content Migration)** adds: `content/<lang>/posts/`, `static/images/`.
- **Phase 3 (SEO Cutover)** adds: `static/_redirects`.

## Local commands
```
hugo server -D --buildFuture     # local dev with drafts
hugo --gc --minify               # production build (same as Netlify)
git submodule update --remote --merge   # update PaperMod
```
```

## AGENTS.md Draft

The content below is the ready-to-save draft for the repository's `AGENTS.md`. Scope: conventions a spawned coding agent (vs. a human maintainer reading `CLAUDE.md`) needs to know before modifying this repo.

```markdown
# AGENTS.md

Conventions for spawned agents working in the `newsite` repo. Human-facing conventions are in `CLAUDE.md`; this file covers agent-specific guardrails.

## Never edit
- `themes/PaperMod/**` — vendored submodule. Overrides go at site root, never inside the theme.
- `public/**` — generated output; gitignored.
- `.hugo_build.lock`, `resources/**` — Hugo build cache; gitignored.

## When overriding a theme file
1. Copy the theme file from `themes/PaperMod/layouts/<path>` to `layouts/<path>` **at the site root** (drop any `_partials` → `partials` mapping if applicable; Hugo site-root uses `partials/`).
2. Edit only the site-root copy.
3. Never add a `themes/PaperMod/` modification to the diff.

## When adding content
- Every non-home page is a bundle: `content/<lang>/<slug>/index.md`, not `content/<lang>/<slug>.md`.
- Translated pairs share `translationKey:` front-matter.
- Orphans are allowed — do not fabricate a translation to avoid the switcher's badge. The badge is the designed UX.

## When adding a visible string
- Add the string ID to **both** `i18n/pt-br.yaml` and `i18n/en.yaml`.
- Never hardcode visible text in a `.html` template. Call `{{ i18n "id" }}`.
- String IDs are snake_case.

## When modifying the language switcher
- The switcher lives in exactly one file: `layouts/partials/header.html`.
- It reads `site.Languages` and `.AllTranslations` (page-level, not `site.Home.Translations`).
- The orphan badge string comes from `i18n/<lang>.yaml` key `only_in_language`.

## When editing layouts
- Per-language 404s are `layouts/404.pt-br.html` and `layouts/404.en.html` (root of `layouts/`, not under `_default/`).
- Do not create `layouts/_default/404.html` — it is not the Hugo convention.
- Do not create `content/404.md` — it would generate a `/404/` page, not a 404 handler.

## When editing Hugo config
- Phase 1 uses a flat `hugo.toml` at the repo root. Do not promote to `config/_default/` unless a second environment variable actually diverges (per `resolvedDecisions.hugo_config_shape`).
- `HUGO_VERSION` must stay pinned in `netlify.toml`. Do not float.

## When editing Netlify config
- `netlify.toml` lives at the repo root.
- `publish = "public"` is Hugo's default — do not change.
- Deploy previews pass `-b $DEPLOY_PRIME_URL` so cross-page links resolve correctly.

## Phase boundaries (do not cross without the user's scope being Phase 2 or Phase 3)
- Phase 2 additions: `content/<lang>/posts/`, `static/images/`.
- Phase 3 additions: `static/_redirects`.
- Any PR that mixes Phase 1 files with Phase 2/3 scope should be split.

## Non-goals in Phase 1
- No analytics, no third-party scripts, no hosted fonts, no Sass pipeline.
- No Markdown linter, no Prettier, no CSS linter. `.editorconfig` + `hugo --gc --minify` is the full validation story.
```

## Open Questions

None. Every reviewable choice above is stated as a decision with a rationale; genuine unknowns (exact PaperMod release tag to pin, WP permalink shape) are explicitly deferred to Phase 2 by `resolvedDecisions` or by the research artifacts and are not Phase 1 open questions.

---

### Appendix A — `hugo.toml` verbatim block (Phase 1)

```toml
baseURL = "https://new.marcelioleal.com/"
title = "Marcelio Leal"
theme = "PaperMod"

defaultContentLanguage = "pt-br"
defaultContentLanguageInSubdir = false
enableRobotsTXT = true
enableGitInfo = true

[languages]
  [languages.pt-br]
    contentDir   = "content/pt-br"
    languageName = "Português"
    languageCode = "pt-BR"
    weight       = 1
    title        = "Marcelio Leal"
  [languages.en]
    contentDir   = "content/en"
    languageName = "English"
    languageCode = "en-US"
    weight       = 2
    title        = "Marcelio Leal"

[params]
  defaultTheme         = "light"
  disableThemeToggle   = true
  disableLangToggle    = false
  displayFullLangName  = true
  ShowReadingTime      = false
  ShowShareButtons     = false
  ShowBreadCrumbs      = false
  ShowCodeCopyButtons  = true
  ShowPostNavLinks     = false
  ShowAllPagesInArchive = true

[markup.goldmark.renderer]
  unsafe = true

[markup.highlight]
  noClasses = false
```

### Appendix B — `netlify.toml` verbatim block (Phase 1)

```toml
[build]
  command = "hugo --gc --minify"
  publish = "public"

[build.environment]
  HUGO_VERSION = "0.170.1"
  TZ = "America/Sao_Paulo"

[context.production.environment]
  HUGO_ENV     = "production"
  HUGO_BASEURL = "https://new.marcelioleal.com/"

[context.deploy-preview]
  command = "hugo --gc --minify -b $DEPLOY_PRIME_URL"
  [context.deploy-preview.environment]
    HUGO_ENV = "development"

[context.branch-deploy]
  command = "hugo --gc --minify -b $DEPLOY_PRIME_URL"
  [context.branch-deploy.environment]
    HUGO_ENV = "development"
```

### Appendix C — Git + submodule init commands (Phase 1, run once in order)

```bash
cd /Users/marcelioleal/workspace/newsite
git init
git branch -M main
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive

# then create hugo.toml, netlify.toml, .gitignore, .editorconfig, initial content, i18n, overrides
# ...
git add .
git commit -m "chore: phase 1 foundation — Hugo + PaperMod bilingual scaffold"

# connect to the GitHub `newsite` repo (created separately in the GitHub UI):
git remote add origin git@github.com:marcelioleal/newsite.git
git push -u origin main
```

`.gitignore` contents (Phase 1 starter):

```
/public/
/resources/
.hugo_build.lock
.DS_Store
```
