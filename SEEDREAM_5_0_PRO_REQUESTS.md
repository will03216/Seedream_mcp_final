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
- ✅ **Layer decomposition** (`layer_decomposition`) — split one input image into separate
  layers (text groups, subjects, background), one output image per layer. Pro only.
- ❌ Batch / sequential (`sequential_image_generation`) — **not supported, errors**
- ❌ Streaming (`stream`) — **not supported, errors**
- ❌ `guidance_scale` — **not supported, errors**
- Single image output only — **except** `layer_decomposition`, which returns one image per layer.

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
| `layer_decomposition` | boolean | — | `false` | Split the input `image` into layers. Needs `image`; prompt must name each layer with a `<bbox>` (see below) |
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

### `layer_decomposition` rules (Pro)
- Requires an input `image` — the layers are cut out of it, so it is a strictly image-to-image mode.
- The **prompt** carries the layer plan: state how many layers, then name each one with its
  bounding box as `<bbox>left top right bottom</bbox>`, coordinates on a **0–1000 scale**
  relative to the input image.
- The response returns **n + 1** entries: a flattened **base image** at `z_index: 0` plus one
  entry per layer at `z_index: 1..n`. **Layers are not returned in `z_index` order** — sort
  before compositing.
- **Layers are always PNG with an alpha channel, regardless of `output_format`.** Only the
  base image honours `output_format`. A request with `"output_format": "jpeg"` still returns
  RGBA PNG layers; verified live.
- ⚠️ **Intermittent.** The same request sometimes returns a single flattened image with
  `generated_images: 1` and no layer fields — decomposition silently not applied, HTTP 200,
  no error. Observed 2 failures then 1 success on byte-identical payloads (2026-08-05).
  **Check for `z_index` in the response rather than assuming layers came back**, and retry.

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

### 11. Layer decomposition (seven layers out of one image)
```bash
curl -sS -X POST "$ARK" -H "Authorization: Bearer $ARK_API_KEY" -H "Content-Type: application/json" -d '{
  "model": "dola-seedream-5-0-pro-260628",
  "prompt": "Split the content in the image into seven layers, including six text groups: <bbox>179 58 809 197</bbox>, <bbox>65 216 319 280</bbox>, <bbox>754 210 942 285</bbox>, <bbox>172 712 832 811</bbox>, <bbox>337 824 663 929</bbox>, and <bbox>812 812 953 897</bbox>; and one parrot: <bbox>330 274 641 991</bbox>",
  "image": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream_50_pro_layer_input.png",
  "size": "2K",
  "output_format": "jpeg",
  "layer_decomposition": true,
  "watermark": true
}'
```
Response (verified live 2026-08-05, abridged — 8 entries for 7 requested layers):

```jsonc
{
  "model": "dola-seedream-5-0-pro-260628",
  "created": 1785957397,
  "data": [
    { "url": "https://...base.jpeg", "size": "2048x2048",
      "output_format": "jpeg", "z_index": 0 },              // flattened composite
    { "url": "https://...layer_4.png", "size": "2454x319",
      "output_format": "png", "z_index": 1,
      "name": "WILD BEAUTY title text",
      "description": "Extract the yellow large serif WILD BEAUTY title text, exclude other elements",
      "bounding_box": {
        "absolute":   [363, 1481, 1686, 1653],   // pixels in the source image
        "normalized": [177,  723,  823,  807]    // 0–1000 scale
      } },
    // ... z_index 2..7, returned OUT of order
    { "url": "https://...layer_7.png", "size": "850x2064",
      "output_format": "png", "z_index": 7, "name": "Scarlet macaw parrot", "...": "..." }
  ],
  "usage": { "input_images": 1, "generated_images": 8,
             "output_tokens": 129578, "total_tokens": 129578 }
}
```

Note `generated_images: 8` — the base image is billed alongside the 7 layers, and
`output_tokens` was ~8× a single 2K generation.

### 12. Full-options T2I
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

### Verified live 2026-08-05 — `layer_decomposition`
| Check | Result |
|---|---|
| 7-layer decomposition of the doc sample image | ✅ 8 entries (base + 7 layers), each with `z_index`, `name`, `description`, `bounding_box` |
| Layer transparency | ✅ RGBA PNG (colour-type 6) **even with `output_format: "jpeg"`** |
| Layer ordering in `data` | ⚠️ not in `z_index` order — sort before compositing |
| Repeatability | ⚠️ **intermittent** — 2 of 3 identical requests returned a single flattened image, HTTP 200, no error, no `z_index` |
| Unknown parameters | silently dropped (a made-up key returns 200), while recognised-but-unsupported ones 400 — so a 200 does **not** confirm the flag took effect |

---

## Using Pro from this repo

Pro is registered in the SDK as `dola-seedream-5-0-pro-260628`, alias `5.0-pro`. The client
enforces the Pro constraints above locally (no `4K`, no sequential, no `guidance_scale`,
≤ 10 references) so you get a named error instead of an API `InvalidParameter`.

```python
from seedream import SeedreamClient

layers = SeedreamClient().generate(
    "Split the content in the image into two layers, including one text group: "
    "<bbox>179 58 809 197</bbox>; and one parrot: <bbox>330 274 641 991</bbox>",
    model="5.0-pro",
    size="2K",
    image_urls=["https://.../seedream_50_pro_layer_input.png"],
    output_format="png",
    layer_decomposition=True,
)

if not layers.layers:
    ...   # decomposition silently did not apply — retry (see the caveat above)

print(layers.base_image.url)              # flattened composite (z_index 0)
for layer in layers.layers:               # sorted bottom-to-top by z_index
    print(layer.z_index, layer.name, layer.bounding_box["normalized"], layer.url)
```

`generate_and_download` names the files by z_index — `seedream-base.jpg`,
`seedream-layer1.png`, … — so the stack reassembles in filename order.

```bash
seedream generate -m 5.0-pro --layer-decomposition --output-format png \
  -r https://.../layer_input.png -o layers/ \
  -p 'Split the content in the image into two layers, including one text group:
      <bbox>179 58 809 197</bbox>; and one parrot: <bbox>330 274 641 991</bbox>'
```

MCP: `seedream_generate(..., model="5.0-pro", layer_decomposition=true)`.
