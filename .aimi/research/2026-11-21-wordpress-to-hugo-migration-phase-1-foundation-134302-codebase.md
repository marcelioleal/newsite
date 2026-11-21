---
date: 2026-11-21
agent: codebase
topic: wordpress-to-hugo-migration-phase-1-foundation
depth: standard
---

Scope:
themes/**
layouts/**
content/pt-br/**
content/en/**
hugo.toml
netlify.toml

## Repository Research Summary

### Greenfield Confirmation

`/Users/marcelioleal/workspace/newsite` is a **greenfield workspace**. The only entry below the project root is `.aimi/`.

Top-level entries (count = 1):

```measure
$ find /Users/marcelioleal/workspace/newsite -maxdepth 1 -mindepth 1
/Users/marcelioleal/workspace/newsite/.aimi
```

```measure
$ find /Users/marcelioleal/workspace/newsite -maxdepth 1 -mindepth 1 | wc -l
       1
```

All files currently in the workspace (count = 3, all AIMI planning artifacts):

```measure
$ find /Users/marcelioleal/workspace/newsite -type f
/Users/marcelioleal/workspace/newsite/.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md
/Users/marcelioleal/workspace/newsite/.aimi/tasks/wordpress-to-hugo-migration/roadmap.json.lock
/Users/marcelioleal/workspace/newsite/.aimi/tasks/wordpress-to-hugo-migration/roadmap.json
```

```measure
$ find /Users/marcelioleal/workspace/newsite -type f | wc -l
       3
```

Absent (verified via find across all expected Hugo/CI anchors — the command returns no matches):

```measure
$ find /Users/marcelioleal/workspace/newsite -maxdepth 4 -name hugo.toml -o -name hugo.yaml -o -name hugo.yml -o -name config.toml -o -name netlify.toml -o -name .git -o -name themes -o -name layouts -o -name content -o -name go.mod -o -name package.json
```

Concretely absent: `.git/` (not a git repo yet), `hugo.toml` / `hugo.yaml` / `config.toml`, `netlify.toml`, `themes/`, `layouts/`, `content/`, `static/`, `assets/`, `i18n/`, `data/`, `go.mod`, `package.json`. No existing Hugo tooling, no PaperMod submodule, no Netlify config, no content, and no `node_modules` / build artifacts.

### Guidance Files Found

No `CLAUDE.md` or `AGENTS.md` files exist anywhere under the project root. The only inherited guidance is the brainstorm artifact:

- `/Users/marcelioleal/workspace/newsite/.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md` — brainstorm output containing phase definitions, decisions, and open questions.
- `/Users/marcelioleal/workspace/newsite/.aimi/tasks/wordpress-to-hugo-migration/roadmap.json` — roadmap snapshot (phase scopes and `creates` identities).

Key constraints that Phase 1 planning must honor (quoted from the brainstorm):

> "A Hugo site styled like eltonminetto.dev is live on a staging subdomain with bilingual scaffolding, home, about, and 404 pages." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:8`

> "Staging subdomain serves a single-column, sans-serif, light-background Hugo site inspired by eltonminetto.dev." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:10`

> "Hugo native i18n is configured with content/pt-br and content/en and a visible language switcher." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:11`

> "The switcher shows an \"only in PT/EN\" badge when a translation is missing instead of hiding or redirecting away." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:13`

> "Theme base: PaperMod customized to resemble eltonminetto.dev (single-column, sans-serif, light background)." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:93`

> "Multilingual scaffolding: Hugo native i18n with content/pt-br and content/en mirrored at the structural level (nav, UI strings, menus). Posts themselves do not require pairs." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:95`

Open Phase-1 questions deferred to `/aimi:plan` (all from the brainstorm `## Open Questions` section, lines 117-122):

- Privacy-friendly analytics choice (Plausible / Umami / none).
- Exact staging subdomain name (`new.` / `staging.` / `hugo.` `marcelioleal.com`).
- Font choice: system sans stack vs Inter + JetBrains Mono.

### Architecture & Structure (Target, Not Yet Present)

There is no architecture to observe — the following is the **target layout** Phase 1 must create. All items in this section are [INFERRED] from standard Hugo + PaperMod multilingual conventions, since no on-disk source exists in this repo.

```
newsite/
├── hugo.toml                    # or config/_default/ split (see decision below)
├── netlify.toml                 # build command, publish dir, Hugo version pin
├── .gitignore                   # /public/, /resources/, .hugo_build.lock
├── archetypes/
│   └── default.md               # front-matter defaults for `hugo new`
├── assets/                      # Hugo Pipes inputs (SCSS/JS to be fingerprinted)
│   └── css/
│       └── extended/            # PaperMod convention: overrides land here
├── content/
│   ├── pt-br/
│   │   ├── _index.md            # home (PT)
│   │   ├── about.md             # /pt-br/about/
│   │   └── 404.md               # optional; usually layout-only
│   └── en/
│       ├── _index.md
│       ├── about.md
│       └── 404.md
├── data/                        # (Phase 2 — Recomendações data)
├── i18n/
│   ├── pt-br.yaml               # UI strings (PT)
│   └── en.yaml                  # UI strings (EN)
├── layouts/
│   ├── _default/
│   │   ├── baseof.html          # only override if customizing shell
│   │   ├── single.html
│   │   └── list.html
│   ├── partials/
│   │   ├── header.html          # language switcher lives here (override)
│   │   └── language_menu.html   # or inline in header
│   ├── 404.html
│   └── index.html               # home override if needed
├── static/
│   ├── favicon.ico
│   └── images/                  # (Phase 2 — migrated WP media)
└── themes/
    └── PaperMod/                # git submodule OR Hugo module
```

### Convention Decisions To Make In Phase 1

#### 1. PaperMod install method: submodule vs Hugo module

Two supported paths — both valid, pick one and commit:

- **Git submodule** (`git submodule add https://github.com/adityatelange/hugo-PaperMod themes/PaperMod`) — simplest, no Go toolchain required, matches most PaperMod example sites. Netlify needs `git submodules = true` in build settings (or `--recursive` clone).
- **Hugo module** (`hugo mod init github.com/marcelioleal/newsite` + `module.imports` in config) — requires Go installed in the Netlify build image, lets consumers pin by commit SHA cleanly. [INFERRED]

Recommendation for a solo-maintained personal site: **submodule**. Fewer moving parts, no Go dependency, easy to fork-and-patch if PaperMod simplification work ever drifts from upstream.

#### 2. Config file: `hugo.toml` vs `config/_default/`

The caller's `paths` scope lists `hugo.toml`, so start there. When overrides (menus, params, languages) grow past ~80 lines or environment-specific overrides appear (staging vs production baseURL), **promote to `config/_default/` + `config/staging/` + `config/production/`** so Netlify can set `HUGO_ENVIRONMENT` and swap only the delta. [INFERRED]

A typical bilingual `hugo.toml` skeleton (contract — this is the shape Phase 1 must produce; nothing exists yet, Source: no code definition found):

```toml
baseURL = "https://new.marcelioleal.com/"   # staging value, overridden in prod
title = "Marcelio Leal"
defaultContentLanguage = "pt-br"
defaultContentLanguageInSubdir = false       # PT serves at /, EN at /en/
theme = "PaperMod"

[languages]
  [languages.pt-br]
    languageName = "Português"
    weight = 1
    contentDir = "content/pt-br"
    [languages.pt-br.params]
      description = "..."
  [languages.en]
    languageName = "English"
    weight = 2
    contentDir = "content/en"

[params]
  defaultTheme = "light"
  disableThemeToggle = true   # eltonminetto.dev is light-only
  ShowReadingTime = false
  ShowShareButtons = false
  ShowBreadCrumbs = false
  ShowCodeCopyButtons = true
  ShowPostNavLinks = false
  ShowAllPagesInArchive = true

[markup.goldmark.renderer]
  unsafe = true               # needed for HTML-in-markdown if used
```

#### 3. Content directory convention: `content/pt-br/` and `content/en/`

Two Hugo-native conventions exist for multilingual content:

- **Filename suffix** (`about.pt-br.md` + `about.en.md` in a single `content/`) — convenient but mixes languages per directory.
- **`contentDir` per language** (`content/pt-br/` + `content/en/`) — cleaner for editorial separation; required by the caller's `paths` scope and the brainstorm's language-code decisions (lines 11, 26-27).

> "Hugo native i18n is configured with content/pt-br and content/en and a visible language switcher." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:11`

Note: Hugo expects lowercase BCP-47-ish keys. `pt-br` is a Hugo-level language key; some communities prefer `pt` (with no region) if there is no plan to split pt-PT. The brainstorm explicitly specifies `pt-br`, so honor it. [INFERRED]

#### 4. UI strings: `i18n/pt-br.yaml` + `i18n/en.yaml`

PaperMod ships default `i18n/*.yaml` under its theme dir. The project only needs to supply the two keys the site actually uses that PaperMod does not already translate, plus any custom strings for the orphan-translation badge:

```yaml
# i18n/en.yaml  (example — contract: no code yet, Source: no code definition found)
- id: only_in_language
  translation: "Only available in {{ .Lang }}"
- id: language_switcher_label
  translation: "Language"
```

The PT-BR variant mirrors the same keys. UI-string keys consumed by PaperMod's own templates (`home`, `read_more`, `posts`, `toc`, `code_copy`, `code_copied`, etc.) are the fallback source; project overrides at `i18n/` take precedence over theme defaults. [INFERRED]

#### 5. Layout override strategy (PaperMod)

PaperMod's documented override pattern uses `assets/css/extended/` for CSS. Hugo's cascade means any file placed at `layouts/<same-path-as-theme>` wins. For eltonminetto.dev-style simplification, the likely overrides are:

- `assets/css/extended/custom.css` — remove PaperMod's cover-image / card ornamentation, enforce single-column max-width (~720px), set system sans or Inter stack, remove dark-mode toggles visually. [INFERRED]
- `layouts/partials/header.html` — strip the hamburger, logo, and search; keep only the title + language switcher + minimal nav. [INFERRED]
- `layouts/partials/language_menu.html` (or similar) — custom partial that renders the "only in PT/EN" badge when `.Translations` is empty.
- `layouts/_default/list.html` — dated post-list resembling eltonminetto.dev's blog index (bare date + title, no excerpts).
- `layouts/404.html` — bilingual 404.

The orphan-badge logic uses Hugo's built-in `.AllTranslations` / `.Translations` / `.IsTranslated`:

```go-html-template
{{/* contract sketch — Source: no code definition found */}}
{{ if .IsTranslated }}
  {{ range .Translations }}
    <a href="{{ .Permalink }}">{{ .Language.LanguageName }}</a>
  {{ end }}
{{ else }}
  {{ range $.Site.Languages }}
    {{ if ne .Lang $.Lang }}
      <span class="badge">{{ i18n "only_in_language" }}</span>
    {{ end }}
  {{ end }}
{{ end }}
```

#### 6. `netlify.toml`

Hugo on Netlify needs a pinned version and a cache-friendly build command. Shape (Source: no code definition found):

```toml
[build]
  publish = "public"
  command = "hugo --gc --minify"

