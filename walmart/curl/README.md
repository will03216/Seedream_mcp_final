# Walmart prompts → Seedream 5.0 Pro curl requests

Analysis of [`../prompts.json`](../prompts.json) and ready-to-run curl requests.

**Model:** `dola-seedream-5-0-pro-260628` · **Endpoint:** `POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`
**Auth:** `Authorization: Bearer $ARK_API_KEY` · **Sync** (one call returns the image) · **size** `2K`, watermark off.

All five scenarios are **image-to-image (edit)** — every one supplies reference images. The Walmart product/scene photos are **local files**, and the API takes references only as public URLs or `data:image/...;base64,...` data-URIs, so each request body embeds the images as base64. That makes the bodies large (multi-MB), so they live in `payloads/*.json` and are sent with `curl --data-binary @payloads/<id>.json` rather than inline.

## Scenario analysis

| # | scenario_id | refs | task type | notes |
|---|---|---|---|---|
| 1 | `studio_many_items_layout_001` | **11** | multi-ref compositing (Thanksgiving table) | ⚠️ **Exceeds Pro's 10-image limit** — this request returns `InvalidParameter` on Pro. Drop 1 ref, or run on 5.0 Lite/4.5/4.0 (allow up to 14). |
| 2 | `rug_under_table_9x15_001` | 2 | spatial placement w/ real-world scale | rug (img2) under coffee table (img1); prompt encodes 9×15 ft rug vs 3×5 ft table. |
| 3 | `edge_reflective_001` | 1 | scene placement + reflections | copper/silver kettle in modern kitchen; tests metallic reflection realism. |
| 4 | `inject_ozark_tumbler_in_camp_chair` | 2 | product injection / relighting | tumbler into chair cup-holder; long prompt fixes scene, DoF, brand fidelity. |
| 5 | `add_props_001_maskfree` | 1 | mask-free object replacement | swap decor on black side table for succulent + magazines. |

## Usage

```bash
# 1. Build request bodies (base64-embeds local refs) — regenerate if images change
./build_payloads.sh

# 2. Send one, or all. Saves image to ../output/<id>.jpeg
export ARK_API_KEY=<your-modelark-bearer-token>
./run.sh rug_under_table_9x15_001
./run.sh --all
```

Each `payloads/<id>.json` is a complete request body — you can also send it directly:

```bash
curl -sS -X POST "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations" \
  -H "Authorization: Bearer $ARK_API_KEY" -H "Content-Type: application/json" \
  --data-binary @payloads/rug_under_table_9x15_001.json | jq -r '.data[0].url'
```
