#!/usr/bin/env bash
# Send a prepared payload to Seedream 5.0 Pro and save the returned image.
#   ARK_API_KEY=... ./run.sh <scenario_id>
#   ARK_API_KEY=... ./run.sh --all
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALMART="$(dirname "$HERE")"
OUTDIR="$WALMART/output"
ENDPOINT="https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
: "${ARK_API_KEY:?Set ARK_API_KEY (BytePlus ModelArk bearer token)}"
mkdir -p "$OUTDIR"

send() {
  local sid="$1" payload="$HERE/payloads/$1.json"
  [ -f "$payload" ] || { echo "[SKIP] $sid: no payload (run build_payloads.sh)"; return; }
  echo "[RUN ] $sid ..."
  local resp; resp="$(curl -sS -X POST "$ENDPOINT" \
    -H "Authorization: Bearer $ARK_API_KEY" \
    -H "Content-Type: application/json" \
    --data-binary "@$payload")"
  local url; url="$(printf '%s' "$resp" | jq -r '.data[0].url // empty')"
  if [ -z "$url" ]; then
    echo "[FAIL] $sid: $(printf '%s' "$resp" | jq -c '.error // .' | cut -c1-300)"
    return
  fi
  curl -sS "$url" -o "$OUTDIR/$sid.jpeg"
  echo "[ OK ] $sid -> output/$sid.jpeg ($(printf '%s' "$resp" | jq -r '.data[0].size'))"
}

if [ "${1:-}" = "--all" ]; then
  for f in "$HERE"/payloads/*.json; do send "$(basename "$f" .json)"; done
else
  [ $# -ge 1 ] || { echo "usage: ARK_API_KEY=... $0 <scenario_id> | --all"; exit 1; }
  send "$1"
fi
