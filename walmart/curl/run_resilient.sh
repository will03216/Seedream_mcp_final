#!/usr/bin/env bash
# Resilient runner for large multi-ref payloads: retries the whole
# generate+download up to N times, verifies the JPEG ends in FFD9 (EOI).
#   ARK_API_KEY=... ./run_resilient.sh <scenario_id> [<scenario_id> ...]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALMART="$(dirname "$HERE")"
OUTDIR="$WALMART/output_1"
ENDPOINT="https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
: "${ARK_API_KEY:?Set ARK_API_KEY}"
mkdir -p "$OUTDIR"
MAX=4

valid_jpeg() { [ -s "$1" ] && [ "$(tail -c2 "$1" | xxd -p)" = "ffd9" ]; }

run_one() {
  local sid="$1" payload="$HERE/payloads/$1.json" out="$OUTDIR/$1.jpeg"
  local attempt=1
  while [ "$attempt" -le "$MAX" ]; do
    echo "[RUN ] $sid (attempt $attempt/$MAX) ..."
    resp="$(curl -sS --connect-timeout 30 --max-time 600 --retry 2 --retry-connrefused \
      -X POST "$ENDPOINT" -H "Authorization: Bearer $ARK_API_KEY" \
      -H "Content-Type: application/json" --data-binary "@$payload")"
    url="$(printf '%s' "$resp" | jq -r '.data[0].url // empty')"
    if [ -z "$url" ]; then
      echo "[warn] $sid: no url: $(printf '%s' "$resp" | jq -c '.error // .' | cut -c1-220)"
      attempt=$((attempt+1)); sleep 5; continue
    fi
    size="$(printf '%s' "$resp" | jq -r '.data[0].size')"
    curl -sS --connect-timeout 30 --max-time 300 --retry 3 --retry-all-errors \
      -C - "$url" -o "$out" || true
    if valid_jpeg "$out"; then
      echo "[ OK ] $sid -> output_1/$sid.jpeg ($size)"; return 0
    fi
    echo "[warn] $sid: download incomplete, retrying..."
    rm -f "$out"; attempt=$((attempt+1)); sleep 5
  done
  echo "[FAIL] $sid after $MAX attempts"; return 1
}

for sid in "$@"; do run_one "$sid"; done
echo "ALL DONE"
