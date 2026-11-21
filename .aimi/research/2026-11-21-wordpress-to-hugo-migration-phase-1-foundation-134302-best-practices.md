---
date: 2026-11-21
agent: best-practices
topic: wordpress-to-hugo-migration-phase-1-foundation
depth: deep
---

## Best Practices Research Summary

Scope — Phase 1 Foundation of a bilingual (pt-BR + en) Hugo + PaperMod site, styled minimally after eltonminetto.dev, deployed to Netlify on a staging subdomain. Greenfield workspace at `/Users/marcelioleal/workspace/newsite`. This file resolves the three deferred open questions from the brainstorm (analytics, staging-subdomain name, fonts) and locks the non-obvious conventions for the five other topics requested by the caller.

### Must Have

Non-negotiable practices for Phase 1 — skipping any of these will create rework in Phase 2 or Phase 3.

#### MH-1. Install PaperMod as a pinned git submodule, not a Hugo module

- Source: PaperMod's own installation docs call submodule the recommended method.
  > "Install PaperMod via git submodule — Adds PaperMod as a git submodule and initializes it. The --depth=1 flag limits history. Add --branch v7.0 to pin a specific release." — `https://github.com/adityatelange/hugo-papermod/wiki/Installation`
- The exact three commands PaperMod documents for install + re-clone + upgrade (keep these verbatim in the Phase 1 README):

  ```bash
  git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
  git submodule update --init --recursive       # needed when you reclone your repo
  git submodule update --remote --merge         # to update the theme later
  ```

  Source: `https://github.com/adityatelange/hugo-papermod/wiki/Installation`.
- Rationale for choosing submodule over Hugo module on a solo-maintained personal site: no Go toolchain dependency in Netlify's build image, theme files visible on disk for inspection, trivial fork-and-patch escape hatch. [INFERRED from the codebase-research recommendation at `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:136`.]
- Netlify requirement: enable "Build settings → Git submodules" in the site UI (or let the presence of `.gitmodules` at the repo root enable it implicitly). Without this, Netlify builds succeed structurally but produce a site with no theme files — a silent and confusing failure. [INFERRED from Netlify Hugo deploy conventions cross-checked against the codebase research note at `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:133`.]

#### MH-2. Pin exact `HUGO_VERSION` in `netlify.toml` from the first commit

- Hugo's own documentation ships a canonical `netlify.toml` and pins every build-tool version it needs:
  > "GO_VERSION = \"1.27.4\" · HUGO_VERSION = \"0.170.0\" · NODE_VERSION = \"24.22.3\"" — `https://gohugo.io/host-and-deploy/host-on-netlify/`
- Floating versions are a known Hugo failure mode (minor releases have broken template APIs mid-cycle). The learnings file flags this as a top candidate for future `developer-experience/` solutions: `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-learnings.md:62`.
- The upstream Hugo repo's own `netlify.toml` is the cleanest reference implementation and uses `HUGO_VERSION = "0.167.0"` with `hugo --gc --minify` as the build command (`https://github.com/gohugoio/hugo/blob/master/docs/netlify.toml`). Pick the current stable at Phase-1 start and bump it deliberately.

#### MH-3. Place every customization in site-level files — never edit anything under `themes/PaperMod/`

- Hugo's lookup order gives site files precedence over theme files, which is the mechanism that makes safe customization possible:
  > "If the path of a file in layouts/ exactly matches that of a file in themes/PaperMod/layouts/, then your site will use the file in layouts/ instead of the one in themes/PaperMod/layouts/. Same for assets/." — paraphrased from PaperMod wiki + Hugo lookup-order docs, surfaced by the DEV.to walkthrough at `https://dev.to/johnonlee/customizing-hugo-papermod-without-forking-the-theme-4c98`.
