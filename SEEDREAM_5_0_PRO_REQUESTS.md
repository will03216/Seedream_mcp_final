# Seedream 5.0 Pro — Request Reference & Permutations

**Model ID:** `dola-seedream-5-0-pro-260628` (public alias `seedream-5-0-pro-260628`)
**Endpoint:** `POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`
**Auth:** `Authorization: Bearer $ARK_API_KEY` (API Key only — no AK/SK for the generation call)
**Synchronous:** one call returns the finished image(s). No task polling.

Sources: [API reference](https://docs.byteplus.com/en/docs/ModelArk/1541523) ·
[User guide](https://docs.byteplus.com/en/docs/ModelArk/1824121). Verified live 2026-07-08.

### Regions
| Region | Base URL |
|---|---|
| ap-southeast-1 | `https://ark.ap-southeast.bytepluses.com/api/v3` |
| eu-west-1 | `https://ark.eu-west.bytepluses.com/api/v3` |

---

## Capabilities (Pro-specific)
- ✅ Text-to-image
- ✅ Single image-to-image (edit)
- ✅ Multi-reference image-to-image — **up to 10 reference images** (Lite/4.5/4.0 allow 14)
- ❌ Batch / sequential (`sequential_image_generation`) — **not supported, errors**
- ❌ Streaming (`stream`) — **not supported, errors**
- ❌ `guidance_scale` — **not supported, errors**
- Single image output only.

---

## Parameters

| Param | Type | Req | Default | Pro notes |
|---|---|---|---|---|
| `model` | string | ✅ | — | `dola-seedream-5-0-pro-260628` |
| `prompt` | string | ✅ | — | ≤ ~600 English words |
| `image` | string \| array | — | — | i2i / multi-ref. Public URL or `data:image/<fmt>;base64,<...>`. Up to **10** images |
| `size` | string | — | `1024x1024` | Presets **`1K`, `2K`** *(no `4K`)*, or `WxH` px (see below) |
| `output_format` | string | — | `jpeg` | `png` \| `jpeg` (Pro & Lite only) |
| `response_format` | string | — | `url` | `url` (24h link) \| `b64_json` |
| `watermark` | boolean | — | `true` | set `false` to disable |
| `optimize_prompt_options` | object | — | — | `{ "mode": "standard" \| "fast" }` (default `standard`) |
| `seed` | integer | — | — | Doc: only `seedream-3-0-t2i`. On Pro it's **accepted but ignored** (no error) |
| `sequential_image_generation` | string | — | — | ⛔ errors on Pro |
| `sequential_image_generation_options` | object | — | — | ⛔ errors on Pro |
| `stream` | boolean | — | — | ⛔ errors on Pro |
| `guidance_scale` | float | — | — | ⛔ errors on Pro |

### `size` rules (Pro)
- **Method 1 — explicit `"WIDTHxHEIGHT"` px:** total pixels in `[1280x720 = 921,600 , 2048x2048 = 4,194,304]`, must be a **multiple of 16**, aspect ratio (w/h) in `[1/16, 16]`. e.g. `2048x1024` ✅, `512x512` ❌ (too few px).
- **Method 2 — preset:** `1K` (~1024²) or `2K` (~4.19M px). `4K` → `InvalidParameter`.
- The model auto-selects aspect from the prompt when a preset is used (returns e.g. portrait/landscape, not forced square).

### `image` input constraints (per reference image)
- Formats: `jpeg, png, webp, bmp, tiff, gif, heic, heif`
- Aspect (w/h) `[1/16, 16]`; width & height `> 14 px`; ≤ 30 MB; total px ≤ `6000x6000 = 36,000,000`
- Base64 must be `data:image/<lowercase-fmt>;base64,<data>`

### Response body
```jsonc
{
  "model": "dola-seedream-5-0-pro",
  "created": 1783516294,
  "data": [{ "url": "https://...jpeg", "size": "1760x2352", "output_format": "jpeg" }],
  // response_format=b64_json -> data[].b64_json instead of url
  "usage": { "generated_images": 1, "input_images": 0, "output_tokens": 16170, "total_tokens": 16170 },
  "error": null
  // output_tokens = sum(image_w * image_h) / 256
}
```

---

## Permutations — ready-to-run

All use `-H "Authorization: Bearer $ARK_API_KEY" -H "Content-Type: application/json"`.
Base: `ARK="https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"`

### 1. Text-to-image, minimal (defaults: jpeg, url, watermark on)
```bash
curl -sS -X POST "$ARK" -H "Authorization: Bearer $ARK_API_KEY" -H "Content-Type: application/json" -d '{
  "model": "dola-seedream-5-0-pro-260628",
  "prompt": "A sunlit ceramic mug of iced cold brew on an oak table by a window"
}'
```

### 2. T2I, preset 2K, no watermark
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...", "size": "2K", "watermark": false }
```

### 3. T2I, preset 1K
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...", "size": "1K", "watermark": false }
```

### 4. T2I, explicit dimensions (landscape 2048x1024)
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...", "size": "2048x1024", "watermark": false }
```

### 5. T2I, PNG output
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...", "size": "1K", "output_format": "png", "watermark": false }
```

### 6. T2I, base64 response
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...", "size": "1K", "response_format": "b64_json", "watermark": false }
```

### 7. T2I, fast prompt-optimization
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...", "size": "2K",
  "optimize_prompt_options": { "mode": "fast" }, "watermark": false }
```

### 8. Image-to-image (single reference, URL)
```json
{ "model": "dola-seedream-5-0-pro-260628",
  "prompt": "same fox, now standing alert in a summer green forest",
  "image": "https://.../fox.jpeg", "size": "2K", "watermark": false }
```

### 9. Multi-reference image-to-image (up to 10, array)
```json
{ "model": "dola-seedream-5-0-pro-260628",
  "prompt": "blend the character in image 1 with the outfit in image 2, studio lighting",
  "image": ["https://.../char.jpg", "https://.../outfit.jpg"],
  "size": "2K", "watermark": false }
```

### 10. Image-to-image with base64 input
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...",
  "image": "data:image/png;base64,<BASE64>", "size": "2K", "watermark": false }
```

### 11. Full-options T2I
```json
{ "model": "dola-seedream-5-0-pro-260628", "prompt": "...",
  "size": "2K", "output_format": "png", "response_format": "url",
  "watermark": false, "optimize_prompt_options": { "mode": "standard" } }
```

---

## ⛔ Invalid on Pro (return `InvalidParameter`)
```json
{ "...": "...", "size": "4K" }                              // preset not supported
{ "...": "...", "sequential_image_generation": "auto" }     // batch unsupported
{ "...": "...", "sequential_image_generation_options": {} } // batch unsupported
{ "...": "...", "stream": true }                            // streaming unsupported
{ "...": "...", "guidance_scale": 5 }                       // unsupported
{ "...": "...", "size": "512x512" }                         // below min total pixels (921,600)
```
`seed` does **not** error but has no effect on Pro.

---

## Verified live (2026-07-08)
| Permutation | Result |
|---|---|
| T2I 2K | ✅ 1760×2352 jpeg |
| T2I 1K | ✅ 1024×1024 jpeg |
| T2I `2048x1024` | ✅ 2048×1024 jpeg |
| `output_format: png` | ✅ png |
| i2i single URL ref | ✅ 2496×1664 |
| `size: 4K` | ❌ InvalidParameter |
| `sequential_image_generation` | ❌ InvalidParameter |
| `stream` | ❌ InvalidParameter |
| `guidance_scale` | ❌ InvalidParameter |
| `seed` | ✅ accepted, ignored |
