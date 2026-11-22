## Decisions Made

- Reused scripts/wp_to_hugo.py --force to overwrite Phase 1 placeholder About pages and Phase 2 placeholder Artigos Tech. Script had the --force flag from Phase 2.
- About PT slug=sobre (URL /sobre/, matches Phase 1), About EN slug=about (URL /en/about/). Shared translationKey about. Popular Posts PT (slug posts-populares) ↔ EN (slug popular-posts) via shared translationKey popular-posts. Artigos Tech translationKey tech-articles pairs with /en/recommendations/tech-articles/.
- Nav weight 15 slots Popular Posts between Sobre/About (10) and Recomendações/Recommendations (20) in the per-language menu.
- After migration, ran scripts/rewrite_media_urls.py to rewrite 23 own-site Jetpack-CDN URLs (i0.wp.com/marcelioleal.com/wp-content/uploads/...) to the local /images/YYYY/MM/ paths downloaded in Phase 2.

## Artifacts Created

- scripts/content-completion-manifest.json — 5 WP page ids with target_paths and translationKeys
- content/pt-br/about/index.md — real Sobre Mim bio from WP page 185 (replaces Phase 1 placeholder)
- content/en/about/index.md — real About me bio from WP page 193 (replaces Phase 1 placeholder)
- content/pt-br/posts-populares/_index.md — Popular Posts PT branch bundle from WP 226
- content/en/popular-posts/_index.md — Popular Posts EN branch bundle from WP 237
- content/pt-br/recomendacoes/artigos-tech/_index.md — Artigos Tech replaced with real WP 1606 content
- hugo.toml — 2 new [[languages.X.menu.main]] entries (Posts Populares PT, Popular Posts EN) at weight 15

## Deviations

- Phase 2.2 planning predicted a potential need to migrate Artigos Tech because Phase 2 inferred that page from WP parent-child relationships. Verified: the Phase 2 placeholder DID exist but was replaced cleanly by the --force migration.
- Phase 2.2 creates identities were originally abstract (content/pt-br/about/index.md, content/en/about/index.md, content/pt-br/posts-populares, content/en/popular-posts). Phase 2's amended creates list included content/pt-br/posts and /recomendacoes but not the specific files Phase 2.2 was about to overwrite — amended via roadmap-amend-phase after migration completed.

## Deferred Items

_None._

## Contracts Delivered

- Phase 2.3 (Design Polish dark-default) consumes hugo.toml [params] — the dark palette + toggle extends current light aesthetic; Phase 2.2 did not touch [params] so there's no overlap.
- Phase 2.4 (Features: Pagefind + RSS + GoatCounter) consumes layouts/partials/extend_head.html (unchanged) and netlify.toml (unchanged). No conflict with Phase 2.2 changes.