- The three override directories Phase 1 should create (and no others):
  - `assets/css/extended/` — custom CSS; PaperMod auto-bundles everything in this folder.
    > "Place CSS files inside the assets/css/extended folder in the site root; all CSS files there will be bundled into one minimized CSS file." — `https://github.com/adityatelange/hugo-papermod/wiki/FAQs`
  - `layouts/partials/<same-name>.html` — override a specific PaperMod partial (e.g. `header.html`, `translation_list.html`).
  - `layouts/_default/<same-name>.html` — override a full template (e.g. `list.html`, `single.html`, `baseof.html`).
- PaperMod's own FAQ gives the override workflow explicitly: copy the theme file to the matching project path, then edit the copy.
  > "Let's say you wish the list was different. All you have to do is copy the list template: your-site/themes/papermod/layouts/_defaults/list.html — And paste it under your own layouts folder: your-site/layouts/_defaults/list.html" — `https://github.com/adityatelange/hugo-papermod/wiki/FAQs`
- Consequence for upgrades: `git submodule update --remote --merge` becomes a no-conflict operation because PaperMod's own tree is untouched.

#### MH-4. Override `layouts/partials/header.html` to render the "only in PT/EN" orphan-translation badge

PaperMod's shipped `header.html` silently hides the alternate language when a page has no translation. The relevant line that makes this a hide-not-badge contract is in the theme's own source:

> "{{- with site.Home.Translations }} ... {{- range . -}} {{- if ne $lang .Lang }} ..." — `https://github.com/adityatelange/hugo-papermod/blob/master/layouts/_partials/header.html`

That partial iterates `site.Home.Translations` — the set of other-language home pages Hugo has actually built — and renders one `<a>` per element. To meet the Phase-1 success criterion
> "The switcher shows an 'only in PT/EN' badge when a translation is missing instead of hiding or redirecting away." — `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:13`

the override must iterate **`site.Languages`** (every configured language), then branch on whether the current page is translated into that language. Hugo exposes the signals we need directly:

- `.Translations` — pages in *other* languages that share this translation key / content path; excludes the current page. Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/methods/page/Translations.md`.
- `.AllTranslations` — same set as `.Translations` plus the current page; sorted by language weight. Source: `https://github.com/gohugoio/hugodocs/blob/master/content/en/methods/page/AllTranslations.md`.
- `.IsTranslated` — boolean; true when `.Translations` is non-empty.
  > "Reports whether the given page has one or more translations." — `https://github.com/gohugoio/hugodocs/blob/master/content/en/methods/page/IsTranslated.md`

Contract sketch for the override (Source: no code definition found — this is the shape Phase 1 must produce):

```go-html-template
{{/* layouts/partials/header.html (project override) */}}
{{- $current := . -}}
<ul class="lang-menu">
  {{- range $.Site.Languages }}
    {{- $lang := . -}}
    {{- if eq $lang.Lang $current.Lang }}
      {{/* current language — render as plain label, no link */}}
      <li aria-current="true"><span>{{ $lang.LanguageName }}</span></li>
    {{- else }}
      {{- $match := index (where $current.AllTranslations "Lang" $lang.Lang) 0 -}}
      {{- if $match }}
        <li><a href="{{ $match.RelPermalink }}" hreflang="{{ $lang.Lang }}">{{ $lang.LanguageName }}</a></li>
      {{- else }}
        <li class="lang-orphan" aria-disabled="true">
          <span>{{ $lang.LanguageName }}</span>
          <small class="lang-badge">{{ i18n "only_in_language" (dict "Lang" $current.Language.LanguageName) }}</small>
        </li>
      {{- end }}
    {{- end }}
  {{- end }}
</ul>
```

The matching i18n strings land in project-level `i18n/pt-br.yaml` and `i18n/en.yaml` (project-level `i18n/` wins over the theme's copy — Hugo's standard i18n lookup):

```yaml
# i18n/en.yaml
- id: only_in_language
  translation: "only in {{ .Lang }}"

# i18n/pt-br.yaml
- id: only_in_language
  translation: "apenas em {{ .Lang }}"
```

Three subtle contracts behind this pattern, each a trap mentioned in prior research:

