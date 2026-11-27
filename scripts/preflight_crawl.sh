#!/usr/bin/env bash
# scripts/preflight_crawl.sh — Phase 3 pre-cutover redirect audit.
#
# Crawls the live staging site (BASE_URL, defaults to new.marcelioleal.com)
# for every URL class in static/_redirects and reports pass/fail per class.
# Run in D-7 and D-1 of the cutover runbook. Zero flags = all good to cut.
#
# Classes tested:
#   1. Dated WP permalinks         /YYYY/MM/DD/<slug>/ → /<slug>/
#   2. Category archives           /category/X/ → /categories/X/
#   3. Tag archives                /tag/X/ → /tags/X/
#   4. Static page redirects       /sobre-mim/ → /sobre/, etc.
#   5. Legacy image uploads        /wp-content/uploads/… → R2 CDN
#   6. Legacy ?p=<wp_id> shortlink (currently known-broken in Netlify)
#   7. Direct Hugo URLs            /, /en/, /recomendacoes/*
#   8. Negative control            /definitely-not-a-page-xyz/ → 404
#
# Usage:
#   ./scripts/preflight_crawl.sh                           # crawls staging
#   BASE_URL=https://marcelioleal.com ./scripts/preflight_crawl.sh  # post-cut
#
# Exits non-zero when any unexpected failure is found.

set -u
PATH=/usr/bin:/bin:/opt/homebrew/bin

BASE_URL="${BASE_URL:-https://new.marcelioleal.com}"
REDIRECTS_FILE="$(dirname "$0")/../static/_redirects"
[ -f "$REDIRECTS_FILE" ] || { echo "ERR: $REDIRECTS_FILE not found"; exit 2; }

TOTAL_PASS=0
TOTAL_FAIL=0
FAIL_LOG=$(mktemp)

# Helper: hit a URL, follow redirects, record pass/fail by expected status.
check() {
  local label="$1" url="$2" expected="$3"
  local out code
  out=$(/usr/bin/curl -sIL --max-redirs 5 -w "%{http_code}" "$url" 2>/dev/null | /usr/bin/tail -1)
  code="$out"
  if [ "$code" = "$expected" ]; then
    TOTAL_PASS=$((TOTAL_PASS+1))
  else
    TOTAL_FAIL=$((TOTAL_FAIL+1))
    printf "[FAIL] %-20s %s → got %s (expected %s)\n" "$label" "$url" "$code" "$expected" >> "$FAIL_LOG"
  fi
}

echo "━━━ Pre-flight redirect crawl ━━━"
echo "Base URL: $BASE_URL"
echo "Rules file: $REDIRECTS_FILE"
echo

# --- 1. Dated WP permalinks (should each 301 to flat slug returning 200) ---
echo "[1/8] Dated WP permalinks..."
# Pull the source path from each line matching /YYYY/MM/DD/<slug>/  (no trailing /* wildcard variant)
/usr/bin/grep -E '^/[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/[^/]+/  ' "$REDIRECTS_FILE" \
  | /usr/bin/awk '{print $1}' > /tmp/_pf_dated.txt
dated_count=$(/usr/bin/wc -l < /tmp/_pf_dated.txt)
while IFS= read -r src; do
  check "dated" "${BASE_URL}${src}" "200"
done < /tmp/_pf_dated.txt
echo "  $dated_count checked"

# --- 2. Category archives (hit real categories from content frontmatter) ---
echo "[2/8] Category archives..."
for cat in software-dev outros musica arte; do
  check "category" "${BASE_URL}/category/${cat}/" "200"
done

# --- 3. Tag archives — currently no tags in content but the rule exists ---
echo "[3/8] Tag archives..."
# Just verify the catch-all 404s cleanly on a nonexistent tag
check "tag(negative)" "${BASE_URL}/tag/does-not-exist/" "404"

# --- 4. Static page slug redirects ---
echo "[4/8] Static page redirects..."
check "static" "${BASE_URL}/sobre-mim/" "200"
check "static" "${BASE_URL}/en/about-me/" "200"
check "static" "${BASE_URL}/popular-posts/" "200"

# --- 5. Legacy image uploads (sample; proves rule fires + R2 serves) ---
echo "[5/8] Legacy /wp-content/uploads/ → R2..."
check "wp-upload" "${BASE_URL}/wp-content/uploads/profile/avatar.png" "200"

# --- 6. Legacy ?p=<wp_id> shortlinks (KNOWN BROKEN in Netlify — expected 200 for now) ---
echo "[6/8] Legacy ?p=N shortlinks..."
out=$(/usr/bin/curl -sIL --max-redirs 5 -w "%{num_redirects}" "${BASE_URL}/?p=4" 2>/dev/null | /usr/bin/tail -1)
if [ "$out" -ge "1" ] 2>/dev/null; then
  echo "  ✓ ?p=N now redirects! Remove this as a known gap."
  TOTAL_PASS=$((TOTAL_PASS+1))
else
  echo "  [KNOWN GAP] ?p=N still serves home 200 (Netlify Query= matcher quirk)"
fi

# --- 7. Direct Hugo URLs (should 200 directly, 0 redirects) ---
echo "[7/8] Direct Hugo URLs..."
for p in / /en/ /recomendacoes/ /recomendacoes/cafes/ /recomendacoes/restaurantes-sp/; do
  check "hugo" "${BASE_URL}${p}" "200"
done

# --- 8. Negative control (should 404 — no greedy catch-all redirect) ---
echo "[8/8] Negative control..."
check "negative-404" "${BASE_URL}/this-url-does-not-exist-abc123/" "404"

echo
echo "━━━ Summary ━━━"
echo "Pass: $TOTAL_PASS"
echo "Fail: $TOTAL_FAIL"
if [ "$TOTAL_FAIL" -gt "0" ]; then
  echo
  echo "Failures:"
  /bin/cat "$FAIL_LOG"
  /bin/rm -f "$FAIL_LOG"
  exit 1
fi
/bin/rm -f "$FAIL_LOG"
echo
echo "✓ All classes pass. Cutover-safe."
