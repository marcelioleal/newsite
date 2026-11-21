---
date: 2026-11-21
agent: framework-docs
topic: wordpress-to-hugo-migration-phase-1-foundation
depth: deep
---

## Framework Research Summary

### Summary

Phase 1 of this migration builds a bilingual (pt-BR + en) Hugo site using the PaperMod theme, deployed to Netlify on a staging subdomain. The three technology contracts resolved here are (1) Hugo's native multilingual configuration (per-language `contentDir`, `defaultContentLanguage`, `defaultContentLanguageInSubdir`, and `i18n/<lang>.yaml` translation tables), (2) PaperMod's officially recommended install path (git submodule, minimum Hugo v0.146.0) along with its safe override seams (`assets/css/extended/`, `layouts/partials/extend_head.html`, `layouts/partials/extend_footer.html`), and (3) Netlify's Hugo build configuration (`hugo` command, `public/` publish dir, mandatory `HUGO_VERSION` env var, `[context.*]` sections for branch-aware `baseURL`). The authoritative PaperMod header partial already ships a language switcher driven by `site.Home.Translations` and guarded by `site.Params.disableLangToggle` — overriding it is not required for a minimal bilingual setup, but overriding `layouts/partials/translation_list.html` (which uses `.IsTranslated` and `.Translations`) is the idiomatic place to customize per-page switcher behaviour and handle orphan pages.

**Current pinned versions (as of 2026-11-21):**
- Hugo stable: **v0.170.1** (released 2026-11-17). Note: v0.170.0 **removed the Hugo extended edition** because LibSass was deprecated — `hugo` and `hugo_extended` are now a single distribution.
- PaperMod minimum Hugo: **v0.146.0** (per wiki Installation page).

### Version Information