1. **Shared `translationKey` or shared relative path** — Hugo only treats two pages as translations when either (a) their content paths match under their language's `contentDir`, or (b) they share a `translationKey` front-matter value. Mismatch produces `.AllTranslations` of length 1 and the badge pattern degrades to "always orphan". Source: `https://discourse.gohugo.io/t/only-link-to-already-translated-content/7334`. The caller's chosen layout `content/pt-br/about.md` + `content/en/about.md` satisfies case (a) by default. For posts that *do* exist in both languages later (Phase 2), front-matter `translationKey` is the cleaner handle.
2. **`defaultContentLanguageInSubdir`** — the brainstorm wants PT-BR at the root and EN at `/en/`. That means `defaultContentLanguage = "pt-br"` + `defaultContentLanguageInSubdir = false`. Hugo docs confirm: `When defaultContentLanguageInSubdir = false, [the default-language pages] live at the root (/article-slug/) while all other languages get a prefix (/en/article-slug/)` — `https://gohugo.io/configuration/languages/`.
3. **Home page is always translated** — Hugo generates `/` and `/en/` from `content/pt-br/_index.md` and `content/en/_index.md`, so the switcher on the home page always has both links. The orphan badge only ever appears on `single` pages, which aligns with the editorial decision in the brainstorm (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:96`) that posts can live in one language only.

#### MH-5. Set `defaultContentLanguage = "pt-br"` + `defaultContentLanguageInSubdir = false`

- Matches the brainstorm's language decisions (PT-BR default; EN served under `/en/`). Source: `.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:26-27`.
- Hugo's documented behavior:
  > "English articles live at the root (/article-slug/) while all other languages get a prefix (/de/article-slug/, /es/article-slug/, etc.)" — paraphrased from `https://gohugo.io/configuration/languages/`.
- Must be decided in Phase 1, not deferred: Phase 3's SEO-preservation story depends on the final URL shape being stable before the WordPress redirect map is authored (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:60-77`).

#### MH-6. `netlify.toml` must branch on deploy context (production vs deploy-preview vs branch-deploy) so `baseURL` is correct everywhere

- Netlify sets `$URL`, `$DEPLOY_PRIME_URL`, and `$DEPLOY_URL` automatically per build. Hugo's own docs recommend passing `--baseURL "${URL}"` directly in the build command so absolute links are correct in every context (`https://gohugo.io/host-and-deploy/host-on-netlify/`).
- The Hugo project's own `netlify.toml` demonstrates the deploy-preview pattern:
  > "Deploy Preview: Runs `npm ls && hugo --gc --minify --buildFuture -b $DEPLOY_PRIME_URL --enableGitInfo`" — `https://github.com/gohugoio/hugo/blob/master/docs/netlify.toml`
- Contract Phase 1 should produce (Source: no code definition found):

  ```toml
  [build]
    publish = "public"
    command = "hugo --gc --minify --baseURL \"${URL}\""

  [build.environment]
    HUGO_VERSION = "0.170.0"          # pin, bump deliberately
    NODE_VERSION = "24.22.3"
    TZ = "America/Sao_Paulo"
    HUGO_ENABLEGITINFO = "true"

  [context.production.environment]
    HUGO_ENV = "production"

  [context.deploy-preview]
    command = "hugo --gc --minify --buildFuture --baseURL \"${DEPLOY_PRIME_URL}\""

  [context.deploy-preview.environment]
    HUGO_ENV = "preview"

  [context.branch-deploy]
    command = "hugo --gc --minify --buildFuture --baseURL \"${DEPLOY_PRIME_URL}\""
  ```

  Two deviations from the Hugo-project reference that fit this project's shape:
  - Drop the `npm ls` prefix — this site has no Node dependencies yet.
  - Replace Oslo with `America/Sao_Paulo` for `.Lastmod` timestamps to match the author's local time (the user's brainstorm is written in pt-BR, this is a courtesy, not a correctness requirement).

