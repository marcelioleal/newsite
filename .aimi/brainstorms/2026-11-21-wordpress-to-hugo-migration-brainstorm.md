---
date: 2026-11-21
topic: wordpress-to-hugo-migration
phases:
  - id: 1
    name: Foundation
    slug: foundation
    goal: A Hugo site styled like eltonminetto.dev is live on a staging subdomain with bilingual scaffolding, home, about, and 404 pages.
    successCriteria:
      - Staging subdomain serves a single-column, sans-serif, light-background Hugo site inspired by eltonminetto.dev.
      - Hugo native i18n is configured with content/pt-br and content/en and a visible language switcher.
      - Home and About render in both languages.
      - The switcher shows an "only in PT/EN" badge when a translation is missing instead of hiding or redirecting away.
    dependsOn: []
    creates:
      - identity: hugo_site_skeleton
        description: Hugo site based on PaperMod with layouts simplified to a minimal single-column sans-serif aesthetic
      - identity: netlify_staging_deploy
        description: Netlify project linked to the GitHub newsite repo, serving the staging subdomain
      - identity: language_switcher
        description: Bilingual switcher that renders an only-in-<lang> badge when the translation is missing
    needs: []
    areas:
      - themes/**
      - layouts/**
      - content/pt-br/**
      - content/en/**
      - hugo.toml
      - netlify.toml
  - id: 2
    name: Content Migration
    slug: content-migration
    goal: Every WordPress post, page, and image is versioned in the Hugo repo and renders on staging, including Recomendações sub-pages and the TCC/ClassGenerator pair.
    successCriteria:
      - All WordPress posts are converted to Markdown with front-matter (title, date, tags, language) under content/<lang>/posts/.
      - All WordPress media is downloaded and versioned under static/images/ and referenced from Markdown.
      - Recomendações renders with sub-pages for Books/Cafés, Kitesurf, Música, Sites e Podcasts, Posts Especiais, and Arte em SP where content exists.
      - TCC/ClassGenerator exists in both PT and EN variants as standalone pages.
    dependsOn:
      - 1
    creates:
      - identity: migrated_posts
        description: WordPress posts converted to Markdown files under content/<lang>/posts/
      - identity: migrated_media
        description: WordPress media downloaded and versioned under static/images/
      - identity: recomendacoes_section
        description: Recomendações page with its sub-pages rendered in the languages where content exists
      - identity: tcc_pages
        description: TCC/ClassGenerator pages in PT and EN as standalone content
    needs:
      - identity: hugo_site_skeleton
        description: Layouts and i18n setup from Phase 1
    areas:
      - content/**
      - static/images/**
      - data/**
  - id: 3
    name: SEO Preservation and Cutover
    slug: seo-cutover
    goal: marcelioleal.com serves the Hugo site without breaking inbound links and WordPress is decommissioned.
    successCriteria:
      - Every WordPress post URL is either preserved as the same slug on Hugo or served via a 301 redirect.
      - A Netlify _redirects file covers every slug change and is verified end-to-end with a crawler.
      - DNS of marcelioleal.com points at Netlify production and WordPress is turned off.
      - Google Search Console reports no new 404 errors after the cutover window.
    dependsOn:
      - 2
    creates:
      - identity: redirect_map
        description: Netlify _redirects file mapping legacy WordPress URLs to Hugo URLs
      - identity: production_cutover
        description: Production deployment serving marcelioleal.com with WordPress decommissioned
    needs:
      - identity: migrated_posts
        description: Hugo posts with final slugs so redirects can be authored
    areas:
      - static/_redirects
      - netlify.toml
---

# WordPress-to-Hugo Migration (marcelioleal.com)

## What We're Building

Marcelio's personal site (marcelioleal.com) is migrating from WordPress (Independent Publisher 2 theme, Jetpack sitemap) back to Hugo deployed on Netlify from a new GitHub repo named `newsite`. The target aesthetic is the minimal, single-column, sans-serif look of https://eltonminetto.dev/ — but with two personal differentiators: a living Recomendações section (música, livros, cafés, kitesurf, arte em SP, sites e podcasts, posts especiais) and a light personal visual touch. The site stays bilingual (pt-BR default + en) using Hugo's native i18n with content/pt-br and content/en mirrored. Editorially, individual posts can live in one language only — the switcher shows an "only in PT/EN" badge instead of orphaning the reader.

## Why This Approach

User resolved the approach during Phase 2 exploration. Alternatives considered: (A) fork eltonminetto.dev — rejected because Elton's GitHub has no public repo for the site; (B) hello-friend-ng — rejected as less documented and thinner community; (C) custom from scratch — rejected because that was the exact approach that stalled the previous migration attempt. Rationale: PaperMod provides a well-maintained Hugo theme with native multilingual support, and reducing it to match Elton's aesthetic is far less work than writing baseof/list/single layouts from scratch while also keeping the project shipable in 2-3 weeks.

## Key Decisions

- **Theme base**: PaperMod customized to resemble eltonminetto.dev (single-column, sans-serif, light background). Rationale: fastest path to the target look with proven i18n.
- **Content migration**: Full WordPress export via a WP-to-Hugo exporter plugin, then convert to Markdown. Rationale: all 10+ posts and pages (2023-2026) deserve to carry over; cherry-picking defers to later pruning.
- **Multilingual scaffolding**: Hugo native i18n with content/pt-br and content/en mirrored at the structural level (nav, UI strings, menus). Posts themselves do not require pairs. Rationale: structural consistency without editorial burden.
- **Editorial policy**: One language per post, chosen by topic (technical → EN, personal/Brazil-specific → PT). Rationale: matches how Marcelio actually writes, keeps new posts flowing.
- **Sections to carry over**: Home, Sobre, Popular Posts, Recomendações (Books/Cafés, Kitesurf, Música, Sites e Podcasts, Posts Especiais, Arte em SP), and the TCC/ClassGenerator pair. Additional sections can be added later.
- **Images**: Downloaded from WordPress and versioned in the Hugo repo under `static/images/`. Rationale: no ongoing dependency on the WP media CDN; survives WordPress shutdown.
- **Comments**: None. Rationale: matches the minimal reference, zero moderation overhead, contact via email/social at the bottom of posts.
- **Deploy target**: Netlify, same as the previous Hugo attempt, with GitHub repo `newsite` as source. Free tier covers current volume comfortably.
- **Domain cutover**: Staging subdomain first (e.g., new.marcelioleal.com). Final cutover by pointing marcelioleal.com DNS at Netlify after staging is validated end-to-end. Rationale: safest path, no visible downtime for readers.
- **URL preservation**: Hugo slugs match WordPress slugs where possible; everything else gets a 301 via Netlify `_redirects`. Rationale: preserve SEO and backlinks accumulated by WordPress.
- **Orphan-translation UX**: Switcher always visible; when a translation is missing, a discreet "only in PT/EN" badge replaces the toggle target. Rationale: honest about bilingual coverage without surprising the reader with language-mismatched home redirects.
- **Success criterion**: SEO preserved (zero new 404s in Search Console after cutover) plus a visual that Marcelio enjoys looking at. Volume-of-posts explicitly deprioritized as the success metric.
- **Target timeline**: 2-3 weeks of evening/weekend work, with a planned cutover date rather than open-ended "when it's ready".

## Design Decisions

- Aesthetic direction: eltonminetto.dev — single-column, sans-serif, light background, minimal nav, dated blog list, no decorative flourishes.
- Reference points: eltonminetto.dev as the primary visual anchor.
- Key visual element: a living Recomendações section that Elton does not have (música, livros, cafés, kitesurf, arte em SP, sites e podcasts, posts especiais) plus a light personal touch — a single accent color or a monospaced treatment for dates/headers — to add personality without breaking the minimal frame.

## Prototypes

No prototype generated during this session. The visual reference provided by the user (https://eltonminetto.dev/) functions as the direct reference for the Foundation phase layouts.

## Open Questions

- Which WordPress-to-Hugo exporter tool to use (wordpress-to-hugo-exporter plugin, SchumacherFM/wordpress-to-hugo-exporter, or a custom script against the WP REST API). [deferred: resolve during `/aimi:plan` Content Migration phase]
- Whether to add a lightweight privacy-friendly analytics stack (Plausible, Umami, or none). [deferred: resolve during `/aimi:plan` Foundation phase]
- Exact staging subdomain name (new.marcelioleal.com, staging.marcelioleal.com, or hugo.marcelioleal.com). [deferred: resolve during `/aimi:plan` Foundation phase]
- Font choice for the personal visual touch — system sans-serif stack (fast, zero cost) vs a specific hosted pair like Inter + JetBrains Mono (adds a render-blocking font request). [deferred: resolve during `/aimi:plan` Foundation phase]

## Next Steps

> Run `/aimi:plan` to generate implementation tasks
