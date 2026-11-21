---
date: 2026-11-21
agent: learnings
topic: wordpress-to-hugo-migration-phase-1-foundation
depth: standard
---

## Institutional Learnings Search Results

### Search Context
- **Feature/Task**: Phase 1 Foundation of a WordPress-to-Hugo migration — building a bilingual (pt-BR + en) Hugo site based on PaperMod, styled minimally after eltonminetto.dev, deployed to Netlify on a staging subdomain. Phase scope: a Hugo site styled like eltonminetto.dev is live on a staging subdomain with bilingual scaffolding, home, about, and 404 pages.
- **Keywords planned**: `hugo`, `papermod`, `i18n`, `multilingual`, `pt-br`, `language switcher`, `orphan translation`, `netlify`, `hugo build`, `netlify.toml`, `staging subdomain`, `dns`, `cname`, `404`, `baseurl`, `theme submodule`, `hugo modules`
- **Target questions planned (search plan)**:
  1. Prior Hugo project setup gotchas (theme as submodule vs module, `baseURL`, `config.toml` / `hugo.toml` layout)?
  2. PaperMod customization patterns (overriding partials/layouts in `layouts/` instead of editing the theme)?
  3. Hugo i18n lessons — bilingual pt-BR/en, orphan translation handling, `enableMissingTranslationPlaceholders`, `defaultContentLanguage`?
  4. Language-switcher pattern with an "only in X" badge for pages that exist in one language only?
  5. Netlify + Hugo build configuration (pinning `HUGO_VERSION`, `netlify.toml`, build command, `--minify`, context-specific `baseURL`)?
  6. Staging-subdomain DNS lessons (CNAME to Netlify, branch deploys, Netlify DNS vs external DNS, HTTPS cert provisioning)?
  7. 404 handling on Netlify for a multilingual Hugo site (per-language 404, Netlify's default 404 page)?

### Files Scanned
- Total files scanned: **0**
- Directories inspected: `/Users/marcelioleal/workspace/newsite/.aimi/`
  - Present: `brainstorms/`, `research/`, `tasks/`
  - **Absent: `.aimi/solutions/`** (directory does not exist)
- Grep calls executed: 0 (no corpus to search)
- Candidate files identified: 0

### Critical Patterns (Always Check)
- **`.aimi/solutions/patterns/critical-patterns.md`**: **not present** — the entire `.aimi/solutions/` tree is absent, so no critical-patterns file exists.

### Relevant Learnings
None. The institutional-knowledge corpus has not been seeded in this repository.

### No Matches

There is nothing to reuse from `.aimi/solutions/` for this phase.

Root cause: `/Users/marcelioleal/workspace/newsite/.aimi/solutions/` does not exist on disk. Verified by direct `ls`:

```measure
$ ls /Users/marcelioleal/workspace/newsite/.aimi/solutions/
ls: /Users/marcelioleal/workspace/newsite/.aimi/solutions/: No such file or directory
```

The surrounding `.aimi/` scaffold contains only `brainstorms/`, `research/`, and `tasks/`:

```measure
$ ls /Users/marcelioleal/workspace/newsite/.aimi
brainstorms
research
tasks
```

This is a greenfield repository — no prior solutions, no prior patterns, no prior critical-pattern file. Phase 1 is, by definition, the first body of work on this codebase, so an empty learnings corpus is expected rather than anomalous.

### Recommendations

Because no prior learnings exist, the actionable recommendation is **forward-looking**: the planning and execution of Phase 1 should seed `.aimi/solutions/` with any non-obvious gotchas encountered, so Phase 2+ benefits. Specifically, candidate categories likely to accumulate learnings during Phase 1 — each would land under `.aimi/solutions/<category>/` with the standard frontmatter schema:

- **`developer-experience/`** — Hugo version pinning (`HUGO_VERSION` env var in `netlify.toml` must match local `hugo version`; mismatch is a top cause of "works locally, breaks on Netlify"). [INFERRED — generalization from the known Hugo/Netlify toolchain, not from any solution file in this repo.]
- **`integration-issues/`** — Netlify build config for Hugo (`netlify.toml` with `[build] command = "hugo --gc --minify"`, `publish = "public"`, and context-specific `HUGO_BASEURL` so deploy-preview and branch-deploy builds use the correct `baseURL`). [INFERRED.]
- **`integration-issues/`** — PaperMod installation method (git submodule vs Hugo Module vs vendored copy). Submodules require `git submodule update --init --recursive` on first clone *and* in Netlify's build; Netlify handles submodules but needs the `GIT_LFS_ENABLED` / submodule token configured if the theme repo is private. [INFERRED.]
- **`ui-bugs/`** — PaperMod customization should go through `layouts/` and `assets/css/extended/` overrides, never by editing files under `themes/PaperMod/`, so that theme updates (`git submodule update --remote`) do not blow away customizations. [INFERRED.]
- **`logic-errors/`** — Hugo i18n orphan handling: set `defaultContentLanguage = "pt-br"` and `defaultContentLanguageInSubdir = true` (or deliberately `false`) consistently; mismatched settings produce a language switcher that 404s. The "only in X" badge requires iterating `.Translations` and comparing against `.Site.Languages` at template time — pages missing a translation will not appear in `.Translations` at all. [INFERRED.]
- **`integration-issues/`** — Staging subdomain DNS: if using an external DNS provider, a `CNAME` for `staging.<domain>` pointing to `<site>.netlify.app` is the standard path; Netlify's automatic Let's Encrypt provisioning only triggers *after* the DNS record resolves, so expect a 5–60 min window where HTTPS is broken on first setup. [INFERRED.]
- **`ui-bugs/`** — Netlify serves `/404.html` automatically for unmatched routes, but for a multilingual Hugo site each language root (`/en/`, `/pt-br/`) needs its own 404 template (`layouts/404.html` with language-aware content), otherwise visitors on `/en/does-not-exist` get a pt-BR 404. [INFERRED.]

These are hypotheses for what *might* be encountered, not reports of what *has* been encountered. They should be validated against Phase 1 execution and promoted into real solution files only when a concrete incident occurs.

### Planner Guidance

Because the learnings corpus is empty, planning for Phase 1 should lean on:
1. **Upstream documentation** (Hugo docs, PaperMod wiki, Netlify Hugo docs) via `context7` or similar — not on this repo's history.
2. **The brainstorm file(s)** under `.aimi/brainstorms/` (present on disk) which likely contain the user's own design decisions for this migration and are the authoritative source for Phase 1 scope.
3. **Explicit seeding**: Phase 1's wrap-up should include a step to write at least one solution file under `.aimi/solutions/` (even a trivial one, e.g. the chosen `HUGO_VERSION`) so the directory exists and future `/aimi:plan` runs do not re-hit this same empty-corpus finding.
