---
date: 2026-11-21
agent: codebase
topic: wordpress-to-hugo-mig-phase-2-content-migration
depth: standard
---

Scope:
content/**
static/images/**
data/**
layouts/**
hugo.toml
scripts/**

## Repository Research Summary

Phase 2 Content Migration lands content into a Hugo site whose Phase 1 foundation is live, clean-building, and intentionally minimal — no custom `_default` templates, no explicit `[permalinks]` block, no `[menu.main]`, no `scripts/` directory, no `static/images/`, and no `.aimi/solutions/`. Phase 2 inherits a bilingual PaperMod install and inherits the theme's `list.html` / `single.html` by default. Every Phase 2 structural decision (Recomendações sub-pages, TCC/ClassGenerator pair, image bundles, WordPress URL preservation, nav expansion) lands in empty space Phase 1 left for it.

## Phase 1 State That Phase 2 Must Respect

### hugo.toml — bilingual contract (unchanged territory)

The entire shipped config (all 32 lines, 18 top-level directives):

```measure
$ grep -c '^[a-z]' /Users/marcelioleal/workspace/newsite/hugo.toml
18
```

Verbatim quotes (contracts Phase 2 consumes):

> `baseURL = "https://new.marcelioleal.com/"` — `hugo.toml:1`
> `title = "Marcelio Leal"` — `hugo.toml:2`
> `theme = "PaperMod"` — `hugo.toml:3`
> `defaultContentLanguage = "pt-br"` — `hugo.toml:4`
> `defaultContentLanguageInSubdir = false` — `hugo.toml:5`
> `[languages.pt-br]` / `contentDir   = "content/pt-br"` / `weight       = 1` / `label        = "Português"` / `locale       = "pt-BR"` — `hugo.toml:7-11`
> `[languages.en]` / `contentDir   = "content/en"` / `weight       = 2` / `label        = "English"` / `locale       = "en-US"` — `hugo.toml:13-17`
> `[params]` with `description`, `images = ["og-default.png"]`, `disableThemeToggle = true`, `ShowBreadCrumbs = false`, `ShowShareButtons = false`, `ShowReadingTime = false`, `ShowCodeCopyButtons = true`, `defaultTheme = "light"`, `ShowPostNavLinks = false` — `hugo.toml:19-28`
> `[params.profileMode]` / `enabled = false` — `hugo.toml:30-31`

Implication for Phase 2:
- The two `contentDir` entries (`content/pt-br`, `content/en`) are the ONLY roots Hugo reads. All migrated WordPress posts land under one of these two trees, never at a single shared `content/posts/`.
- `defaultContentLanguageInSubdir = false` means pt-br is served from `/` (not `/pt-br/`), so a pt-br post at `content/pt-br/posts/foo/index.md` currently resolves to `/posts/foo/`, while an en post at `content/en/posts/foo/index.md` resolves to `/en/posts/foo/`.
- `ShowBreadCrumbs`, `ShowReadingTime`, `ShowShareButtons`, `ShowPostNavLinks` are already all `false`; Phase 2 post pages inherit that without further work.
- `ShowCodeCopyButtons = true` matters for TCC/ClassGenerator (and any other code-heavy post) — code blocks already get the copy button.

### Permalinks — no `[permalinks]` block exists

```measure
$ grep -c permalinks /Users/marcelioleal/workspace/newsite/hugo.toml
0
```

`hugo.toml` contains zero occurrences of `permalinks`, so Hugo falls back to section-based defaults: `content/pt-br/posts/foo/index.md` → `/posts/foo/`, `content/pt-br/recomendacoes/bar/index.md` → `/recomendacoes/bar/`. WordPress pretty permalinks on `marcelioleal.com` are `/<slug>/` (no `/posts/` prefix) [INFERRED — not confirmed by any file on disk; WordPress default permalink shapes and the brainstorm's cutover expectation are the basis]. If Phase 2 wants to preserve WordPress URL shape without redirect noise, an explicit `[permalinks]` block (e.g. `posts = "/:slug/"`, `recomendacoes = "/:slug/"`, `recommendations = "/:slug/"`) is the one hugo.toml edit Phase 2 will need. Deferring this to static/_redirects is also viable and is where Phase 3 is already planning to write — see the handoff's Phase 3 contract line.

### Menu — no `[menu.main]` block; nav items are hardcoded in the partial

```measure
$ grep -c menu /Users/marcelioleal/workspace/newsite/hugo.toml
0
```

Zero menu config in hugo.toml. The only `menu` match in header.html is the HTML/CSS id:

> `    <ul id="menu">` — `layouts/partials/header.html:18`

The About entry is hardcoded in template Go, not driven by `[menu.main]`:

> `{{- with site.GetPage "/about" -}}` / `<a href="{{ .RelPermalink }}">{{ i18n "nav_about" }}</a>` — `layouts/partials/header.html:21-22`

Phase 2 that wants Recomendações in the nav therefore has two paths:
1. Add another hardcoded `<li>` block following the existing About pattern (`site.GetPage "/recomendacoes"` resolves per-language via the content dir; the EN page would be `/recommendations`, which `site.GetPage` cannot look up with a single path — this is the reason a menu-driven approach is cleaner).
2. Introduce `[[languages.pt-br.menu.main]]` and `[[languages.en.menu.main]]` entries in hugo.toml and rewrite the nav partial to `range site.Menus.main`. This supports per-language slugs (`recomendacoes` vs `recommendations`) cleanly, which single-path `site.GetPage` does not.

The planner should pick option 2 — it's the only one that cleanly supports the pt/en slug split for Recomendações and keeps the TCC/ClassGenerator pair reachable from either language's nav if they become promoted items later. [INFERRED recommendation]

### layouts/_default — empty (theme inheritance only)

```measure
$ find /Users/marcelioleal/workspace/newsite/layouts/_default -type f
/Users/marcelioleal/workspace/newsite/layouts/_default/.gitkeep
```

The `layouts/_default/` directory contains exactly one file, a `.gitkeep`. Phase 1 did not author a project-level `list.html` or `single.html`; Hugo reads PaperMod's theme templates directly:

- `themes/PaperMod/layouts/list.html` (117 lines, paginated post entries with `.Summary`, `.Truncated`, cover image, entry-link, post_meta partial, pagination) — `themes/PaperMod/layouts/list.html:1-117`
- `themes/PaperMod/layouts/single.html` (67 lines, post-header + translation_list + post_meta + cover + ToC + content + tags + share) — `themes/PaperMod/layouts/single.html:1-67`

Implication for Phase 2:
- WordPress tags/categories on migrated posts will flow into PaperMod's `post-tags` footer and taxonomy pages for free (`.GetTerms $tags` at `themes/PaperMod/layouts/single.html:50`) IF the migrated front-matter uses `tags:` / `categories:` keys.
- PaperMod's single.html references `.Summary` on list pages — WordPress excerpts should map to `summary:` in the migrated front-matter so the pt-br posts index renders excerpts instead of auto-truncated first paragraphs.
- Post cover images: `themes/PaperMod/layouts/list.html:68` / `themes/PaperMod/layouts/single.html:32` both call `partial "cover.html"` with `.Param "cover"`; Phase 2's image migration should set `cover.image: "image.jpg"` in front-matter alongside page bundles.
- `post_canonical.html` is called on every single page (`themes/PaperMod/layouts/single.html:27`) — this is PaperMod's built-in way to emit `rel=canonical` when a migrated post needs to point at the old WordPress URL during cutover. The project's own `extend_head.html:8` also emits a canonical pointing at `.Permalink` (self). Phase 2 should verify there is no duplicate canonical in the final rendered HTML for a post that sets `canonicalURL` in front-matter.
- The handoff pins override locations:
  > "Overrides restricted to assets/css/extended/, layouts/partials/{header,extend_head,extend_footer}.html, layouts/404*.html" — `.aimi/tasks/wordpress-to-hugo-migration/phase-1-foundation/handoff.md:5`
  Any new project layout files (e.g., `layouts/_default/single.html` to add custom WordPress-era metadata rendering, or `layouts/recomendacoes/list.html` to style recommendations differently) widen that override surface — call this out at planning time rather than drift the contract silently.

### archetypes/default.md — minimal 5-line template

Full file (5 lines, uses TOML `+++` fences):

> `+++` / `title = '{{ replace .Name "-" " " | title }}'` / `date = {{ .Date }}` / `draft = true` / `+++` — `archetypes/default.md:1-5`

Implication for Phase 2:
- The archetype is TOML-fenced (`+++`), but the two shipped content files (`content/pt-br/about/index.md`, `content/en/about/index.md`) use YAML-fenced (`---`) front-matter with keys `title`, `slug`, `translationKey`. Phase 2 will produce dozens/hundreds of files from the WordPress exporter; the exporter output format (YAML, usually) will not match the archetype's TOML style, and `hugo new` is unlikely to be run against the archetype during bulk migration. **The archetype is effectively unused for Phase 2's bulk flow but remains the default for any one-off `hugo new content/pt-br/posts/foo.md`.** If Phase 2 wants new drafts to be bilingual-ready, extend the archetype to include a `translationKey:` stub.
- `translationKey: "about"` is already in use at `content/pt-br/about/index.md:4` and `content/en/about/index.md:3` — this is the shipped mechanism for linking pt-br↔en counterparts whose slugs differ. Phase 2 should use `translationKey: "<some-stable-key>"` on every post that has a bilingual counterpart. The handoff also calls out this exact pattern:
  > "PT About slug=sobre (resolves at /sobre/); EN stays /en/about/. Nav partial uses site.GetPage so slugs resolve per-language" — `.aimi/tasks/wordpress-to-hugo-migration/phase-1-foundation/handoff.md:7`

### Current content/ tree — 4 content markdown files, all placeholders

```measure
$ find /Users/marcelioleal/workspace/newsite/content -type f -name *.md
/Users/marcelioleal/workspace/newsite/content/pt-br/_index.md
/Users/marcelioleal/workspace/newsite/content/en/_index.md
/Users/marcelioleal/workspace/newsite/content/pt-br/about/index.md
/Users/marcelioleal/workspace/newsite/content/en/about/index.md
```

The pt-br and en home pages carry a one-liner tagline — no `mainSections` is set in `[params]`, and PaperMod's `list.html` falls back to `where site.RegularPages "Type" "in" site.Params.mainSections` at `themes/PaperMod/layouts/list.html:44`. With no `mainSections`, the home list renders nothing [INFERRED — not verified against the live build output]. Phase 2 adding posts will need `mainSections = ["posts"]` in `[params]` to make the home page start listing posts.

### Target directories — all absent

```measure
$ ls /Users/marcelioleal/workspace/newsite/content/pt-br/posts /Users/marcelioleal/workspace/newsite/content/pt-br/recomendacoes /Users/marcelioleal/workspace/newsite/content/en/posts /Users/marcelioleal/workspace/newsite/content/en/recommendations /Users/marcelioleal/workspace/newsite/static/images 2>&1 | grep -c 'No such file'
5
```

Every one of the five Phase 2 target directories (`content/pt-br/posts/`, `content/pt-br/recomendacoes/`, `content/en/posts/`, `content/en/recommendations/`, `static/images/`) does not yet exist. Phase 1 intentionally reserved them — the handoff states:
> "Phase 2 content paths: content/pt-br/posts/, content/en/posts/, static/images/ (per the brainstorm roadmap areas) — Phase 2 adds these; Phase 1 reserved the directory placeholders" — `.aimi/tasks/wordpress-to-hugo-migration/phase-1-foundation/handoff.md:59`
(The handoff lists three directories; the Recomendações pair is additionally implied by the Phase 2 scope description the caller provided. The brainstorm roadmap presumably covers it [INFERRED — no .aimi/brainstorms file was consulted in this scope].)

### data/ and scripts/ — absent / empty

```measure
$ find /Users/marcelioleal/workspace/newsite/data -type f
/Users/marcelioleal/workspace/newsite/data/.gitkeep
```

`data/` contains only `.gitkeep` — no data files yet. A `scripts/` directory does not exist at the repo root (not listed in the top-level `ls` output). Phase 2's exporter tooling (per the handoff's Deferred Items line 50: *"WordPress-to-Hugo exporter tool choice (wordpress-to-hugo-exporter plugin, SchumacherFM, or custom WP REST API script). Resolve at Phase 2 start."*) is the natural inhabitant of `scripts/` if the chosen path is a custom WP REST API script.

### .aimi/solutions/ — absent

```measure
$ ls /Users/marcelioleal/workspace/newsite/.aimi/solutions 2>&1 | head -1
ls: /Users/marcelioleal/workspace/newsite/.aimi/solutions: No such file or directory
```

Expected empty state per the caller's hint; no prior solution artifacts to pick up.

## Build Health

```measure
$ hugo --quiet; echo $?
0
```

`hugo --quiet` builds cleanly with exit code 0 against the current Phase 1 state. The `public/` output contains the expected bilingual URL shape (`sobre/` for pt About, `en/about/` for en About, `pt-br/` directory for pt-br root bundles, `en/`, `categories/`, `tags/`, `page/`, `sitemap.xml`, `index.xml` RSS, `404.html`, and the static assets `favicon.ico`, `og-default.png`, `robots.txt`, `_headers`).

```measure
$ ls /Users/marcelioleal/workspace/newsite/public | wc -l
14
```

14 top-level entries in `public/` after the build. Phase 2 can confidently layer content on top of a green-build foundation.

## Contracts Phase 2 Consumes (quoted verbatim)

### Theme submodule pin

> `[submodule "themes/PaperMod"]` / `	path = themes/PaperMod` / `	url = https://github.com/adityatelange/hugo-PaperMod.git` — `.gitmodules:1-3`

Shallow clone (`--depth=1`) per the handoff; Phase 2 must not edit anything under `themes/PaperMod/` and must not pin a different theme commit mid-Phase 2 without re-running the clean-build check above.

### Hugo version pin

> `hugo 0.170.1` — `.tool-versions:1`

Matches `HUGO_VERSION = "0.170.1"` at `netlify.toml:6`. Phase 2 inherits this version; any Hugo-version-sensitive content feature (e.g., new `page.resources` behavior in Hugo 0.171+) must be verified against 0.170.1 docs before adoption. [INFERRED caveat]

### Netlify build command

> `command = "hugo --gc --minify"` — `netlify.toml:2`
> `publish = "public"` — `netlify.toml:3`
> `[context.production.environment]` / `HUGO_ENV = "staging"` — `netlify.toml:16-17`

Phase 2 deploys continue to land on the staging subdomain; `HUGO_ENV=staging` keeps PaperMod's robots meta on `noindex,nofollow` (and `extend_head.html:3-5` double-checks via the `.Site.BaseURL != "https://marcelioleal.com/"` guard).

### Bilingual noindex / canonical / hreflang contract (header)

> `{{ if ne .Site.BaseURL "https://marcelioleal.com/" }}` / `<meta name="robots" content="noindex,nofollow">` — `layouts/partials/extend_head.html:3-4`
> `<link rel="canonical" href="{{ .Permalink }}">` — `layouts/partials/extend_head.html:8`
> `<link rel="alternate" hreflang="{{ .Language.Lang }}" href="{{ .Permalink }}">` + loop over `.AllTranslations` + `x-default` — `layouts/partials/extend_head.html:11-26`
> `<meta property="og:title" …>` + `og:description` + `og:type` (article when `!.IsHome`) + `og:url` + `og:image` + `og:locale` + `og:locale:alternate` — `layouts/partials/extend_head.html:28-37`

Implication: every migrated post automatically gets a self canonical, bilingual hreflang (when a translation exists via `translationKey:`), and OG tags. Phase 2 should NOT add its own `<meta name="robots">`, `<link rel="canonical">`, or OG tags per-post — that would double-emit. `og:type` already flips to `article` for non-home pages, so posts get correct OG typing for free.

### i18n keys already available

> `site_description` / `nav_about` / `only_in_language` / `switch_to_language` / `not_found_title` / `not_found_body` / `back_to_home` — `i18n/pt-br.yaml:1-7` and `i18n/en.yaml:1-7`

Phase 2 that adds a Recomendações nav entry will add a new key (e.g., `nav_recomendacoes` / `nav_recommendations`) to both `i18n/pt-br.yaml` and `i18n/en.yaml`. If Phase 2 renders section landing pages for posts (e.g., "Latest posts" title on `/posts/`), those labels become new i18n entries as well.

### Front-matter conventions (observed, de facto contract)

> `---` / `title: "Sobre"` / `slug: "sobre"` / `translationKey: "about"` / `---` — `content/pt-br/about/index.md:1-5`
> `---` / `title: "About"` / `translationKey: "about"` / `---` — `content/en/about/index.md:1-3`

Phase 2 migrated posts should:
- Use YAML front-matter (`---` fences) — matches the shipped files, mismatches the archetype's TOML `+++`.
- Use `translationKey:` to link pt↔en pairs whenever a translation exists (not every WordPress post has a translation — most will be single-language).
- Use `slug:` when the migrated URL slug must diverge from the directory name (the `sobre` case). For bulk posts migrated at their WordPress slug, the directory name is the slug and no explicit `slug:` is needed.
- Include `date:` from the WordPress export — PaperMod's `post_meta.html` partial uses it in list and single views.
- Include `tags:` / `categories:` from WordPress taxonomies — PaperMod renders them in the single footer at `themes/PaperMod/layouts/single.html:50`.
- Optionally include `summary:` for list-page excerpts (WordPress excerpt → `summary`).
- Optionally include `cover.image:` for the lead image (WordPress featured image) — targets PaperMod's cover partial contract.

## Decisions and Deferrals the Handoff Flags for Phase 2

- **WP-to-Hugo exporter tool choice** — "Resolve at Phase 2 start" per handoff line 50. Options: `wordpress-to-hugo-exporter` plugin, SchumacherFM, custom WP REST API script.
- **GitHub-webhook auto-deploy** — currently manual `netlify deploy --prod --dir=public`; handoff line 49 says "Wire via Netlify UI → Build & deploy → Link repository in Phase 2."
- **Analytics** — still deferred (handoff line 51). Not a Phase 2 blocker.
- **Phase 2 `needs.hugo_site_skeleton`** — already retargeted to `hugo.toml` per handoff line 45 (`roadmap-amend-phase --retarget-needs`). Phase 2 planning should treat `hugo.toml` as the atomic input it consumes.

## Open Questions / Unresolved Items

- **WordPress source inventory** — this research was scoped to the Hugo repo only. The count of posts, pages, images, recomendação sub-pages, and whether TCC/ClassGenerator is one post or two (the brief says "TCC/ClassGenerator pair") is not knowable from `/Users/marcelioleal/workspace/newsite/`. Phase 2 planning needs the WordPress export (or at least a `wp-cli` count) as a separate input.
- **Recomendações sub-pages structure** — single-level (`content/pt-br/recomendacoes/<slug>/index.md`) vs nested (`content/pt-br/recomendacoes/<category>/<slug>/index.md`) is a planning decision; Phase 1 reserved no opinion. [INFERRED — likely single-level given PaperMod's section conventions, but unconfirmed.]
- **URL preservation strategy** — explicit `[permalinks]` in hugo.toml vs. `static/_redirects` at cutover. Phase 3 handoff hints at `static/_redirects` ownership (handoff line 60), which suggests `[permalinks]` in hugo.toml is the cleaner Phase 2 choice. Confirm at planning.
- **Image bundling** — Hugo page bundles (`content/pt-br/posts/foo/index.md` + `content/pt-br/posts/foo/image.jpg`) vs. shared `static/images/`. The caller's scope lists `static/images/` as a Phase 2 target, suggesting the global folder is in-plan. Page bundles would supersede `static/images/` for post-local images — this needs a planning call.
- **`mainSections` param** — currently unset in `[params]`. If Phase 2 wants the home page to render a post list, this needs to become `mainSections = ["posts"]`. If the home stays as the current tagline-only `_index.md` body, no change is needed. [INFERRED — unverified against the current live build.]

## Recommendations for Phase 2 Planning

1. **Treat hugo.toml as a two-edit input**, not frozen: add `[permalinks]` (to preserve WordPress `/<slug>/` shape) and `[[languages.pt-br.menu.main]]` + `[[languages.en.menu.main]]` (to add Recomendações nav without duplicating the hardcoded About pattern). Both edits are small and self-contained.
2. **Keep `layouts/_default/` empty if possible** — PaperMod's list/single are already wired for post tags, translations, canonical, meta. Only override if a WordPress-era metadata field (e.g., a `custom_fields` migration artifact) genuinely needs custom rendering, and if so, respect the handoff's override allowlist.
3. **Extend the archetype** to a bilingual-ready stub (add `translationKey:` and `tags:` placeholders) only if `hugo new` is part of the Phase 2 workflow. For bulk exporter output, the archetype is bypassed.
4. **Lock an exporter choice first** — the exporter determines the front-matter dialect (YAML keys, taxonomy field names, image-reference style) that every subsequent task in Phase 2 must consume. Choosing late means re-authoring the whole content tree.
5. **Add a `summary` field per-post** during migration — the home page and section list pages render `.Summary` / `.Truncated` (`themes/PaperMod/layouts/list.html:84`), and without an explicit `summary:` Hugo auto-truncates the first paragraph, which rarely matches what WordPress served as the excerpt.
6. **Verify the single-canonical story** on at least one migrated post — `themes/PaperMod/layouts/single.html:27` calls `post_canonical.html` AND `layouts/partials/extend_head.html:8` emits a self canonical. Inspect the rendered `<head>` for a post with no `canonicalURL` front-matter and a post with one, to confirm exactly one `rel=canonical` per page.
