## Decisions Made

- WP-to-Hugo conversion: scripts/wp_to_hugo.py using WordPress.com public REST API + pandoc --from=html --to=gfm + 10-regex Python post-processor. NO third-party exporter plugin.
- Language detection: lingua-language-detector weighted on title + cleaned body; hard category override (22748652 Uncategorized-en + 22748979 Product Management = EN).
- Permalinks: posts at /:slug/ matching WordPress URLs 1:1. Pages use default Hugo /:section/:slug/ resolution; About uses slug='sobre' in PT, 'about' in EN.
- Menu strategy: [[languages.X.menu.main]] in hugo.toml drives per-language nav. header.html refactored from site.GetPage lookup to range site.Menus.main.
- Content layout: Hugo page bundles (content////index.md) + branch bundles (_index.md) for Recomendações/Recommendations listing pages.
- Media paths: images static/images///, videos static/videos/, PDFs static/assets/.
- HEIC → JPEG at migration time via heif-convert -q 92. VideoPress MP4s downloaded from videos.files.wordpress.com into static/videos/ for self-hosting.
- Translation keys for divergent PT/EN slug pairs: tcc-classgenerator, coffee (cafes↔coffee), books (livros↔books), recomendacoes (recomendacoes↔recommendations). File-path convention elsewhere.
- Home page dated post list via mainSections=['posts'] + custom layouts/_default/list.html with paginated chronological entries.
- Front-matter dialect: YAML --- (matches Phase 1 shipped content).
- Big-file handling: static/videos/20250201095728000070.mp4 (139MB) gitignored — Netlify CLI deploys it, but GitHub rejects >100MB. Candidate for YouTube migration.
- Jetpack CDN external proxies (i0.wp.com//...) left as-is — these proxy third-party images (Giphy, Medium, softwarelivre.org). Will break when WP Jetpack is decommissioned in Phase 3.

## Artifacts Created

- scripts/wp_to_hugo.py — ~500 LOC Python: WP REST fetch, pandoc convert, 10-regex post-processor, HEIC convert, VideoPress download, Hugo bundle writer, lingua language detection
- scripts/rewrite_media_urls.py — post-migration URL rewriter (3 regex classes: WP uploads, VideoPress, Jetpack-proxied own-site)
- scripts/posts-manifest.json — 107 WP post ids with slugs and lang:auto
- scripts/media-manifest.json — 134 media ids with source_url + mime_type
- scripts/recomendacoes-manifest.json — 14 Recomendações/Recommendations pages with target_path + translationKey
- scripts/tcc-manifest.json — TCC/Thesis pair with shared translationKey
- scripts/README.md — install prerequisites (pandoc, libheif, lingua) + manifest shapes + conversion pipeline docs
- hugo.toml — [permalinks] posts=/:slug/; per-language [[menu.main]] for Sobre/About + Recomendações/Recommendations; [params.mainSections]=['posts']
- layouts/partials/header.html — menu-driven nav (range site.Menus.main) + preserved orphan-aware language switcher
- layouts/_default/list.html — dated post list for home; sub-page link list for section pages
- 107 posts under content/pt-br/posts// (103) and content/en/posts// (4)
- 14 Recomendações branch bundles: content/pt-br/recomendacoes/{_index,livros,musica,kitesurf,sites-e-podcasts,posts-especiais,cafes,arte-em-sp,viagem-pra-belem,artigos-tech}/_index.md + content/en/recommendations/{_index,books,coffee,tech-articles}/_index.md
- content/pt-br/tcc-classgenerator/index.md + content/en/thesis-classgenerator/index.md (translationKey=tcc-classgenerator)
- static/images/ — 112 images across year/month subdirs
- static/videos/ — 12 self-hosted VideoPress MP4/MOV files (13th was 139MB, gitignored)
- static/assets/ — 8 PDFs including ClassGenerator-Thesis-EN.pdf, tccfinal.pdf, and 6 legacy presentation PDFs
- Live staging: https://new.marcelioleal.com (noindex, HTTPS, HSTS, CSP) — 107 posts resolve 200, Recomendações bilingual, TCC pair, dated home list

## Deviations

- The 107→107 posts migrated included only 4 EN classifications despite the plan assuming more posts would have English content. Category 22748652 (Uncategorized-en) + 22748979 (Product Management) hard override caught the explicitly EN-tagged posts. Lingua detection on title+body was conservative (preferred PT for ambiguous cases). Reviewer can manually flip specific posts to en via front-matter if needed.
- 133 of 134 media written (1 duplicate filename collision, 2024 vs 2025 app.pdf). All HEIC successfully converted to JPEG. The 139MB video at static/videos/20250201095728000070.mp4 exceeded GitHub's 100MB file limit; added to .gitignore and deployed only via Netlify CLI. Not referenced from any post currently.
- VideoPress embeds in migrated Markdown produced empty  placeholders because pandoc stripped the iframe src. Known posts affected: o-perigo-da-musica-reflexiva-e-a-relacao-austro-paraense, sounds-of-quartzo, ainda-continuo-com-23, o-que-e-software-em-2024-com-a-inteligencia-articial-ainda-precisaremos-programar. Deferred: replace empty iframes with " controls> HTML or YouTube embeds.
- Jetpack CDN i0.wp.com URLs that proxy external domains (giphy.com, medium.com, softwarelivre.org) are left unrewritten — 157 references across posts. Will break when Jetpack proxy stops working post-decommission. Deferred to Phase 3 or a follow-up: either download these external images locally, or strip the Jetpack wrapper to point at original source.
- git history rewrite: ffcb4b1 (original Wave 2 commit) was reset and recommitted as 5af4a12 without the 139MB video. Second commit 327a1d6 (US-006 rewrite) was consolidated into the same new commit. The two WIP commits exist only in reflog.
- Roadmap Phase 2 creates identities were originally abstract (migrated_posts, migrated_media, recomendacoes_section, tcc_pages) and did not verify against tracked source. Amended via roadmap-amend-phase to concrete paths (content/pt-br/posts, static/images, content/pt-br/recomendacoes, content/pt-br/tcc-classgenerator). Phase 3's needs.migrated_posts retargeted to content/pt-br/posts.

## Deferred Items

- YouTube migration for large video (139MB): user plans to upload to a YouTube channel; the empty iframe placeholders in affected posts need to be replaced with YouTube embeds.
- VideoPress empty-iframe cleanup in ~4 posts (replace with  HTML5 tag pointing at /videos/ or with YouTube embeds).
- Jetpack CDN proxied external images: 157 refs to i0.wp.com/ URLs. Download locally or strip Jetpack wrapper. Follow-up for Phase 3 or standalone cleanup.
- GitHub-webhook auto-deploy on Netlify (push to main → auto-build) still pending from Phase 1 handoff. Phase 3 should wire via Netlify UI → Build & deploy → Link repository.
- Nav menu entries for pages NOT yet created (Phase 1 plan foresaw more sections). Currently nav shows Sobre + Recomendações (PT) / About + Recommendations (EN). Expand as needed.
- 20 WP pages NOT migrated: Sobre Mim (185), About me (193), Popular Posts PT (226) + EN (237), Artigos Tech (1606). Those were in scope per the brainstorm but not called out in US-007's explicit id list. Follow-up to migrate them if desired.

## Contracts Delivered

- Phase 3 consumes content/pt-br/posts (retargeted from migrated_posts) — Hugo posts with final slugs so Phase 3 can author the Netlify _redirects file mapping legacy WP URLs where the slug differs.
- Phase 3 adds static/_redirects at the repo root mapping WP URLs that do NOT match the migrated slugs. Audit of which WP URLs diverge is Phase 3's first task.
- Phase 3 flips the apex marcelioleal.com from WordPress to Netlify production (apex A record + www CNAME). hugo.toml baseURL stays the staging URL; Netlify's [context.production] command uses ${URL} which will be https://marcelioleal.com/ once the apex points at Netlify. HUGO_ENV in [context.production.environment] must flip from 'staging' back to 'production' at cutover to disable noindex.
