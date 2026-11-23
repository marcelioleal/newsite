# Phase 2.3 Handoff — Design Polish (dark-default)

**Date:** 2026-11-23 (shipped over 11-22 and 11-23)
**Branch:** main (solo-dev direct commits)
**Status:** completed on staging

## Shipped

- Dark theme as default (`defaultTheme: dark`), light toggle preserved
- Pará-clay accent palette (`#d9541b`) in `assets/css/extended/custom.css`
- Self-hosted Inter + JetBrains Mono fonts (preloaded primary variants)
- Two-column home layout (1120px): posts feed + sidebar
- Home hero: avatar + bio + badges + CTAs card
- Header redesign: ML monogram SVG + "Marcelio Leal" brand name
- Topic filter pills on home
- Taxonomy archive layout
- Post-single typography + code block styling

## Commits in this phase

- 4650bdc feat(phase-2.3): home redesign — hero + 2-col + dark-default + taxonomy filters
- a100485 fix(header): trim menu to spec and drop site title text
- 11a7744 feat(header): ML monogram + name signature, bio card refresh, new profile
- c923cc3 fix(home-hero): drop duplicate name + re-crop avatar on face
- fcea2ab feat(home-hero): new work tag with Former companies, merged passions, socials row

## Extensions beyond original plan

Mid-flight user additions:
- ML monogram SVG from Downloads adapted to currentColor
- Profile photo swap with face-centered crop
- Role badge expanded with LinkedIn company links
- Socials row (LinkedIn, Instagram, X, @blankframe.art)
- Bio text trimmed (removed Berlin references, ex-company list)

## Known follow-ups

- Favicon multi-res .ico + /brand/icon-512.png from user-provided asset bundle
- open-graph image update to use ML monogram