[build.environment]
  HUGO_VERSION = "0.138.0"   # pin to a current stable at Phase-1 start
  HUGO_ENV = "production"
  TZ = "America/Sao_Paulo"

[context.deploy-preview.environment]
  HUGO_ENV = "preview"

[context.production]
  command = "hugo --gc --minify --environment production"

[context.staging]
  command = "hugo --gc --minify --environment staging"
```

Submodules checkout is enabled in the Netlify UI (Build & deploy → Dependency management) or implicitly when a `.gitmodules` file is present at repo root.

### Issue Conventions

Not applicable — no git repo, no GitHub project, no prior issues to mine. First commit lands during Phase 1.

### Documentation Insights

No `CONTRIBUTING.md`, no style guide, no coding standards exist. The brainstorm serves as the de facto project charter. Phase-1 planning may optionally seed a minimal root `README.md` documenting local `hugo server -D --buildFuture` usage.

### Templates Found

None. No `.github/`, no `.gitlab/`, no issue or PR templates.

### Implementation Patterns

Nothing to pattern-match in-repo. The patterns the Phase-1 plan should **import** from PaperMod convention and the eltonminetto.dev visual reference are:

- Front-matter keys the site will actually read: `title`, `date`, `draft`, `tags`, `summary`, `translationKey` (to link posts across languages when they do exist as pairs — Phase 2 concern).
- Permalink preservation: Phase 3 depends on Phase 1 setting stable slug conventions now. Set `[permalinks] posts = "/:slug/"` (no date prefix, no language prefix for PT) if WordPress slugs were flat. [INFERRED — needs confirmation against the WP export in Phase 2]
- `enableRobotsTXT = true` + a minimal `static/robots.txt` disallowing the staging host; flip for production via environment config.
- `enableGitInfo = true` so `.Lastmod` is driven by git commit times (only useful after the repo exists).

### Recommendations

1. **Confirm greenfield to the user before any file is created** — there is no accidental overwrite risk, but the user should know the first Phase-1 step is `git init` and scaffolding from zero.
2. **Pick submodule over module for PaperMod** unless the plan already assumes Go on Netlify.
3. **Start with `hugo.toml` flat**; promote to `config/_default/` only when staging-vs-production env delta grows. The caller's `paths` scope already biases toward the flat file.
4. **Resolve the three deferred Phase-1 open questions during `/aimi:plan`** (analytics, staging subdomain, fonts) — none require further codebase research; they're product decisions.
5. **Keep PaperMod un-forked**; place all customization in `assets/css/extended/`, `layouts/partials/`, `layouts/_default/`, and `i18n/` at the project root so PaperMod updates stay a plain `git submodule update --remote`.
6. **Pin HUGO_VERSION in `netlify.toml`** from day one — floating versions have bitten Hugo sites during minor releases.
7. **Deferred for Phase 2/3, flag now so Phase 1 does not paint itself into a corner**: permalink format must be decided before Phase-2 content migration lands, or redirects in Phase 3 become more complex.

### Unresolved

- Exact PaperMod version / commit SHA to pin — out of scope for codebase research; pick latest stable at Phase-1 start.
- Whether WordPress slugs contain language prefixes or date prefixes — determined by the WP export, not available in this repo. Phase 2 will resolve.
- Whether `translationKey` front-matter is needed in Phase 1 — only matters once post pairs exist (Phase 2+).