| Component | Recommended version | Source |
|---|---|---|
| Hugo | v0.170.1 (any post-v0.146.0 works for PaperMod) | [`gohugoio/hugo` releases](https://discourse.gohugo.io/t/hugo-v0-170-1-released/58091) |
| PaperMod | Pin via git submodule `--branch v8.0` (or omit to track `master`) | PaperMod wiki Installation |
| Netlify build image | Default Ubuntu-based image; set `HUGO_VERSION` to pull binary on build | [docs.netlify.com/build/frameworks/framework-setup-guides/hugo](https://docs.netlify.com/build/frameworks/framework-setup-guides/hugo/) |

**Extended-edition note:** Prior to Hugo v0.170.0, Dart-Sass-via-LibSass projects used `hugo_extended`. PaperMod itself does **not** depend on Sass compilation — it ships pre-written CSS under `assets/css/` — so the standard `hugo` binary is sufficient for Phase 1. If you later want Dart Sass, Netlify's build image supports it via a separate install; no `HUGO_VERSION`-equivalent env var is required.

### Key Concepts

**Hugo multilingual model:** Hugo supports two file-layout strategies for multilingual content: (a) **by file name** (`post.en.md`, `post.pt-br.md` in one shared directory) or (b) **by content directory** (`content/en/post.md`, `content/pt-br/post.md`). For this migration the directory strategy is chosen; it requires `contentDir` to be set per language.

**Translation table:** `i18n/<lang>.yaml` (or `.toml`/`.json`) holds UI strings keyed by `id`. These are distinct from content translations. Hugo resolves lookups in order: current language's locale → current language's key → `defaultContentLanguage`'s locale → `defaultContentLanguage`'s key.

**PaperMod install philosophy:** Treat the theme directory as a vendored dependency. Never edit files inside `themes/PaperMod/`. Every custom file goes under the **site root's** `assets/`, `layouts/`, or `static/` directories, which Hugo merges with (and overrides) the theme's equivalent paths.

**Netlify deploy contexts:** Netlify distinguishes `production`, `deploy-preview`, `branch-deploy`, `dev`, and arbitrary named branches. Each gets its own `[context.<name>]` and `[context.<name>.environment]` section in `netlify.toml`. Hugo's `baseURL` is read from the Hugo config but can be overridden per-context via the `HUGO_BASEURL` env var or by passing `-b $URL` to the build command.

### Implementation Guide

#### 1. hugo.toml — minimal bilingual (pt-BR default, en secondary)

```toml
baseURL = "https://staging.example.com/"
title = "Minha Serie"
theme = "PaperMod"

defaultContentLanguage = "pt-br"
defaultContentLanguageInSubdir = false
enableRobotsTXT = true

[languages]
  [languages.pt-br]
    contentDir   = "content/pt-br"
    languageName = "Português"
    languageCode = "pt-BR"
    weight       = 1
    title        = "Minha Serie"
  [languages.en]
    contentDir   = "content/en"
    languageName = "English"
    languageCode = "en-US"
    weight       = 2
    title        = "My Series"

[params]
  defaultTheme       = "auto"
  disableLangToggle  = false
  displayFullLangName = true

[markup.highlight]
  noClasses = false
```

Key choices:

- `defaultContentLanguage = "pt-br"` — Portuguese is served at `/`, English at `/en/`.
- `defaultContentLanguageInSubdir = false` — the default (pt-br) is **not** nested under `/pt-br/`, matching what readers of a Portuguese-first site expect.
- `displayFullLangName = true` — makes the switcher show "Português" / "English" instead of "Pt-Br" / "En".
- Hugo's language key `pt-br` is lowercased in the config; the `languageCode` field carries the full RFC 5646 tag (`pt-BR`) used in `hreflang` attributes and Open Graph locale.

#### 2. i18n directory layout (UI strings)

```
i18n/
├── pt-br.yaml
└── en.yaml
```

PaperMod's `layouts/_partials/translation_list.html` reads the key `translations` — add it to each file. Example `i18n/pt-br.yaml` keys to override from PaperMod's bundled `i18n/en.yaml`:

```yaml
- id: translations
  translation: "Idiomas"
- id: read_time
  translation:
    one: "1 min"
    other: "{{ .Count }} min"
- id: words
  translation:
    one: "palavra"
    other: "{{ .Count }} palavras"
- id: toc
  translation: "Sumário"
- id: home
  translation: "Início"
- id: edit_post
  translation: "Sugerir alteração"
- id: code_copy
  translation: "Copiar"
- id: code_copied
  translation: "Copiado!"
```

Hugo resolves missing keys by falling back to `defaultContentLanguage`'s table, then to the theme's bundled i18n files, so it is safe to leave a key unset.

#### 3. PaperMod install (current recommended: git submodule)

Verbatim from the PaperMod wiki (Method 2, marked "recomended"):

```bash
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive
```

To pin a release instead of tracking `master`, append `--branch v8.0` (or the current latest release tag) to the `submodule add`. For Netlify CI, the build hook must clone submodules — Netlify does this by default when `.gitmodules` is present, but ensure the repo is **not** shallow-cloned without submodule support. The `git submodule update --init --recursive` line is what Netlify's build image runs during checkout.

Update later with:

```bash
git submodule update --remote --merge
```

#### 4. PaperMod override seams (safe customization paths)

All three directories live at the **site root**, not inside `themes/PaperMod/`:

```
<site root>/
├── assets/
│   └── css/
│       └── extended/        # any *.css here is bundled + minified with theme CSS
│           └── custom.css
├── layouts/
│   ├── 404.html              # overrides theme's 404 template
│   ├── partials/
│   │   ├── extend_head.html  # injected into <head> after theme CSS
│   │   └── extend_footer.html # injected at end of <body>
│   └── _default/
│       └── ...               # override any theme layout by matching its path
└── static/
    └── ...                   # copied verbatim to /
```

**Language-switcher customization strategy:** PaperMod's header already renders a language switcher from `site.Home.Translations` (see §Contracts below). For a bilingual site you typically do **not** need to override `layouts/_partials/header.html`. The theme's switcher has two gotchas:

1. It iterates `site.Home.Translations`, so it only lists languages where the **home page** has a translation. If both `content/pt-br/_index.md` and `content/en/_index.md` exist, both languages appear.
2. On non-home pages it still links to the other language's **home**, not the current page's translation, because it uses `site.Home.Translations` rather than `.Translations`.

To make the switcher hop to the current page's translation when one exists (and fall back to the home when it doesn't — the "orphan" case), override `layouts/_partials/header.html` by copying the theme file into `<site root>/layouts/partials/header.html` and replacing the switcher block with a `.Translations`-aware version (see pattern in §Common Issues).

#### 5. Netlify config — minimal netlify.toml

```toml
[build]
  command   = "hugo --gc --minify"
  publish   = "public"

[build.environment]
  HUGO_VERSION = "0.170.1"

[context.production.environment]
  HUGO_ENV     = "production"
  HUGO_BASEURL = "https://staging.example.com/"

[context.deploy-preview.environment]
  HUGO_ENV     = "development"
  # Deploy previews get a unique URL like https://deploy-preview-42--yoursite.netlify.app/
  # Netlify injects $DEPLOY_PRIME_URL; pass it to Hugo via -b in the command below.

[context.deploy-preview]
  command = "hugo --gc --minify -b $DEPLOY_PRIME_URL"

[context.branch-deploy]
  command = "hugo --gc --minify -b $DEPLOY_PRIME_URL"
```

Notes:

- `HUGO_VERSION` is **required** — without it Netlify's build image exits with code 255. Pin to the exact local version returned by `hugo version`.
- `publish = "public"` matches Hugo's default output directory. Do not change unless you also change Hugo's `publishDir`.
- `HUGO_ENV = "production"` toggles PaperMod's `params.env = production` conditionals (Google Analytics, Open Graph, Twitter cards, JSON-LD). In PaperMod's bundled example config this is set via `params.env` in `hugo.toml`, but reading it from the env var at build time is cleaner.
- `DEPLOY_PRIME_URL` is Netlify's per-deploy canonical URL (points to the primary alias for a deploy preview). Passing it via `-b $DEPLOY_PRIME_URL` ensures deploy-preview builds have correct absolute links and asset URLs. Without this, deploy previews use the production `baseURL` from `hugo.toml` and all cross-page links break.

#### 6. 404 page conventions

Hugo renders `/404.html` from a `layouts/404.html` template. For multilingual sites, Hugo supports **per-language 404 templates by file name suffix**:

```
layouts/
├── 404.pt-br.html
├── 404.en.html
└── 404.html          # optional default fallback
```

`layouts/_default/404.html` is **not** the Hugo convention — the 404 template lives at the root of `layouts/`, not inside `_default/`. The `_default/` directory is for single and list templates.

Avoid using `content/404.md` — that creates a regular page at `/404/`, not a template for actual not-found responses. The static-host-side 404 wiring on Netlify is automatic: Netlify serves `/404.html` for any unresolved path with status 404, with no extra `_redirects` rules required.

For per-language 404 behaviour on Netlify (so a user visiting `/en/does-not-exist` lands on the English 404 rather than the pt-BR one), add to `netlify.toml`:

```toml
[[redirects]]
  from = "/en/*"
  to   = "/en/404.html"
  status = 404

[[redirects]]
  from = "/*"
  to   = "/404.html"
  status = 404
```

The default-language redirect must come **last** per Hugo's own server docs.

### Best Practices

1. **Pin HUGO_VERSION explicitly.** Netlify's build image updates its default Hugo version periodically; a missing `HUGO_VERSION` causes drift and build failures.

2. **Vendor PaperMod as a git submodule, not a module** (for Phase 1). Submodules work out of the box on Netlify with no Go toolchain; Hugo modules require `go.mod` and `GO_VERSION` env vars and add deploy-time complexity without benefits for a single-theme setup.

3. **Never edit `themes/PaperMod/`.** Every override belongs at the site root. If a theme file needs to change, copy it to the matching site-root path (e.g. `themes/PaperMod/layouts/_partials/header.html` → `layouts/partials/header.html`). Hugo's layout lookup resolves site-root paths before theme paths.

4. **Use `[params.env] = "production"` or `HUGO_ENV=production`** for live deploys only. PaperMod gates Google Analytics, Open Graph, Twitter Card, and JSON-LD rendering on this value; deploy previews should **not** fire analytics.

5. **Keep `defaultContentLanguageInSubdir = false` for the Portuguese-primary site.** This serves pt-BR at `/` (clean URLs for the primary audience) and en at `/en/`. Setting it to `true` would serve pt-BR at `/pt-br/` and require an alias at `/`.

6. **Match `languageCode` to a valid BCP 47 / RFC 5646 tag** (`pt-BR`, `en-US`). PaperMod and Hugo both use this for `<html lang>`, `hreflang`, and Open Graph `og:locale`. Mismatches silently break SEO cross-language discovery.

7. **For the switcher, override `translation_list.html`, not `header.html`,** when per-page translation links are needed. The theme's header switcher already handles the home-level case; `translation_list.html` is called per post and uses `.IsTranslated` + `.Translations` natively.

### Common Issues

**Issue 1: Language switcher links go to home instead of translated page.**
Cause: PaperMod's header uses `site.Home.Translations` (intentionally — switches site-wide language). Fix: override `layouts/partials/header.html` and replace `site.Home.Translations` with `.Translations` guarded by `.IsTranslated`, falling back to the other language's home when not translated:

```html
{{- $currentLang := .Lang -}}
{{- range site.Languages -}}
  {{- if ne .Lang $currentLang -}}
    {{- $otherLang := . -}}
    {{- $target := "" -}}
    {{- with $.Translations -}}
      {{- range . -}}
        {{- if eq .Lang $otherLang.Lang -}}
          {{- $target = .Permalink -}}
        {{- end -}}
      {{- end -}}
    {{- end -}}
    {{- if not $target -}}
      {{- $target = (printf "/%s/" $otherLang.Lang) -}}
    {{- end -}}
    <a href="{{ $target }}">{{ $otherLang.LanguageName }}</a>
  {{- end -}}
{{- end -}}
```

This pattern — "translation if it exists, else home" — is the idiomatic Hugo way to handle orphan pages (pages that exist in one language only).

**Issue 2: `HUGO_VERSION` not set → Netlify build fails with exit code 255.**
Direct quote from Netlify docs: *"Setting HUGO_VERSION is required to install Hugo on the build image and avoid exit code 255 errors."* Always pin in `netlify.toml`.

**Issue 3: Submodule not cloned on Netlify.**
If the theme directory is empty after a Netlify build, Netlify's checkout step skipped submodules. Ensure `.gitmodules` is committed at the repo root. Netlify auto-initializes submodules when this file is present.

**Issue 4: `displayFullLangName: true` shows empty label.**
PaperMod uses `.Language.Label` for the label when `displayFullLangName` is true, falling back to `.Lang | title`. Hugo exposes the config field as `languageName` (TOML) → `Language.LanguageName` (Go), but PaperMod reads `.Language.Label`, which Hugo aliases to `languageName`. If labels are blank, verify the config uses `languageName` (not `label`) under each `[languages.X]` block.

**Issue 5: pt-BR locale normalization.**
Hugo lowercases language keys. In config: `[languages.pt-br]` (lowercase, hyphen). In `languageCode`: `"pt-BR"` (BCP 47 standard). In filenames: `content/pt-br/`, `i18n/pt-br.yaml`. The output URL subdirectory (when `defaultContentLanguageInSubdir = true`) will be `/pt-br/`.

**Issue 6: Hugo v0.170.0 removed the extended edition.**
If migration docs or older guides reference `HUGO_VERSION_EXTENDED = true` or `hugo_extended`, that env var has no effect from v0.170.0 onward. Just set `HUGO_VERSION = "0.170.1"` and the standard binary includes everything the former extended edition did except LibSass (which was deprecated upstream).

### Contracts

Verbatim contracts from authoritative sources, with citations.

#### C1. Hugo language configuration — full option set

Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/configuration/languages.md`

```toml
defaultContentLanguage = 'de'
defaultContentLanguageInSubdir = true
disableDefaultLanguageRedirect = false

[languages.de]
contentDir = 'content/de'
direction = 'ltr'
disabled = false
label = 'Deutsch'
locale = 'de-DE'
title = 'Projekt Dokumentation'
weight = 1

[languages.en]
contentDir = 'content/en'
direction = 'ltr'
disabled = false
label = 'English'
locale = 'en-US'
title = 'Project Documentation'
weight = 2
```

Field semantics (quoted from the same source):

> `defaultContentLanguage`: (`string`) The project's default language, conforming to the syntax described in RFC 5646. When one or more languages are defined, this value must match one of the defined language keys.
>
> `defaultContentLanguageInSubdir`: (`bool`) Whether to publish the default content language to a subdirectory matching the `defaultContentLanguage`. Default is `false`.
>
> `disableDefaultLanguageRedirect`: (new in 0.140.0) (`bool`) Whether to disable generation of the alias redirect for the default content language.

#### C2. Hugo `.Translations` page method

Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/methods/page/Translations.md`

> Returns all translations of the given page, **excluding the current language**, sorted by language weight then language name.

Return type: `page.Pages` (a collection). Idiomatic usage:

```go-html-template
{{ with .Translations }}
  <ul>
    {{ range . }}
      <li>
        <a href="{{ .RelPermalink }}" hreflang="{{ .Language.Locale }}">
          {{ .LinkTitle }} ({{ or .Language.Label .Language.Name }})
        </a>
      </li>
    {{ end }}
  </ul>
{{ end }}
```

#### C3. Hugo `.IsTranslated` page method

Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/methods/page/IsTranslated.md`

> Reports whether the given page has one or more translations. Returns `bool`.

#### C4. Hugo `lang.Translate` / `i18n` / `T` function

Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/functions/lang/Translate.md`

Signature:

```
lang.Translate KEY [CONTEXT]
```

> Returns a translated string using the translation tables in the i18n directory. It searches the **current language's translation tables**, then those for the **defaultContentLanguage**, and returns an empty string if not found.

Aliases: `T`, `i18n`. Translation-table lookup order: current language locale → current language key → defaultContentLanguage locale → defaultContentLanguage key.

#### C5. PaperMod header language switcher

Source: `https://github.com/adityatelange/hugo-papermod/blob/master/layouts/_partials/header.html`

```html
{{- if (not site.Params.disableLangToggle) }}
    {{- $lang := .Lang}}
    {{- with site.Home.Translations }}
    {{- $separator := or $label_text (not site.Params.disableThemeToggle)}}
    {{- if $separator }}<span class="nav-sep">|</span>{{ end }}
    <ul class="lang-menu">
        {{- range . -}}
        {{- if ne $lang .Lang }}
        <li>
            <a href="{{- .Permalink -}}" title="{{ .Language.Params.languageAltTitle | default (.Language.Label | emojify) | default (.Lang | title) }}"
                aria-label="{{ .Language.Label | default (.Lang | title) }}">
                {{- if (and site.Params.displayFullLangName (.Language.Label)) }}
                {{- .Language.Label | emojify -}}
                {{- else }}
                {{- .Lang | title -}}
                {{- end -}}
            </a>
        </li>
        {{- end -}}
        {{- end}}
    </ul>
    {{- end }}
{{- end }}
```

Controlled by two site params:
- `site.Params.disableLangToggle` — hides the switcher entirely.
- `site.Params.displayFullLangName` — shows `Language.Label` instead of the short language code.

Note the data source is `site.Home.Translations`, not `.Translations` — switcher always points at the other language's home.

#### C6. PaperMod translation list (per-page)

Source: `https://github.com/adityatelange/hugo-papermod/blob/master/layouts/_partials/translation_list.html`

```html
{{- if .IsTranslated -}}
    {{- if (ne .Layout "search") }}
        {{- if or (.Param "author") (.Param "ShowReadingTime") (not .Date.IsZero) }}
            {{- printf "&nbsp;|&nbsp;" | safeHTML -}}
        {{- end -}}
    {{- end -}}
    <span>{{- i18n "translations" | default "Translations" }}:</span>
    <ul class="i18n_list">
        {{- range .Translations }}
        <li>
            <a href="{{ .Permalink }}">
                {{- if (and site.Params.displayFullLangName (.Language.Label)) }}
                {{- .Language.Label | emojify -}}
                {{- else }}
                {{- .Lang | title -}}
                {{- end -}}
            </a>
        </li>
        {{- end }}
    </ul>
{{- end -}}
```

This partial runs per-post and correctly uses `.Translations` (page-level).

#### C7. PaperMod install — recommended method (git submodule)

Source: `https://github.com/adityatelange/hugo-papermod/wiki/Installation` ("Method 2 - Git Submodule (recomended)")

```bash
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive # needed when you reclone your repo (submodules may not get cloned automatically)
```

Pinning a release: append `--branch v7.0` (or newer tag) to the `submodule add`. Update: `git submodule update --remote --merge`.

Minimum Hugo version per the wiki: **Hugo >= v0.146.0**.

#### C8. Netlify `netlify.toml` for Hugo — base

Source: `https://docs.netlify.com/build/frameworks/framework-setup-guides/hugo/`

```toml
[build]
  command = "hugo"
  publish = "public"

[build.environment]
  HUGO_VERSION = "YOUR_HUGO_VERSION"
```

> Setting `HUGO_VERSION` is required to install Hugo on the build image and avoid exit code 255 errors.

Dev defaults from Netlify's framework autodetect: dev command `hugo server -w`, dev port `1313`.

#### C9. Netlify deploy contexts

Source: `https://docs.netlify.com/deploy/deploy-overview/`

```toml
[context.production]
  command = "make production"
  [context.production.environment]
    ACCESS_TOKEN = "super secret"

[context.deploy-preview.environment]
  ACCESS_TOKEN = "not so secret"

[context.branch-deploy]
  command = "make staging"

[context.dev.environment]
  NODE_ENV = "development"

[context.feature]
  command = "make feature"

[context."features/branch"]
  command = "gulp"
```

Note the dotted alternate syntax: `environment = { KEY = "value" }` inline, or nested `[context.<name>.environment]` block.

#### C10. Hugo 404 template

Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/templates/404.md`

Single-language: place at `layouts/404.html`:

```go-html-template
{{ define "main" }}
  <h1>404 Not Found</h1>
  <p>The page you requested cannot be found.</p>
  <p>
    <a href="{{ site.Home.RelPermalink }}">
      Return to the home page
    </a>
  </p>
{{ end }}
```

Multi-language layout (file-name suffix pattern):

```
layouts/
├── 404.de.html
├── 404.en.html
└── 404.fr.html
```

**Not** `layouts/_default/404.html` — the template lives at the root of `layouts/`.

### References

- Hugo configuration → languages: https://gohugo.io/configuration/languages/
- Hugo content management → multilingual: https://gohugo.io/content-management/multilingual/
- Hugo methods → `.Translations`: https://gohugo.io/methods/page/translations/
- Hugo methods → `.IsTranslated`: https://gohugo.io/methods/page/istranslated/
- Hugo functions → `lang.Translate`: https://gohugo.io/functions/lang/translate/
- Hugo templates → 404: https://gohugo.io/templates/404/
- Hugo hosting → Netlify: https://gohugo.io/hosting-and-deployment/hosting-on-netlify/
- PaperMod wiki → Installation: https://github.com/adityatelange/hugo-PaperMod/wiki/Installation
- PaperMod wiki → FAQs (custom CSS, extend_head, extend_footer): https://github.com/adityatelange/hugo-PaperMod/wiki/FAQs
- PaperMod wiki → Features: https://github.com/adityatelange/hugo-PaperMod/wiki/Features
- PaperMod source → `layouts/_partials/header.html`: https://github.com/adityatelange/hugo-PaperMod/blob/master/layouts/_partials/header.html
- PaperMod source → `layouts/_partials/translation_list.html`: https://github.com/adityatelange/hugo-PaperMod/blob/master/layouts/_partials/translation_list.html
- Netlify → Hugo build settings: https://docs.netlify.com/build/frameworks/framework-setup-guides/hugo/
- Netlify → File-based configuration: https://docs.netlify.com/build/configure-builds/file-based-configuration/
- Netlify → Deploy contexts: https://docs.netlify.com/deploy/deploy-overview/
- Netlify → Environment variables: https://docs.netlify.com/build/environment-variables/get-started/
- Hugo v0.170.1 release notes: https://discourse.gohugo.io/t/hugo-v0-170-1-released/58091
- Hugo v0.170.0 release (extended-edition removal): https://discourse.gohugo.io/t/hugo-v0-170-0-released/57913
