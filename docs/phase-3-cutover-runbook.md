# Phase 3 — WordPress → Hugo Cutover Runbook

**Goal:** `marcelioleal.com` serves the Hugo site from Netlify, inbound WP URLs 301 to their Hugo equivalents, WordPress is decommissioned, Search Console reports no new 404s after the cutover window.

**Window:** ~21 days end-to-end (D-7 preflight → D cut → D+14 decommission).
Cut itself is a ~30-min window on a weeknight (never Friday evening).

**Prerequisites verified in the pre-flight audit session:**
- `static/_redirects` covers 107/107 migrated posts on the WP-dated `/YYYY/MM/DD/slug/` path (99.1% live-tested against staging).
- Category / tag / static-page redirects verified.
- 2 known residual gaps, both low-severity, documented in [Known gaps](#known-gaps-accepted-pre-cut).

---

## Known gaps (accepted pre-cut)

1. **`/2008/05/02/1%c2%ba-de-maio/` → 404.** Netlify's redirect matcher silently ignores rule sources containing UTF-8 (the `º` ordinal). Rule is correctly byte-encoded in `_redirects` but doesn't fire. Low severity: 2008 post, no known external backlinks. Mitigation: monitor Search Console; if it shows up, add a manual rule using a wildcard pattern or rename the slug.
2. **`/?p=N` short-links don't 301.** Netlify's `Query=p=N` matcher doesn't fire (tried both `/*` and `/` source paths, plus `Query=` before/after the status code). WordPress's canonical URL has always been `/YYYY/MM/DD/slug/`, so `?p=N` was only used in the admin and rarely indexed. Mitigation: same — monitor Search Console.
3. **Missing migrated image: `/wp-content/uploads/2013/12/victoreleo.jpg`.** The `/wp-content/uploads/*` → R2 redirect fires correctly, but this specific file was never uploaded to R2 during Phase 2 — the migration script skipped it. Referenced by the post `startup-e-cto-as-solucoes-para-um-bom-casamento`. Mitigation: either find the original and `./scripts/upload-image.sh`, or edit the post to remove the broken `<img>` reference.

None of these block the cut. (1) and (2) are fixable in-flight if Search Console surfaces them; (3) is cosmetic.

---

## Variables to fill in before you start

| Placeholder | Where to find |
|---|---|
| `<REGISTRAR>` | Where you bought the domain (Registro.br, GoDaddy, Namecheap, Cloudflare, Google Domains, etc.) |
| `<NETLIFY_SITE_NAME>` | Netlify dashboard → your site → Site name (today's staging `newsite-marcelioleal`) |
| `<NETLIFY_APEX_IPS>` | Netlify dashboard → Domain settings → DNS → reveals IPs when apex is added (usually `75.2.60.5`) |
| `<WP_HOSTING>` | Where WP lives (WordPress.com, Bluehost, hosting with own panel, etc.) |
| `<WP_ADMIN_URL>` | e.g. `https://marcelioleal.com/wp-admin/` |

---

## D-7 — Pre-flight (one week before)

Goal: everything ready so D-day is purely a DNS switch.

### D-7.1 Freshen the redirects audit
```bash
cd ~/workspace/newsite
/opt/homebrew/bin/python3 scripts/generate_redirects.py
git diff static/_redirects
# If any diff, commit it. The pre-flight should produce zero diff.
```

### D-7.2 Full WordPress backup
- [ ] Export every post, page, media via WP Admin → Tools → Export → **All content** (`.xml` file). Save locally as `backups/wp-export-YYYY-MM-DD.xml`.
- [ ] If on self-hosted WP: dump the database (`wp db export`) and zip `wp-content/` (full plugin + themes + uploads).
- [ ] If on WordPress.com: the export is the only extraction option — note that you cannot re-import to a different host without a paid plan.
- [ ] Store the backup **outside** the WP server (local disk + a cloud copy).

### D-7.3 Lower DNS TTL
- [ ] Log into `<REGISTRAR>` DNS panel.
- [ ] For each of `marcelioleal.com` (apex) and `www.marcelioleal.com`:
  - Note down current `TTL` (likely `3600` or `86400`).
  - Change to `300` (5 min).
- [ ] This takes `OLD_TTL` seconds to propagate. Done 7 days before D gives plenty of buffer.

### D-7.4 Note down current DNS for rollback
Create `backups/dns-pre-cutover.txt` with the full current state. Every DNS panel lets you export; otherwise screenshot:

```
marcelioleal.com (apex)
  A    xxx.xxx.xxx.xxx    TTL=300
  A    (other if present)

www.marcelioleal.com
  CNAME marcelioleal.com   TTL=300

MX records (if you have email)
  MX    10  mx1.<email-provider>.com
  MX    20  mx2.<email-provider>.com

TXT (SPF, DKIM, verification)
  TXT  "v=spf1 include:..."
  TXT  "google-site-verification=..."

Nameservers
  ns1.<registrar>.com
  ns2.<registrar>.com
```

### D-7.5 Add the domain to Netlify (no DNS swap yet)
- [ ] Netlify dashboard → `<NETLIFY_SITE_NAME>` → Domain settings → **Add custom domain** → `marcelioleal.com` (and separately `www.marcelioleal.com`).
- [ ] Netlify will say "awaiting DNS pointing here" — that's expected, don't flip DNS yet.
- [ ] Netlify auto-provisions a Let's Encrypt cert as soon as DNS points in. Wait for that on D-day (usually <5 min).

### D-7.6 Confirm MX / email records (if you use email at the domain)
- [ ] List MX / TXT / SPF / DKIM records. These stay untouched during DNS swap — only A/AAAA/CNAME for apex and www change.
- [ ] Double-check in `backups/dns-pre-cutover.txt` that every email-related record is noted.

### D-7.7 Audit crawl re-run
```bash
cd ~/workspace/newsite
./scripts/preflight_crawl.sh
```
Expect: **121 pass, 1 fail** — the fail should be exactly the known `1º-de-maio` UTF-8 gap. Any other failure → investigate before D-day. The script also flags the `?p=N` as a known gap (does not count toward pass/fail).

After the cut, re-run against the apex to confirm production parity:
```bash
BASE_URL=https://marcelioleal.com ./scripts/preflight_crawl.sh
```

### D-7.8 Smoke-test the site end to end
Open `https://new.marcelioleal.com/` and manually hit:
- [ ] Home loads, newsletter CTA works
- [ ] Any 5 posts from the home feed load
- [ ] `/recomendacoes/` + 2 subpages
- [ ] `/en/` loads
- [ ] RSS feed `https://new.marcelioleal.com/index.xml` is valid XML
- [ ] Sitemap `https://new.marcelioleal.com/sitemap.xml` lists every slug
- [ ] 404 page renders (e.g. `/does-not-exist-abc123/`)
- [ ] Search box (Pagefind) returns results for "paraense"

---

## D-1 — Dry-run (day before)

### D-1.1 Rebuild the Hugo site locally
```bash
cd ~/workspace/newsite
rm -rf public resources .hugo_build.lock
hugo --gc --minify
```
Expect: zero build errors, warnings OK.

### D-1.2 Confirm Netlify build pipeline green
- [ ] Netlify dashboard → Deploys → last build is green.
- [ ] If red: fix before D-day.

### D-1.3 Re-run pre-flight crawl
```bash
cd ~/workspace/newsite
./scripts/preflight_crawl.sh
```
Expect: 121 pass, 1 fail (`1º-de-maio` known gap). If any OTHER failure appears, debug before D-day — do not cut with a regression.

### D-1.4 Verify TTL dropped to 300
```bash
dig +short marcelioleal.com @8.8.8.8 | /usr/bin/head -3
dig marcelioleal.com @8.8.8.8 | /usr/bin/grep -A1 "ANSWER SECTION"
```
Expect: current A records with TTL `300` (or less by now).

### D-1.5 Prep a terminal with the DNS and Netlify tabs open
D-day is faster if you're not clicking around.

---

## D-day — The cut (~30 min window)

**Pick a low-traffic weeknight (e.g. Tuesday 21h-22h BRT).** Never Friday.

### D.1 Sanity re-check (T-5 min)
```bash
PATH=/usr/bin:/bin
/usr/bin/curl -sI https://new.marcelioleal.com/ | /usr/bin/head -1
# Expect: HTTP/2 200
```

### D.2 Flip `hugo.toml` baseURL
```bash
cd ~/workspace/newsite
# Edit hugo.toml:
#   baseURL = "https://marcelioleal.com/"   (was: new.marcelioleal.com)
# Also check netlify.toml for any new.marcelioleal.com reference.
```

In `netlify.toml`, update `HUGO_ENV` from `staging` to `production` under `[context.production.environment]`:
```toml
[context.production.environment]
HUGO_ENV = "production"
```
The staging `HUGO_ENV` made PaperMod emit `<meta robots="noindex">` — flipping to `production` removes that so Google can index.

Commit and push:
```bash
git add hugo.toml netlify.toml
git commit -m "cutover: flip baseURL to apex marcelioleal.com + HUGO_ENV=production"
git push origin main
```
Netlify will start building. Keep the deploy tab open; wait for it to go green (~90s).

### D.3 Point DNS to Netlify (T-0)
At `<REGISTRAR>` DNS panel:

**Apex (`marcelioleal.com`):**
- Delete current `A` records.
- Add new `A` record (one is enough; Netlify advertises `75.2.60.5` publicly, but check the exact values Netlify tells you after you added the domain in D-7.5):
  ```
  A   75.2.60.5    TTL=300
  ```
- If your registrar supports `ALIAS` or `ANAME` for apex, prefer that pointing to `apex-loadbalancer.netlify.com` — it's more future-proof than hard-coding IPs.

**WWW (`www.marcelioleal.com`):**
- Change the CNAME to:
  ```
  CNAME   <NETLIFY_SITE_NAME>.netlify.app    TTL=300
  ```

**Leave untouched:** MX, TXT (SPF/DKIM), any NS records.

### D.4 Wait for propagation (~5 min thanks to low TTL)
```bash
PATH=/usr/bin:/bin
for i in 1 2 3 4 5 6 7 8 9 10; do
  /bin/sleep 30
  ip=$(/usr/bin/dig +short marcelioleal.com @8.8.8.8 | /usr/bin/head -1)
  echo "try $i: marcelioleal.com → $ip"
  if [ "$ip" = "75.2.60.5" ]; then echo "✓ DNS switched"; break; fi
done
```

### D.5 Confirm TLS cert on apex
```bash
PATH=/usr/bin:/bin
/usr/bin/curl -sI https://marcelioleal.com/ | /usr/bin/head -1
# Expect: HTTP/2 200
# Error? Netlify is auto-provisioning the Let's Encrypt cert.
# Wait ~2 min and retry. If still broken, check Netlify Domain settings → TLS.
```

### D.6 Verify 3 critical URL patterns on apex
```bash
PATH=/usr/bin:/bin
for u in \
  "/" \
  "/sobre/" \
  "/recomendacoes/cafes/" \
  "/2024/03/11/o-que-e-software-em-2024-com-a-inteligencia-articial-ainda-precisaremos-programar/" \
  "/sobre-mim/"; do
  out=$(/usr/bin/curl -sIL -w "%{http_code}|%{url_effective}" "https://marcelioleal.com$u" 2>/dev/null | /usr/bin/tail -1)
  echo "$u → $out"
done
```
All 5 should end with HTTP 200 on the correct Hugo URL.

### D.7 Set apex as primary in Netlify
Netlify dashboard → Domain settings → **Set `marcelioleal.com` as primary domain**. This makes `www` 301 to apex (or vice-versa — pick one canonical and stick with it).

**Recommendation: apex as canonical.** Shorter, matches current branding.

### D.8 Re-submit sitemap to Google Search Console
- [ ] Add a new property `https://marcelioleal.com` (if not already there).
- [ ] Sitemaps → Submit `https://marcelioleal.com/sitemap.xml`.
- [ ] Also submit `https://marcelioleal.com/en/sitemap.xml` if one exists.

**CUT DONE. Start the watch.**

---

## D+0 (same night) — smoke test

- [ ] Open the site in an incognito window. Does it look right?
- [ ] Test a shared link from social: paste `https://marcelioleal.com/` in a tweet (don't post).
- [ ] Visit at least 3 posts from different years.
- [ ] Test the newsletter signup form.
- [ ] Check theme toggle works.

If anything major broken: see [Rollback](#rollback-procedure-any-day) below.

---

## D+1 to D+7 — First week monitoring

### Daily checks (5 min)
- [ ] Google Search Console → **Coverage** report → "Pages with errors" count. Should trend flat or down.
- [ ] Google Search Console → **Performance** → compare daily impressions vs prior week. A 10-30% dip is normal during index swap; >50% is red flag.
- [ ] Netlify → **Analytics** (or Umami/Plausible if set up) → compare daily unique visitors vs prior 7-day avg. Same tolerance.
- [ ] Netlify → **Functions/Logs** → scan for spike in 4xx/5xx.
- [ ] `curl https://marcelioleal.com/ | head` → confirm still serving Hugo.

### When Search Console flags 404s
1. Note the exact URL pattern.
2. If it's one of the [known gaps](#known-gaps-accepted-pre-cut), check in. If a real surge, address:
   - Add manual entry to `static/_redirects` (above the generated section) matching the pattern.
   - Commit, push. Netlify auto-deploys in ~1 min.

### When traffic drops >50%
Immediate rollback consideration — see [Rollback](#rollback-procedure-any-day). Most likely cause: DNS record not propagated to a large resolver. Check with `dig @1.1.1.1`, `dig @8.8.8.8`, `dig @9.9.9.9`.

---

## D+14 — Decommission WordPress

Only proceed if the first week was calm. Any unresolved incident → extend the monitoring window.

### D+14.1 Final WordPress backup
- [ ] Re-export (D-7 backup is 3 weeks old by now).
- [ ] Verify the backup opens / unzips correctly.
- [ ] Store in 2 places (local + cloud).

### D+14.2 Downgrade / cancel hosting
- [ ] If on WordPress.com: downgrade to free plan (keeps account open but stops billing), or delete site entirely after exporting.
- [ ] If on self-hosted: stop the WP service, keep the hosting server for 30 more days as rollback cushion.

### D+14.3 Cancel domain-attached subscriptions
- [ ] Jetpack, Yoast, any premium plugin subscriptions.
- [ ] Email forwarding (if moved to a different provider).
- [ ] Any analytics (GA/Clicky/etc. account can stay — property still relevant).

### D+14.4 Update tooling that referenced the old WP
- [ ] Remove WP from any CI secrets.
- [ ] Update `.env` files, API keys, cron jobs.

### D+14.5 Mark the roadmap complete
Update `.aimi/tasks/wordpress-to-hugo-migration/roadmap.json`:
```json
{"id": 3, "status": "completed"}
```
Then move on to Phase 3.5 (custom images CDN).

---

## Rollback procedure (any day)

If the cut goes wrong (site serving wrong content, major 5xx, cert fails and won't provision):

### Scenario A: pre-D+1 (within hours)
1. At `<REGISTRAR>` DNS panel: restore the original A/CNAME records from `backups/dns-pre-cutover.txt`.
2. DNS propagates in ~5 min thanks to lowered TTL.
3. WordPress is back live — nothing on WP was touched.
4. Netlify keeps serving `new.marcelioleal.com` as always (staging subdomain unaffected).
5. Investigate the failure, fix, retry.

### Scenario B: D+2 to D+7
Same as A, but Google may have already started indexing the new URLs. After restoring:
- Submit a "URL removal request" in Search Console for any already-indexed /new/ URLs that shouldn't be there.
- Expect 2-3 days for Google to re-crawl the restored WP state.

### Scenario C: D+8+ (post-decommission window, before D+14)
WP hosting is still paid. Follow A/B.

### Scenario D: Post-D+14
WP is gone. No rollback. Any residual issue has to be fixed forward on Hugo.

---

## Backup procedure (monthly, ongoing)

Per the project memory: a monthly backup procedure ships WITH Phase 3, not before.

### Hugo backup (automated)
GitHub is the single source of truth — `git clone git@github.com:marcelioleal/newsite.git` gets you everything **except** media that lives in R2.

For the R2 media, add this cron entry (macOS LaunchAgent or crontab):
```cron
# First Sunday of each month, 03:00, snapshot R2 to a dated prefix
0 3 1-7 * 0 /usr/local/bin/rclone sync r2:marcelioleal-images r2:marcelioleal-images-backup/$(date +\%Y-\%m) --fast-list
```
(adjust `rclone` path per `which rclone`)

### WordPress backup (one-shot, D-7)
Already covered in D-7.2 above. After D+14 this no longer applies.

---

## Appendix — files touched during cutover

| File | Change | Diff size |
|---|---|---|
| `hugo.toml` | `baseURL = "https://marcelioleal.com/"` | 1 line |
| `netlify.toml` | `HUGO_ENV = "production"` under `[context.production.environment]` | 1 line |
| (optional) `README.md` | update deploy URL references from `new.marcelioleal.com` to `marcelioleal.com` | a few lines |
| (optional) `content/pt-br/posts/**/*.md` | any absolute-URL self-references | zero if the migration used relative |

Total code diff for the cutover itself: **~2 lines**. The real work is DNS + monitoring.