#### MH-7. Create a `layouts/404.html` that renders in the visitor's current language

- Netlify auto-serves `/404.html` as the single catch-all for unmatched routes. On a multilingual Hugo site this means `/en/does-not-exist` and `/pagina-inexistente` both hit the same file — so that file must self-detect language (or render both strings and hide one via CSS, which is simpler).
- Hugo generates one `404.html` per language root when it exists in each `contentDir`, but Netlify only serves the top-level one. The pragma: render both strings in `layouts/404.html`, driven by a small inline check:

  ```go-html-template
  {{/* layouts/404.html — contract, Source: no code definition found */}}
  <section>
    <h1>404</h1>
    <p lang="pt-br">Página não encontrada.</p>
    <p lang="en">Page not found.</p>
    <p><a href="/">Início</a> · <a href="/en/">Home</a></p>
  </section>
  ```

  The two paragraphs cost nothing; the bilingual home links let the reader self-recover. This matches the learnings-file hypothesis at `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-learnings.md:68`.

### Recommended

Strongly suggested — one of these per topic is the cleanest default; alternatives listed when the trade-off is real.

#### R-1. Use a system font stack by default; defer self-hosted Inter until there's a concrete reason

This resolves the brainstorm's deferred open question on fonts (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:122`).

Three reasons to default to system sans-serif on this specific site:

1. **The reference site already does.** Live inspection of eltonminetto.dev shows "Body font: Appears to be a sans-serif system font stack (not explicitly named in markup)" — see WebFetch result for `https://eltonminetto.dev/`. Matching the reference's visual tempo is a direct Phase-1 success criterion.
2. **GDPR hygiene is simpler.** Self-hosted Inter is fine. Loading Inter from `fonts.googleapis.com` is not.
   > "In January 2022, the Munich Regional Court ruled that loading Google Fonts from Google's servers violates GDPR, because it transfers the visitor's IP address to Google without consent." — `https://privacychecker.pro/blog/google-fonts-gdpr-compliant`
   A system stack sidesteps the entire category.
3. **Zero FOIT/FOUT; zero ms LCP overhead.**
   > "Sites that self-host fonts with proper preloading see a median LCP improvement of about 180ms versus the Google Fonts CDN." — `https://webinvolved.com/writing/essays/054-self-hosted-fonts/` (via WebSearch summary at `webinvolved.com/guides/web-fonts-performance-self-hosting/`)
   > "GitHub uses system fonts exclusively for the application UI, resulting in zero font-loading overhead, zero FOUT/FOIT, and instant text rendering." — same source.

Recommended stack (ships identically on macOS, iOS, Android, Windows, modern Linux):

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
}
```

Escape hatch — if the brainstorm's "a monospaced treatment for dates/headers" decision (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:111`) is pursued, add a monospace variable only for `<time>` and heading dates:

```css
:root { --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }
time, .post-date { font-family: var(--font-mono); }
```

Both stacks are system-only; no network, no cookies, no consent banner. If Inter later becomes a real design need, self-host the Latin subset (~30 KB per style) with `font-display: swap` and preload the regular weight only:
> "A full Inter file is 200+ KB, while a Latin-only subset is around 30 KB." — `https://webinvolved.com/guides/web-fonts-performance-self-hosting/`.

#### R-2. Skip analytics for Phase 1; revisit after cutover

This resolves the brainstorm's deferred open question on analytics (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:120`).

Ranked options (cheapest → most capable):

