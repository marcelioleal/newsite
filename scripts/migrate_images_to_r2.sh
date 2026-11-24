#!/usr/bin/env bash
# Upload static/images/** to Cloudflare R2 using rclone (S3-compatible).
#
# Required env vars (never commit these):
#   R2_ACCESS_KEY_ID
#   R2_SECRET_ACCESS_KEY
#   R2_ENDPOINT          — e.g. https://<account-id>.r2.cloudflarestorage.com
#   R2_PUBLIC_URL        — e.g. https://pub-XXXX.r2.dev
#
# Required bucket (pre-created in Cloudflare dashboard):
#   marcelioleal-images
#
# Usage:
#   ./scripts/migrate_images_to_r2.sh --dry-run  # list, no upload
#   ./scripts/migrate_images_to_r2.sh            # upload for real
#   ./scripts/migrate_images_to_r2.sh --verify   # HEAD check sample after upload

set -euo pipefail

: "${R2_ACCESS_KEY_ID:?set R2_ACCESS_KEY_ID in env}"
: "${R2_SECRET_ACCESS_KEY:?set R2_SECRET_ACCESS_KEY in env}"
: "${R2_ENDPOINT:?set R2_ENDPOINT in env}"
: "${R2_PUBLIC_URL:?set R2_PUBLIC_URL in env}"

BUCKET="marcelioleal-images"
SOURCE_DIR="static/images"
REMOTE="r2:${BUCKET}"

# Build rclone env-var config inline so we never write secrets to disk.
export RCLONE_CONFIG_R2_TYPE="s3"
export RCLONE_CONFIG_R2_PROVIDER="Cloudflare"
export RCLONE_CONFIG_R2_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID}"
export RCLONE_CONFIG_R2_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY}"
export RCLONE_CONFIG_R2_ENDPOINT="${R2_ENDPOINT}"
# NOTE: R2 ignores per-object ACL (public access is bucket-level). No ACL env.
# NOTE: --s3-no-check-bucket is passed as a flag below — the API token has
# Object R/W only, so rclone's default CreateBucket precheck would 401.

cmd="${1:-upload}"

case "$cmd" in
  --test|test)
    echo "=== TEST: read-only probe on remote bucket ==="
    echo "(expect: lists objects or 'empty' with no error)"
    rclone ls "$REMOTE" --s3-no-check-bucket --max-depth 1 2>&1 | head -10
    exit $?
    ;;

  --dry-run|dry-run)
    echo "=== DRY RUN: would upload the following files ==="
    rclone lsf -R "$SOURCE_DIR" | wc -l | xargs printf "File count: %s\n"
    du -sh "$SOURCE_DIR"
    echo ""
    echo "Preview (first 20):"
    rclone lsf -R "$SOURCE_DIR" | head -20
    echo ""
    echo "Nothing uploaded. Run without --dry-run to execute."
    ;;

  upload|"")
    echo "=== Uploading $SOURCE_DIR → $REMOTE ==="
    rclone copy "$SOURCE_DIR" "$REMOTE" \
      --progress \
      --transfers 16 \
      --checkers 32 \
      --fast-list \
      --s3-no-check-bucket \
      --s3-chunk-size 16M \
      --s3-upload-concurrency 8
    echo ""
    echo "=== Upload complete. Verifying file count ==="
    local_count=$(find "$SOURCE_DIR" -type f | wc -l | tr -d ' ')
    remote_count=$(rclone lsf -R "$REMOTE" --s3-no-check-bucket --files-only | wc -l | tr -d ' ')
    echo "Local: $local_count files"
    echo "Remote: $remote_count files"
    if [ "$local_count" != "$remote_count" ]; then
      echo "⚠️  Count mismatch — investigate before proceeding."
      exit 1
    fi
    echo "✅ File counts match."
    ;;

  --verify|verify)
    echo "=== HEAD check: 5 random public URLs ==="
    find "$SOURCE_DIR" -type f | shuf -n 5 | while read -r f; do
      rel="${f#"$SOURCE_DIR"/}"
      url="${R2_PUBLIC_URL}/${rel}"
      code=$(curl -sI -o /dev/null -w "%{http_code}" "$url")
      printf "%s  %s\n" "$code" "$url"
    done
    ;;

  *)
    echo "Usage: $0 [--dry-run|--verify|upload]"
    exit 2
    ;;
esac
