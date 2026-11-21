## Decisions Made

- Hugo 0.170.1 non-extended pinned in .tool-versions and netlify.toml
- PaperMod installed as a shallow git submodule at themes/PaperMod (--depth=1); never edit under themes/
- Overrides restricted to assets/css/extended/, layouts/partials/{header,extend_head,extend_footer}.html, layouts/404*.html
- Hugo native i18n: defaultContentLanguage=pt-br, defaultContentLanguageInSubdir=false — pt-BR served at /, en at /en/
- PT About slug=sobre (resolves at /sobre/); EN stays /en/about/. Nav partial uses site.GetPage so slugs resolve per-language
- Language switcher iterates site.Languages + .AllTranslations to render aria-current span / link / aria-disabled only-in-X badge; pure HTML, no JS
- 404 lives at layouts/404.html (bilingual fallback with inline hide-wrong-language script) + layouts/404.pt-br.html + layouts/404.en.html
- Staging subdomain new.marcelioleal.com. CNAME added via WordPress.com DNS (TTL 300s) → newsite-marcelioleal.netlify.app
- HUGO_ENV=staging drives PaperMod's own robots meta to emit noindex,nofollow. extend_head doubles that keyed on baseURL != apex. Phase 3 flips both.
- No analytics in Phase 1 (deferred: Netlify Web Analytics is the preferred option when a metric becomes necessary)
- System sans-serif font stack (zero FOIT/FOUT, no Google-Fonts GDPR exposure); single-column 720px max-width, light background
- Security headers via static/_headers: CSP (allows unsafe-inline for 404 inline script), Referrer-Policy strict-origin-when-cross-origin, X-Content-Type-Options nosniff, Permissions-Policy camera/microphone/geolocation/interest-cohort off
- Deploy flow: netlify-cli with manual netlify deploy --prod --dir=public. GitHub-webhook auto-deploy not yet wired; see Deferred
- WP-to-Hugo exporter choice deferred to Phase 2 Content Migration

## Artifacts Created

- hugo.toml — bilingual pt-br/en configuration, PaperMod theme, [params] disabling theme toggle/breadcrumbs/share/reading-time/post-nav/profileMode
- netlify.toml — pinned HUGO_VERSION=0.170.1, build hugo --gc --minify, publish public, three [context.*] environments (production=staging in Phase 1-2; deploy-preview; branch-deploy), GIT_SUBMODULE_STRATEGY=recursive
- layouts/partials/header.html — bilingual language switcher, orphan-aware only-in-X badge, aria-current/aria-disabled
- layouts/partials/extend_head.html — conditional noindex (keyed on baseURL) + canonical + hreflang alternates (pt-br, en, x-default) + Open Graph defaults
- layouts/404.html + layouts/404.pt-br.html + layouts/404.en.html — bilingual fallback with JS-off graceful degradation
- assets/css/extended/custom.css — minimal single-column 720px light aesthetic, system font stack, :focus-visible outline
- i18n/pt-br.yaml + i18n/en.yaml — site_description, nav_about, only_in_language (printf %s), switch_to_language, not_found_title, not_found_body, back_to_home
- content/pt-br/{_index.md, about/index.md (slug=sobre)} + content/en/{_index.md, about/index.md} — home + about placeholder bios
- static/robots.txt — Disallow: / (staging noindex)
- static/_headers — Netlify security headers
- static/og-default.png (1200x630 placeholder) + static/favicon.ico (16x16 placeholder)
- README.md — clone + git submodule update --init --recursive + hugo server -D + theme update + deploy instructions + Toolchain section + Phase 1 artifacts anchor
- .tool-versions — hugo 0.170.1 (asdf/mise compatible)
- .gitignore — excludes /public/, /resources/, .hugo_build.lock, .DS_Store, .netlify
- themes/PaperMod — pinned git submodule, --depth=1, url github.com/adityatelange/hugo-PaperMod
- Netlify project newsite-marcelioleal (site_id 00c6970d-3ce5-412d-bef3-5a3f1e1c9625), serving the staging subdomain https://new.marcelioleal.com with HTTPS + Let's Encrypt cert + HSTS
- GitHub repository https://github.com/marcelioleal/newsite (public, main branch, 16 commits)

## Deviations

- US-001 git init step was done as a pre-execute bootstrap (git init + initial empty commit) because /aimi:execute requires an existing git repo as its starting state. The rest of US-001 (submodule, folder scaffold, hugo.toml, .tool-versions, .gitignore, archetypes) ran normally.
- All stories ran sequentially on main instead of parallel in per-story worktrees because the greenfield-from-nothing bootstrap makes worktree-first execution less useful (only one producer per file, no real contention).
- Original plan expected /sobre/ URL for PT About, but US-002 authored content at content/pt-br/about/ (slug defaults to dir name = /about/). Fixed post-US-002 by adding slug: 'sobre' to front-matter and changing nav partial to resolve via site.GetPage.
- noindex contract was rewritten mid-Phase: original key was HUGO_ENV but the default Hugo build sets it to 'production', conflicting with PaperMod's own index/follow emission. Fixed by using HUGO_ENV=staging for Netlify production context (Phase 1-2) and keying extend_head's noindex on baseURL != apex.
- Netlify GitHub-webhook CI setup was not completed (the --with-ci path in netlify sites:create prompts for a GitHub OAuth flow that is not available from this agent's terminal). Current deploys are manual via netlify deploy --prod --dir=public. Phase 2 should wire GitHub via the Netlify UI → Site settings → Build & deploy → Link repository → GitHub → marcelioleal/newsite.
- Phase 1 creates identities were originally architecture-level nouns (hugo_site_skeleton, netlify_staging_deploy, language_switcher) which verify-creates could not match against tracked source. Amended via roadmap-amend-phase --retarget-needs to real tracked paths (hugo.toml, netlify.toml, layouts/partials/header.html). Phase 2's needs.hugo_site_skeleton was retargeted to hugo.toml by the same call.

## Deferred Items

- GitHub-webhook auto-deploy on Netlify (push to main → auto-build). Current deploys are manual CLI. Wire via Netlify UI → Build & deploy → Link repository in Phase 2.
- WordPress-to-Hugo exporter tool choice (wordpress-to-hugo-exporter plugin, SchumacherFM, or custom WP REST API script). Resolve at Phase 2 start.
- Analytics decision (Netlify Web Analytics vs Plausible vs Umami vs none). Revisit after cutover when a real metric becomes necessary.
- Audit-deferred: Story 05 wires the [params] / markup blocks the US-001 scaffold deferred (verified — [params] is populated in hugo.toml by story 05 + story 07).
- Audit-deferred: Story 07 appends canonical/hreflang/OpenGraph to layouts/partials/extend_head.html (verified — live markup confirms).
- DNS: www.marcelioleal.com is still a CNAME to apex marcelioleal.com (WordPress), untouched. Phase 3 will decide whether www moves to Netlify or 301-redirects at apex.

## Contracts Delivered

- Phase 2 consumes: hugo.toml (retargeted from hugo_site_skeleton) — the bilingual Hugo config, i18n setup, and theme pinning Phase 2 Content Migration depends on
- Phase 2 content paths: content/pt-br/posts/, content/en/posts/, static/images/ (per the brainstorm roadmap areas) — Phase 2 adds these; Phase 1 reserved the directory placeholders
- Phase 3 consumes: migrated_posts from Phase 2, then adds static/_redirects at the repo root (netlify.toml context.production commands already derive baseURL from Netlify's ${URL} env var — Phase 3 just points the apex marcelioleal.com at the site and flips HUGO_ENV from staging to production)