1. **No analytics.** Matches the "minimal reference, zero moderation overhead" posture in the brainstorm (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:99`). Zero cost, zero consent banner, zero third-party scripts. Default recommendation for Phase 1.
2. **Netlify Web Analytics — $9/mo/site.** Fully server-side, driven by Netlify's CDN logs.
   > "Netlify Analytics is driven directly from genuine HTTP requests to Netlify's Application Delivery Network and does not require any client-side JavaScript or need to allow third party access to your data." — `https://www.netlify.com/platform/core/analytics/`
   > "Site activity is tracked anonymously without cookies or personally identifying information, making Web Analytics fully GDPR compliant." — `https://docs.netlify.com/manage/monitoring/web-analytics/how-web-analytics-works/`
   One switch in the Netlify UI; no script tag in the site; no consent banner. The right answer if the user ever wants a number but does not want to add a dependency.
3. **Plausible cloud — $19/mo for 100k pageviews.** EU-hosted, cookieless.
   > "Both Plausible and Umami are cookieless tools that avoid GDPR consent requirements entirely by not collecting personal data, meaning no consent banners are required." — `https://ossalt.com/guides/plausible-vs-umami-2026`
   Adds a ~1 KB script tag to the site. Pick if the user wants referrers, search-term reports, and a UTM dashboard.
4. **Umami — self-hosted (free) or cloud ($9/mo for 100k events).** MIT-licensed, Node + PostgreSQL.
   > "Umami at $9/month for 100k events beats Plausible at $19/month for 100k pageviews, and Umami is simpler and MIT-licensed with no cloud tier upsell." — `https://ossalt.com/guides/plausible-vs-umami-2026`
   Self-hosting adds a runtime the author would otherwise not run; cloud is cheaper than Plausible with a similar feature set.
5. **Plausible self-hosted.** Elixir + ClickHouse stack. Powerful, but the heaviest runtime of the four; overkill for a personal blog with ~10 posts (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:94`).

Phase-1 recommendation: **no analytics**. If a signal is wanted later, Netlify Analytics is the one-click option that keeps the site script-free.

#### R-3. Name the staging subdomain `new.marcelioleal.com` and keep DNS at the registrar

This resolves the brainstorm's deferred open question on staging subdomain (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:121`).

Trade-offs between the three candidate names (all are valid subdomain labels):

- **`new.`** — Matches the repo name `newsite` and the verbal framing in the brainstorm ("WordPress-to-Hugo Migration", "newsite" repo). Reads as temporary; obviously retires when `marcelioleal.com` cuts over in Phase 3. [INFERRED from the brainstorm's framing.]
- **`staging.`** — Industry-conventional label.
  > "For development and testing, `staging.example.com` is used as a pre-production environment." — summary of `https://ikarthiks.medium.com/subdomain-naming-conventions-for-environments-services-and-regions-9379c855aaee`
  But this site has no "development" environment — local `hugo server` fills that role — so a "staging" label implies more than exists.
- **`hugo.`** — Technology-leaking. Avoid: the reader of the subdomain shouldn't need to know the stack. [INFERRED from the subdomain-naming best-practice "stick to conventional names" rule — `https://www.darazhost.com/subdomain-names-how-to-choose-and-name-subdomains-well/`.]

Pick `new.marcelioleal.com`. Short, memorable, retires naturally at Phase-3 cutover.

**DNS option comparison** (both work, neither is strictly better):

| Option | What it requires | SSL cert timing |
|---|---|---|
| **External DNS (registrar) + CNAME to Netlify** | One `CNAME new -> <site>.netlify.app` at the registrar (Registro.br, Cloudflare, etc.) | Netlify issues Let's Encrypt once the CNAME resolves; "up to 48 hours" documented, usually minutes. — `https://docs.netlify.com/manage/domains/configure-domains/configure-external-dns/` |
| **Netlify DNS (NS records moved)** | Point `marcelioleal.com`'s nameservers to Netlify's NS set | Faster SSL, simpler Netlify UX, but moves a shared dependency (DNS for the WordPress-era root domain) under the subdomain's provider. |

Recommendation for Phase 1: **keep DNS at the registrar, add a single CNAME**. WordPress still serves the apex `marcelioleal.com` until Phase 3 cutover; the subdomain is a single surgical record that can be removed cleanly if the migration stalls.

Three gotchas worth encoding in the Phase-1 runbook:

1. **CAA records can block Let's Encrypt.** If the registrar has an existing CAA record that whitelists only one issuer (e.g. Comodo), Netlify's Let's Encrypt call fails silently.
   > "CAA records can block Let's Encrypt from issuing certificates, so if you're experiencing provisioning issues, you should verify your CAA records are configured correctly." — `https://answers.netlify.com/t/support-guide-troubleshooting-ssl-certificate-errors/39865`
2. **TTL of the existing record matters.** If a previous CNAME for `new.` exists with a 24h TTL, the first cert issuance waits for that TTL to expire. Drop the TTL to 300s *before* the Phase-1 Netlify switchover begins.
3. **Expect a 5-60 min HTTPS gap on first provisioning.** Documented in the learnings file as a likely incident class (`.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-learnings.md:67`) and confirmed by Netlify's own cert docs.

#### R-4. Single-column, ~720px max-width, one accent color, light background only

Translating eltonminetto.dev's inspection into Phase-1 CSS contracts (all from the WebFetch of `https://eltonminetto.dev/`):

- **Layout**: "Single-column responsive design". Target `max-width: 720px`, centered, ~24px side padding on mobile. (The codebase-research note at `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:207` independently recommends 720px.)
- **Colors**: "Background: White/light · Text: Dark gray/black · Accent: Minimal; links appear in standard blue". Use a single CSS custom property for the accent so the "light personal touch" in the brainstorm (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:111`) is a one-line change later. Example contract:

  ```css
  :root {
    --bg: #ffffff;
    --fg: #1a1a1a;
    --muted: #6b6b6b;
    --accent: #0a66c2;   /* one thing to change to repersonalize */
    --border: #e6e6e6;
  }
  a { color: var(--accent); text-decoration-thickness: 1px; }
  ```

- **Post index**: "Dates appear above each post title (e.g., '04/10/2026') · Bold post titles follow dates · Brief excerpts beneath". The `layouts/_default/list.html` override should render `{{ .Date.Format "02/01/2006" }}` above an `<h2>` title, excerpts optional. The codebase-research note at line 209 anticipates this.
- **Chrome to strip from PaperMod**: cover images, cards, breadcrumbs, share buttons, read-more buttons, dark-mode toggle. PaperMod exposes most of these via `params` flags — the codebase-research note at `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:166-171` has the full list; use that. Use `[params] disableThemeToggle = true` to lock the site to light mode (`.aimi/brainstorms/2026-11-21-wordpress-to-hugo-migration-brainstorm.md:109`).
- **Dark-mode fallback pattern** — if the user later wants a dark-mode toggle, the modern selector pattern on PaperMod is `:root[data-theme='dark']`, not `body.dark`:
  > "Outdated tutorials reference `body.dark` selectors that 'silently do nothing' on current PaperMod. Use instead: `:root[data-theme='dark']` and `@media (prefers-color-scheme: dark)` for no-JS fallbacks." — `https://dev.to/johnonlee/customizing-hugo-papermod-without-forking-the-theme-4c98`

#### R-5. Promote `hugo.toml` to `config/_default/` + `config/staging/` only when a second environment variable diverges

- Phase 1 only has one environment (staging). One flat `hugo.toml` is less ceremony than a `config/<env>/` tree. The codebase-research note explicitly recommends starting flat (`.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:140`).
- The split becomes worth it when at least two of {baseURL, title, params.description, menu entries} differ between staging and production. Phase 1 has only `baseURL` diverging — and Netlify sets that via `--baseURL "${URL}"` in the build command (MH-6), not via config files. So Phase 1 does not need the split.
- Decide to split only in Phase 2 or Phase 3 when `[params]` genuinely diverges (e.g. staging gets `robots: noindex,nofollow` and production does not).

### Optional

Situational — do these if time allows in Phase 1, or defer confidently to later phases.

#### O-1. Add `enableGitInfo = true` to surface `.Lastmod` from git commit times

- Trades one Netlify setting (ensure a shallow clone that still has commit history — Netlify does this by default) for truthful "updated at" timestamps on posts.
- The Hugo-project `netlify.toml` sets `HUGO_ENABLEGITINFO = "true"` in its `[context.production]` only (`https://github.com/gohugoio/hugo/blob/master/docs/netlify.toml`), so deploy previews build faster. Phase 1 can mirror that pattern.
- Defer-safely: has no effect while content is empty; becomes meaningful only after Phase-2 content migration.

#### O-2. Seed `.aimi/solutions/` with one trivial solution at Phase-1 wrap-up

The learnings-research file specifically calls this out (`.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-learnings.md:77`). Writing even one skeleton solution (e.g. `.aimi/solutions/developer-experience/hugo-version-pinning.md`) creates the directory so Phase 2/3 planners don't re-hit the empty-corpus finding.

#### O-3. Add `enableRobotsTXT = true` with a staging-only `robots.txt` that disallows all

- Keeps `new.marcelioleal.com` out of Google's index until cutover. The codebase-research note at line 273 anticipates this.
- Implementation: a single `static/robots.txt` file with `User-agent: *` / `Disallow: /`. Strip or overwrite it in Phase 3's production `config/production/` when the apex cuts over.

#### O-4. Decide permalink format in Phase 1 even though posts land in Phase 2

- Phase 3's redirect-map work depends on stable slug conventions being chosen before content migration (`.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:284`). Setting `[permalinks] posts = "/:slug/"` in Phase 1 is a one-line commit with zero cost, and it removes an otherwise invisible dependency from Phase 2 to Phase 3.

### Examples

Four concrete templates to copy into Phase 1, in dependency order.

#### E-1. `hugo.toml` skeleton (project root)

Shape and param choices from the codebase-research note at `.aimi/research/2026-11-21-wordpress-to-hugo-migration-phase-1-foundation-134302-codebase.md:145-174`, cross-checked against PaperMod's wiki and the current Hugo multilingual docs. Source: no code definition found — Phase 1 produces this.

```toml
baseURL = "https://new.marcelioleal.com/"
title = "Marcelio Leal"
theme = "PaperMod"

defaultContentLanguage = "pt-br"
defaultContentLanguageInSubdir = false

enableRobotsTXT = true
enableGitInfo = true

[permalinks]
  posts = "/:slug/"

[markup.goldmark.renderer]
  unsafe = true

[params]
  defaultTheme = "light"
  disableThemeToggle = true
  ShowReadingTime = false
  ShowShareButtons = false
  ShowBreadCrumbs = false
  ShowPostNavLinks = false
  ShowCodeCopyButtons = true
  displayFullLangName = true

[languages]
  [languages.pt-br]
    languageName = "Português"
    weight = 1
    contentDir = "content/pt-br"
    [languages.pt-br.params]
      description = "Notas pessoais e técnicas."
  [languages.en]
    languageName = "English"
    weight = 2
    contentDir = "content/en"
    [languages.en.params]
      description = "Personal and technical notes."
```

#### E-2. `netlify.toml` with deploy contexts

Values from Hugo's own current `netlify.toml` (`https://gohugo.io/host-and-deploy/host-on-netlify/`) and the deploy-preview pattern from the Hugo repo's `netlify.toml` (`https://github.com/gohugoio/hugo/blob/master/docs/netlify.toml`). Source: no code definition found.

```toml
[build]
  publish = "public"
  command = "hugo --gc --minify --baseURL \"${URL}\""

[build.environment]
  HUGO_VERSION = "0.170.0"
  NODE_VERSION = "24.22.3"
  TZ = "America/Sao_Paulo"

[context.production.environment]
  HUGO_ENV = "production"
  HUGO_ENABLEGITINFO = "true"

[context.deploy-preview]
  command = "hugo --gc --minify --buildFuture --baseURL \"${DEPLOY_PRIME_URL}\""

[context.deploy-preview.environment]
  HUGO_ENV = "preview"

[context.branch-deploy]
  command = "hugo --gc --minify --buildFuture --baseURL \"${DEPLOY_PRIME_URL}\""
```

#### E-3. `layouts/partials/header.html` with orphan-badge language switcher

Full override that renders both languages, disables the current-language link, and shows an "only in …" badge when the alternate language has no translation. Mirrors PaperMod's shipped structure (`https://github.com/adityatelange/hugo-papermod/blob/master/layouts/_partials/header.html`) but swaps the inner `site.Home.Translations` loop for a `site.Languages` loop. Source: no code definition found — Phase 1 produces this.

```go-html-template
{{/* layouts/partials/header.html */}}
<header class="header">
  <nav class="nav">
    <div class="logo">
      <a href="{{ "" | absLangURL }}" aria-label="home">{{ site.Title }}</a>
    </div>
    <ul class="menu">
      {{- range site.Menus.main }}
        <li><a href="{{ .URL | absLangURL }}">{{ .Name }}</a></li>
      {{- end }}

      {{- $current := . }}
      <li class="lang-switcher">
        <ul class="lang-menu">
          {{- range site.Languages }}
            {{- $lang := . }}
            {{- if eq $lang.Lang $current.Lang }}
              <li aria-current="true"><span>{{ $lang.LanguageName }}</span></li>
            {{- else }}
              {{- $match := index (where $current.AllTranslations "Lang" $lang.Lang) 0 }}
              {{- if $match }}
                <li>
                  <a href="{{ $match.RelPermalink }}" hreflang="{{ $lang.Lang }}">
                    {{ $lang.LanguageName }}
                  </a>
                </li>
              {{- else }}
                <li class="lang-orphan" aria-disabled="true"
                    title="{{ i18n "only_in_language" (dict "Lang" $current.Language.LanguageName) }}">
                  <span>{{ $lang.LanguageName }}</span>
                  <small class="lang-badge">
                    {{ i18n "only_in_language" (dict "Lang" $current.Language.LanguageName) }}
                  </small>
                </li>
              {{- end }}
            {{- end }}
          {{- end }}
        </ul>
      </li>
    </ul>
  </nav>
</header>
```

Paired i18n contracts (`i18n/en.yaml` and `i18n/pt-br.yaml`):

```yaml
# i18n/en.yaml
- id: only_in_language
  translation: "only in {{ .Lang }}"

# i18n/pt-br.yaml
- id: only_in_language
  translation: "apenas em {{ .Lang }}"
```

#### E-4. `assets/css/extended/custom.css` minimal stylesheet

Collapses PaperMod's card/cover chrome into a single column matching the eltonminetto.dev inspection. Source: no code definition found — Phase 1 produces this.

```css
:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #6b6b6b;
  --accent: #0a66c2;
  --border: #e6e6e6;
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
}

html { background: var(--bg); color: var(--fg); }
body { font-family: var(--font-body); line-height: 1.6; }

.main, main.main { max-width: 720px; margin: 0 auto; padding: 1.5rem 1rem; }

/* flatten PaperMod cards into a dated list */
.post-entry, article.post-entry { background: transparent; border: 0; padding: 0; margin: 0 0 1.5rem 0; }
.post-entry .entry-cover, .entry-footer, .entry-hint { display: none; }

.post-date, time { font-family: var(--font-mono); color: var(--muted); font-size: 0.9rem; }

a { color: var(--accent); text-decoration-thickness: 1px; }

/* orphan-translation badge */
.lang-orphan { opacity: 0.6; cursor: not-allowed; }
.lang-badge { display: inline-block; margin-left: 0.25rem; font-size: 0.75rem; color: var(--muted); }
```

## Verified

No corrections needed yet — this file carries no `measure` blocks because every quantitative claim is either a cited external string or a configuration contract rather than a repo measurement. If Phase 1 execution surfaces a divergence (e.g. the current Hugo stable is not 0.170.0 at commit time), record the corrected version here rather than editing the body.
