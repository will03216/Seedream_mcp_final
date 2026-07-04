# Models & Sizes

## Models

| Model | ID | Alias | Sizes | When to pick |
|---|---|---|---|---|
| **Seedream 4.5** | `seedream-4-5-251128` | `4.5` | 2K, 4K | Default. Strong general text-to-image and single-reference editing. **No 1K.** |
| **Seedream 5.0 Lite** | `seedream-5-0-260128` | `5.0-lite` | 1K, 2K, 4K, adaptive | Newer and cheaper. Stronger reference consistency, layout/structure reasoning, and complex design intent. Supports 1K and adaptive sizing. |

> Model IDs can change as BytePlus ships new versions. If a call fails with an unknown-model
> error, re-check the [ModelArk Seedream docs](https://docs.byteplus.com/en/docs/ModelArk/1824121)
> and update `packages/seedream-sdk/seedream/config.py`.

### Choosing

- **Default to 4.5** for straightforward text-to-image and simple edits.
- **Choose 5.0 Lite** when the user asks for it, wants lower cost, needs `1K`/`adaptive`,
  or the task is layout-heavy / multi-reference / preservation-critical.

## Sizes

| Size | Meaning |
|---|---|
| `1K` | ~1024px class. **5.0 Lite only** — 4.5 rejects it. |
| `2K` | ~2048px class. Default; good quality/latency balance. |
| `4K` | ~4096px class. Highest detail; slower and more expensive. |
| `adaptive` | Model picks dimensions from the prompt/reference. **5.0 Lite only.** |
| `WxH` | Explicit pixels, e.g. `2048x2048`. Accepted for either model. |

Rules of thumb:

- Posters / hero art / print → `4K`.
- Web / social / iteration → `2K`.
- Fast drafts on 5.0 Lite → `1K`.
- Non-standard aspect ratios → an explicit `WxH`, or `adaptive` on 5.0 Lite.

The SDK validates size against the chosen model and rejects `1K`/`adaptive` on 4.5 with a
clear error.
