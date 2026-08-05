# Models & Sizes

## Models

| Model | ID | Alias | Sizes | When to pick |
|---|---|---|---|---|
| **Seedream 4.5** | `seedream-4-5-251128` | `4.5` | 2K, 4K | Default. Strong general text-to-image and single-reference editing. **No 1K.** |
| **Seedream 5.0 Lite** | `seedream-5-0-260128` | `5.0-lite` | 2K, 3K, 4K | Newer and cheaper. Stronger reference consistency, layout/structure reasoning, and complex design intent. **No 1K, no `adaptive`, no `guidance_scale`** — all verified live. |
| **Seedream 5.0 Pro** | `dola-seedream-5-0-pro-260628` | `5.0-pro` | 1K, 1.5K, 2K | Highest fidelity, and the only model that can **decompose an image into layers**. Max 10 reference images. **No 4K/adaptive, no sequential sets, no `guidance_scale`; `seed` is ignored.** |

> Model IDs can change as BytePlus ships new versions. If a call fails with an unknown-model
> error, re-check the [ModelArk Seedream docs](https://docs.byteplus.com/en/docs/ModelArk/1824121)
> and update `packages/seedream-sdk/seedream/config.py`.

### Choosing

- **Default to 4.5** for straightforward text-to-image and simple edits.
- **Choose 5.0 Lite** when the user asks for it, wants lower cost, needs `1K`/`adaptive`,
  or the task is layout-heavy / multi-reference / preservation-critical.
- **Choose 5.0 Pro** when the user asks for it, wants the highest fidelity, or wants an
  image **split into layers**. Pro is the only model with `layer_decomposition`.

## Sizes

| Size | Meaning |
|---|---|
| `1K` | ~1024px class. **Not on 4.5.** |
| `2K` | ~2048px class. Default; good quality/latency balance. |
| `4K` | ~4096px class. Highest detail; slower and more expensive. **Not on 5.0 Pro.** |
| `adaptive` | Model picks dimensions from the prompt/reference. **5.0 Lite only.** |
| `WxH` | Explicit pixels, e.g. `2048x2048`. Accepted for any model. |

Rules of thumb:

- Posters / hero art / print → `4K` (4.5 or 5.0 Lite; Pro tops out at `2K`).
- Web / social / iteration → `2K`.
- Fast drafts on 5.0 Lite → `1K`.
- Non-standard aspect ratios → an explicit `WxH`, or `adaptive` on 5.0 Lite.

The SDK validates size against the chosen model — it rejects `1K`/`adaptive` on 4.5 and
`4K`/`adaptive` on 5.0 Pro with a clear error.

## Layer decomposition (5.0 Pro only)

Splits one input image into its component layers. Returns **n + 1** images: a flattened base
image at `z_index: 0`, plus one per layer at `z_index: 1..n`, each with a `name`,
`description` and `bounding_box`.

```
seedream_generate(
  prompt='Split the content in the image into three layers, including two text groups:
          <bbox>179 58 809 197</bbox>, <bbox>65 216 319 280</bbox>; and one parrot:
          <bbox>330 274 641 991</bbox>',
  model="5.0-pro", size="2K", image_urls=["https://.../poster.png"],
  output_format="png", layer_decomposition=true
)
```

- Needs a source image in `image_urls` — it is an image-to-image mode, never text-to-image.
- The **prompt** is the layer plan: say how many layers, then give each one a
  `<bbox>left top right bottom</bbox>` with coordinates on a **0–1000 scale** relative to the
  input image.
- **Layers are always transparent PNGs**, whatever `output_format` says; only the base image
  honours it. You do not need `output_format="png"` to get transparency.
- **Layers are not returned in `z_index` order** — sort by `z_index` before compositing
  (1 = bottom). The SDK's `result.layers` does this for you.
- ⚠️ **The decomposition is intermittent.** The same request sometimes comes back as a single
  flattened image with no `z_index` — HTTP 200, no error. **Check whether any image has a
  `z_index` before reporting success**, and just retry if not; the payload is fine.

## Not implemented: `stream`

The API documents a `stream` boolean (5.0 Lite / 4.5 / 4.0 only; 5.0 Pro errors on it)
that returns each image as it finishes instead of all at once. This SDK does not expose it —
`generate()` is synchronous and returns the finished set. Batch generation works without it;
you just wait for the whole set. Everything else in the request schema is covered.

## Output format

`output_format` is `png` or `jpeg`, and is accepted only by **5.0 Pro and 5.0 Lite**. The API
default is `jpeg`. 4.5 rejects the parameter.
