## Decisions Made

- VideoPress swap strategy: re-fetched each affected post via WP REST API, extracted VideoPress GUID from original iframe src, mapped via media-manifest.json to local /videos/. paths; replaced empty  with ....
- Orphan 139MB video decision: deleted static/videos/20250201095728000070.mp4 rather than uploading to YouTube — NO migrated post references it (confirmed via grep). YouTube upload path remains available if a future post wants to reference an external hosted video.
- Jetpack CDN cleanup strategy: default 'archive via proxy' — download each external image from the Jetpack proxy (while still live) into static/images/external//. Dead sources (imageshack.us, old brazilian blogs, Flickr pre-2010) had their  and  tags removed entirely since they were already broken.
- Hugo markup unsafe=true: Phase 1 brainstorm deferred [markup.goldmark.renderer] to story 05; that never happened. Added here because inline HTML (VideoPress , Spotify embeds, image divs) was being silently stripped. Trust model: all content is owner-authored, no user submissions, so unsafe is appropriate.
- Netlify GitHub auto-deploy: wired via UI OAuth (netlify-cli can't drive the GitHub App installation handshake). Phase 2.1 auto-deployed itself as proof of life. Manual deploy via netlify-cli remains available as emergency fallback (documented in README).

## Artifacts Created

- scripts/swap_videopress.py — 160 LOC Python: WP REST re-fetch, token→filename mapping via media-manifest.json, idempotent HTML5  substitution; deletes 139MB orphan
- scripts/cleanup_jetpack_proxies.py — 180 LOC Python: downloads live Jetpack-proxied images to static/images/external//, removes dead-source / tags; idempotent with dry-run
- static/images/external/ — 74 archived external images under host-named subdirs (giphy, cdn-images-1.medium.com, softwarelivre.org, images.uncyc.org, blog.ulf-wendel.de, etc.)
- hugo.toml — [markup.goldmark.renderer] unsafe=true added; allows inline HTML to render
- Netlify ↔ github.com/marcelioleal/newsite auto-deploy wired via Netlify GitHub App (installation_id 8142829); push to main triggers build automatically
- README.md — Deploy section updated to document auto-deploy + manual fallback

## Deviations

- Phase 2.1 scope grew by one item: the goldmark unsafe=true fix was not in the original brainstorm but became necessary during US-004 verification when live rendered HTML showed zero  tags despite local build having them. Fixing it unlocked not only VideoPress playback but also Spotify embeds and WordPress Gutenberg div structures that had been silently stripped across all 107 migrated posts.
- Phase 2.1 creates identities were originally abstract (youtube_video_embeds, netlify_github_autodeploy) — not verifiable against tracked source. Amended via roadmap-amend-phase to the two real tracked scripts (scripts/swap_videopress.py, scripts/cleanup_jetpack_proxies.py). The netlify_github_autodeploy outcome is observable via netlify api getSite's build_settings.repo_url field but is not a tracked artifact, so it's documented in handoff decisions rather than as a verifiable create.
- Jetpack cleanup removed 88 dead-source  tags that pointed at long-defunct external hosts (imageshack.us accounts from 2007-2008, old brazilian blog aggregators, early Flickr URLs). Posts affected retain their text but lose those images that were already broken before migration.

## Deferred Items

- YouTube upload for 139MB video: not deferred anymore — deleted since no post referenced it. Available to revisit later if a specific post wants an embedded hosted video.
- Older WordPress posts (pre-2015) often lose aesthetic coherence because their image references were dead external hosts. They remain migrated as text archives.
- Netlify's 'Git submodules' UI toggle was not explicitly flipped — the netlify.toml [build.environment] GIT_SUBMODULE_STRATEGY=recursive + the auto-detected submodule configuration suffices; PaperMod submodule has been fetching correctly in every build since Phase 1.

## Contracts Delivered

- Phase 2.2 (Content Completion) reuses scripts/wp_to_hugo.py from Phase 2 for the remaining 5 WP pages (Sobre Mim 185, About me 193, Popular Posts PT/EN 226/237, Artigos Tech 1606). No new conversion tooling needed.
- Phase 2.3 (Design Polish dark-default) builds on the current hugo.toml [params] and assets/css/extended/custom.css — the dark palette extends Phase 1's light aesthetic; the goldmark unsafe=true setting stays in place.
- Phase 2.4 (Features: Pagefind + RSS + GoatCounter) consumes layouts/partials/extend_head.html (Phase 1), netlify.toml for CSP updates (Phase 1), and the auto-deploy pipeline wired here — new scripts only, no changes to existing scripts.
