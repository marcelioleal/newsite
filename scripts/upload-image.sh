#!/usr/bin/env bash
# Upload a single new image (or a dir of images) to Cloudflare R2.
#
# Usage:
#   ./scripts/upload-image.sh path/to/local/image.jpg
#   ./scripts/upload-image.sh path/to/local/dir/
#
# Behaviour:
#   - Reads R2 credentials from env (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
#     R2_ENDPOINT, R2_PUBLIC_URL) or from ./.env.r2 if present.
#   - Resolves the remote key from the local path:
#       static/images-source/2026/11/foo.jpg → 2026/11/foo.jpg
#       any absolute path → basename only, prompted for year/month if missing
#   - Uploads with rclone (same flags as the migration script).
#   - Prints the public CDN URL to stdout so the caller can pipe to pbcopy.

set -euo pipefail

# Load .env.r2 if present (gitignored)
if [ -f .env.r2 ]; then
  set -a; source .env.r2; set +a
fi

: "${R2_ACCESS_KEY_ID:?set R2_ACCESS_KEY_ID in env or .env.r2}"
: "${R2_SECRET_ACCESS_KEY:?set R2_SECRET_ACCESS_KEY in env or .env.r2}"
: "${R2_ENDPOINT:?set R2_ENDPOINT in env or .env.r2}"
: "${R2_PUBLIC_URL:?set R2_PUBLIC_URL in env or .env.r2}"

[ $# -ge 1 ] || { echo "Usage: $0 <path-to-image-or-dir>"; exit 2; }
SRC="$1"
[ -e "$SRC" ] || { echo "Error: $SRC does not exist"; exit 1; }

BUCKET="marcelioleal-images"
REMOTE="r2:${BUCKET}"

export RCLONE_CONFIG_R2_TYPE="s3"
export RCLONE_CONFIG_R2_PROVIDER="Cloudflare"
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID}"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY}"
export RCLONE_CONFIG_R2_ENDPOINT="${R2_ENDPOINT}"

# Derive the remote key. If the local path is under static/images-source/,
# strip that prefix. Otherwise use the path verbatim (caller specifies the
# folder layout under R2).
if [[ "$SRC" == static/images-source/* ]]; then
  REMOTE_KEY="${SRC#static/images-source/}"
else
  REMOTE_KEY="$SRC"
fi

echo "Uploading $SRC → $REMOTE/$REMOTE_KEY"
if [ -d "$SRC" ]; then
  rclone copy "$SRC" "$REMOTE/$REMOTE_KEY" \
    --progress --s3-no-check-bucket \
    --transfers 8 --s3-chunk-size 16M
else
  rclone copy "$SRC" "$REMOTE/$(dirname "$REMOTE_KEY")/" \
    --progress --s3-no-check-bucket
fi

echo ""
echo "Public URL(s):"
if [ -d "$SRC" ]; then
  find "$SRC" -type f | while read -r f; do
    rel="${f#"$SRC"/}"
    echo "  ${R2_PUBLIC_URL}/${REMOTE_KEY}/${rel}"
  done
else
  echo "  ${R2_PUBLIC_URL}/${REMOTE_KEY}"
fi
