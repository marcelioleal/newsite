---
date: 2026-11-22
topic: polish-and-pendings
phases:
  - id: 2.1
    name: Pending Tech Fixes
    slug: pending-tech-fixes
    goal: Technical debt from Phase 2 migration is resolved — the 139MB video self-hosted on YouTube, broken VideoPress embeds replaced, external images no longer proxied through Jetpack, and GitHub pushes auto-deploy via Netlify without manual CLI.
    successCriteria:
      - The 139MB video (static/videos/20250201095728000070.mp4) is published on a YouTube channel owned by the site owner and referenced via a YouTube iframe embed in its originating post.
      - Every WordPress post that originally embedded a VideoPress iframe either plays a self-hosted video via the HTML5 video tag pointing at /videos/<file>, or embeds a YouTube video — with no empty iframe divs remaining in the rendered HTML.
      - External images proxied through i0.wp.com (Giphy, Medium, softwarelivre.org and similar) are either downloaded and self-hosted under static/images/external/, or replaced inline with the original source URL — the staging site no longer depends on Jetpack for any image.
      - Pushing to main on github.com/marcelioleal/newsite triggers an automatic Netlify production deploy without a manual netlify deploy invocation.
    dependsOn:
      - 2
    creates:
      - identity: youtube_video_embeds
        description: YouTube iframe embeds (or self-hosted video tags) replacing the empty VideoPress iframe divs in migrated posts
      - identity: netlify_github_autodeploy
        description: Netlify site linked to the GitHub repo via OAuth webhook so push → auto-build
    needs:
      - identity: content/pt-br/posts
        description: Migrated post bundles from Phase 2 whose empty iframes need swapping
    areas:
      - content/**
      - scripts/**
      - netlify.toml
  - id: 2.2
    name: Content Completion
    slug: content-completion
    goal: WordPress pages left behind in Phase 2 are migrated into the Hugo site, replacing Phase 1 placeholder content with real WordPress authoring and filling in the Popular Posts and Artigos Tech pages the roadmap always intended to carry over.
    successCriteria:
      - content/pt-br/about/index.md replaces the Phase 1 placeholder with the migrated content of WordPress page 185 (Sobre Mim).
      - content/en/about/index.md replaces the Phase 1 placeholder with the migrated content of WordPress page 193 (About me).
      - Popular Posts PT (WP page 226) is migrated to content/pt-br/posts-populares/_index.md and linked in the nav or home page.
      - Popular Posts EN (WP page 237) is migrated to content/en/popular-posts/_index.md and linked in the nav or home page.
      - WordPress page 1606 (Artigos Tech) is migrated to content/pt-br/recomendacoes/artigos-tech/_index.md, replacing the Phase 2 branch-bundle placeholder that resolved from the WP child relationship.
    dependsOn:
      - 2
    creates:
      - identity: content/pt-br/about/index.md
        description: Real Sobre Mim bio replacing the Phase 1 placeholder, migrated from WP page 185
      - identity: content/en/about/index.md
        description: Real About me bio replacing the Phase 1 placeholder, migrated from WP page 193
      - identity: content/pt-br/posts-populares
        description: Popular Posts PT branch bundle migrated from WP page 226
      - identity: content/en/popular-posts
        description: Popular Posts EN branch bundle migrated from WP page 237
    needs:
      - identity: scripts/wp_to_hugo.py
        description: Migration script from Phase 2 reused for the remaining pages
    areas:
      - content/**
  - id: 2.3
    name: Design Polish (dark-default theme)
    slug: design-polish
    goal: The site ships with a dark theme by default and a light toggle, extending the Phase 1 minimal single-column aesthetic into a dark palette that reads editorial and intentional — not generic dark-mode.
    successCriteria:
      - disableThemeToggle in hugo.toml [params] is set to false, exposing PaperMod's theme toggle in the header.
      - defaultTheme in hugo.toml [params] is set to "dark".
      - assets/css/extended/custom.css defines a cohesive dark palette (background, foreground, muted, accent) that preserves the ~720px single-column layout, system font stack, and dates-above-titles typography from Phase 1.
      - The language switcher's only-in-X aria-disabled badge and the dated post-list on the home page both maintain WCAG AA contrast (≥4.5:1) in dark mode.
      - Both static/og-default.png and static/favicon.ico adapt or are reconsidered for dark-default rendering.
    dependsOn:
      - 2
    creates:
      - identity: assets/css/extended/custom.css
        description: Extended CSS with a dark-default palette and a light override triggered by PaperMod's data-theme attribute
    needs:
      - identity: hugo.toml
        description: Hugo config with the Phase 1 aesthetic params that this phase amends (disableThemeToggle=false, defaultTheme=dark)
    areas:
      - assets/**
      - layouts/**
      - hugo.toml
  - id: 2.4
    name: Features — Search, RSS, Analytics
    slug: features-search-rss-analytics
    goal: The site has static search, discoverable RSS feeds, and privacy-friendly analytics that count both humans and bot traffic — all free or near-free, no cookie banner, GDPR-safe.
    successCriteria:
      - Pagefind is wired into the Hugo build; a search field in the header returns ranked results across all posts and pages.
      - An RSS link is visible in the header or footer pointing at /index.xml (PT) and /en/index.xml (EN).
      - GoatCounter free-tier is wired via a 2KB inline script in layouts/partials/extend_head.html; visits are visible at goatcounter.com dashboard, including bot classifications.
      - The analytics script loads only in production/staging (not local dev) and respects Do-Not-Track.
      - CSP in static/_headers is updated to allow the GoatCounter script origin without compromising the strict baseline.
    dependsOn:
      - 2
    creates:
      - identity: pagefind_index
        description: Pagefind static search index built at Hugo build time and served from /pagefind/
      - identity: goatcounter_integration
        description: GoatCounter analytics script in layouts/partials/extend_head.html with bot visibility
    needs:
      - identity: layouts/partials/extend_head.html
        description: Head partial from Phase 1 where the analytics script and search toggle land
    areas:
      - layouts/**
      - static/**
      - hugo.toml
---

# Pre-Cutover Polish and Pending Fixes

## What We're Building

Between Phase 2 (Content Migration, complete) and Phase 3 (SEO Cutover, deferred) we are inserting four smaller sub-phases to resolve technical debt from the content migration, complete the content WordPress still carries, polish the visual design, and add the features the brainstorm's original roadmap deferred. The cutover is deliberately held back until the new staging site is "melhor, seguro, e de acordo com o meu gosto" — the owner's own gate.

## Why This Approach

Three alternatives considered:

- **Pendings-first, then polish (chosen)** — Resolve the technical debt (videos, iframes, Jetpack proxies, auto-deploy) before touching design. This keeps the polish work from compounding on top of known bugs and gives the owner an empty debt column before investing time in visual decisions.
- Polish-first, pendings-second — Rejected: starting on design when VideoPress iframes render empty divs and the big video is only on Netlify (not git) means every visual review would carry unspoken "yes but that one is broken" caveats.
- Interleaved thematic phases — Rejected: splitting work by theme (e.g., "content phase includes About + fixing iframes + bringing Popular Posts") mixes concerns and makes it hard to say "pending tech fixes are done; now I can see what's left".

The chosen order is: Pending Tech Fixes → Content Completion → Design Polish → Features → (future) SEO Cutover. The design polish and features are intentionally last-before-cutover so the staging site arrives at Phase 3 looking the way the owner wants it to look live.

## Key Decisions

- **Priority order**: technical debt first (Phase 2.1), content completion second (2.2), visual polish third (2.3), features fourth (2.4), cutover last (Phase 3).
- **About page content**: migrate the real content from WordPress page 185 (PT, Sobre Mim) and page 193 (EN, About me) rather than rewriting or keeping placeholders — the WP content already exists and is the owner's authored voice.
- **Dark mode**: ship **dark-default** with a light toggle, not light-only. This is a deliberate pivot from the Phase 1 light-only aesthetic. The Phase 1 brainstorm anchored on eltonminetto.dev (light), but dark-default is now preferred as a signature element; the light option stays via PaperMod's built-in toggle.
- **Search**: add Pagefind (static-site search, ~30KB on the client, zero backend, free). 107+ posts justifies a search affordance.
- **RSS**: expose Hugo's auto-generated /index.xml and /en/index.xml via a visible header or footer link — zero new code, improves distribution.
- **Analytics**: use **GoatCounter hosted free tier** (<100k pageviews/month). Explicit bot visibility is the discriminating feature — the owner explicitly wants to see which AI crawlers, search engines, and generic bots hit the site, not only humans. Server-side-ish via a tiny client script; GDPR-friendly; no cookie banner.
- **Phase numbering**: inserted phases are 2.1, 2.2, 2.3, 2.4 (decimal IDs, between existing Phase 2 and Phase 3). Phase 3 (SEO Cutover) stays the last phase and will be re-amended to depend on 2.4 during the next /aimi:plan run (today's `dependsOn: [2]` doesn't naturally gate it behind these new phases).

## Design Decisions

- **Aesthetic direction**: dark-default minimal, with the Phase 1 single-column 720px / system sans-serif / dates-above-titles aesthetic preserved. A light toggle returns the Phase 1 light palette on demand. Not "dark mode as an option" — **dark as the identity**, light as an escape hatch.
- **Reference points**: eltonminetto.dev continues to anchor the layout, but the palette inverts. The "monospace dates" treatment from Phase 1 gains extra legibility in dark.
- **Key visual element**: the orphan-translation "only in PT/EN" badge that was Phase 1's differentiator stays — and needs to retain legibility in both themes (AA contrast ≥4.5:1 in dark, as in light).

## Open Questions

- Which WordPress posts have VideoPress embeds that need video replacements? (deferred: inventoried during Phase 2.1 execution — `grep -l "wp-block-video" content/`)
- Which YouTube channel will host the uploaded videos? Public or Unlisted? (deferred: decided by owner during Phase 2.1 execution)
- RSS link placement — header or footer? (deferred: visual decision during Phase 2.3 polish)
- Pagefind search UI — header icon that opens a modal, or inline search field? (deferred: visual decision during Phase 2.4)
- CSP tightening for GoatCounter — allow `*.goatcounter.com` or a specific GoatCounter site domain? (deferred: decided at Phase 2.4 wiring time, the GoatCounter docs will name the exact origin.)
- Should Phase 3 (SEO Cutover) `dependsOn` be amended from `[2]` to `[2.4]` so the roadmap enforces the order? (resolved: yes — handled during the next /aimi:plan run via `aimi-cli roadmap-amend-phase`.)

## Next Steps

> Run `/aimi:plan --phase 2.1` to generate implementation tasks for Pending Tech Fixes. Subsequent phases (2.2, 2.3, 2.4) are planned individually in order.
