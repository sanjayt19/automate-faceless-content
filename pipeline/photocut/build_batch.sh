#!/usr/bin/env bash
# Render several Photo Cut reels back to back inside one sandbox lease.
#
#   REF=<sha> build_batch.sh <key>=<upload-url> [<key>=<upload-url> ...]
#
# Each reel uploads the moment it finishes and drops a marker, so a rerun after
# a lease expiry skips whatever already landed.
set -uo pipefail

REF="${REF:-claude/automated-video-shorts-lq2gya}"
RAW="https://raw.githubusercontent.com/sanjayt19/automate-faceless-content/$REF/pipeline/photocut"
ROOT=/home/user/pcut
mkdir -p "$ROOT/assets" "$ROOT/done"
cd "$ROOT"
for f in build_photocut.sh; do curl -fsSL --retry 3 "$RAW/$f" -o "$f"; done
for f in resolve.py urls.json stills.json narration.json; do
  curl -fsSL --retry 3 "$RAW/assets/$f" -o "assets/$f"
done

for arg in "$@"; do
  KEY="${arg%%=*}"; UP="${arg#*=}"
  if [ -f "done/$KEY" ]; then echo "SKIP $KEY (already built)"; continue; fi
  echo "=== $KEY"
  NARR=$(python3 assets/resolve.py "$KEY" "$ROOT/$KEY-urls.json") || { echo "RESOLVE FAILED $KEY"; continue; }
  if REF="$REF" bash build_photocut.sh "$KEY" "$NARR" "$ROOT/$KEY-urls.json" "$UP"; then
    touch "done/$KEY"
  else
    echo "BUILD FAILED $KEY"
  fi
done
echo "BATCH COMPLETE"
