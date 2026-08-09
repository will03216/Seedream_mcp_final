#!/usr/bin/env bash
# Build one JSON request body per scenario in prompts.json, with local
# reference images embedded as base64 data-URIs (Seedream 5.0 Pro, i2i).
# Output: payloads/<scenario_id>.json  (ready for: curl --data-binary @payloads/<id>.json)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALMART="$(dirname "$HERE")"
PROMPTS="$WALMART/prompts.json"
OUT="$HERE/payloads"
MODEL="dola-seedream-5-0-pro-260628"
SIZE="2K"
mkdir -p "$OUT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Write a data-URI (no trailing newline) for a local image into $1.
write_data_uri() {
  local dest="$1" path="$2" ext mime
  ext="$(echo "${path##*.}" | tr '[:upper:]' '[:lower:]')"
  case "$ext" in
    png) mime=image/png ;; webp) mime=image/webp ;; bmp) mime=image/bmp ;;
    gif) mime=image/gif ;; tif|tiff) mime=image/tiff ;;
    heic) mime=image/heic ;; heif) mime=image/heif ;;
    *) mime=image/jpeg ;;
  esac
  printf 'data:%s;base64,' "$mime" > "$dest"
  base64 < "$path" | tr -d '\n' >> "$dest"
}

count="$(jq '.examples | length' "$PROMPTS")"
for i in $(seq 0 $((count-1))); do
  sid="$(jq -r ".examples[$i].scenario_id" "$PROMPTS")"
  prompt="$(jq -r ".examples[$i].prompt" "$PROMPTS")"
  imgs=()
  while IFS= read -r line; do imgs+=("$line"); done \
    < <(jq -r ".examples[$i].input_images[]" "$PROMPTS")

  echo "building $sid (${#imgs[@]} refs)..."

  jq -n --arg m "$MODEL" --arg p "$prompt" --arg s "$SIZE" \
    '{model:$m, prompt:$p, size:$s, watermark:false}' > "$TMP/body.json"

  if [ "${#imgs[@]}" -eq 1 ]; then
    write_data_uri "$TMP/u.txt" "$WALMART/${imgs[0]}"
    jq --rawfile u "$TMP/u.txt" '.image=$u' "$TMP/body.json" > "$OUT/$sid.json"
  elif [ "${#imgs[@]}" -gt 1 ]; then
    # build the image array file-by-file to avoid arg-length limits
    echo '[]' > "$TMP/arr.json"
    n=0
    for f in "${imgs[@]}"; do
      write_data_uri "$TMP/u.txt" "$WALMART/$f"
      jq --rawfile u "$TMP/u.txt" '. += [$u]' "$TMP/arr.json" > "$TMP/arr.next"
      mv "$TMP/arr.next" "$TMP/arr.json"
      n=$((n+1))
    done
    jq --slurpfile a "$TMP/arr.json" '.image=$a[0]' "$TMP/body.json" > "$OUT/$sid.json"
  else
    cp "$TMP/body.json" "$OUT/$sid.json"
  fi
  echo "  -> payloads/$sid.json ($(du -h "$OUT/$sid.json" | cut -f1))"
done
echo "done."
