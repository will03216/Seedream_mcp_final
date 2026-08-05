---
name: seedream
description: Generate images with BytePlus Seedream 4.5, 5.0 Lite and 5.0 Pro — text-to-image, image editing, reference-based generation, multi-image composition, consistent multi-panel sets, and splitting an image into layers, backed by the seedream MCP server.
version: 1.1.0
---

# Seedream Image Generation

Use this skill to generate AI images with **BytePlus Seedream 4.5**, **Seedream 5.0 Lite**
and **Seedream 5.0 Pro** directly from Claude Code, backed by the `seedream` MCP server.

The Seedream image API is **synchronous** — `seedream_generate` returns the finished
image URL(s) in a single call. There is no task to poll (unlike Seedance video).

> **🚨 MANDATORY PRE-FLIGHT RULE #1 — Prompt clarification, not inflation**
>
> Before calling `seedream_generate`, turn the user's brief into a concise, concrete
> prompt using the framework in [`references/prompt-guidance.md`](references/prompt-guidance.md):
>
> **subject + action + setting + composition + lighting + style + output-type**,
> plus **preservation constraints** for edits.
>
> Seedream rewards *clarity*, not adjective piles. Do **not** "enhance" an already-good
> prompt. Add missing pieces only when the brief is underspecified. Show the user the
> final prompt before submission so they can confirm or tweak it.
>
> - **Text that must appear in the image** → wrap the exact words in double quotes:
>   `the headline "Summer Cold Brew"`.
> - **Editing** → give a direct instruction *and* state what must stay fixed (pose,
>   composition, product material, camera angle, branding).
> - **Multi-image** → name each image's role: "Use Image 1 as the background, replace
>   the subject with the character from Image 2."

> **🚨 MANDATORY PRE-FLIGHT RULE #2 — Local files must be uploaded first**
>
> Generation needs **public URLs**, not local paths. When the user supplies a local
> reference image:
>
> 1. Call `seedream_upload_image_to_tos(file_path=..., bucket=...)` to get a public URL.
> 2. If the user hasn't said which bucket, call `seedream_list_tos_buckets` first and
>    **ask** which bucket to use (accounts can have several).
> 3. Pass the returned URL in `image_urls`.
>
> TOS upload needs `ARK_AK` / `ARK_SK`. Plain text-to-image needs only `ARK_API_KEY`.

> **🚨 MANDATORY PRE-FLIGHT RULE #3 — The Image Card**
>
> Before every `seedream_generate` call, print an **Image Card** and get confirmation:
>
> ```text
> 🖼  Seedream Image Card
> Mode:  text-to-image | edit/reference | sequential-set | layer-decomposition
> Model: seedream-4-5-251128 (4.5) | seedream-5-0-260128 (5.0 Lite)
>        | dola-seedream-5-0-pro-260628 (5.0 Pro)
> Size:  2K            (4.5 has NO 1K; 5.0 Pro has NO 4K/adaptive)
> Refs:  [image1]=<role/url> · [image2]=… (all local files uploaded to TOS)
> Set:   n images (only if sequential; refs + n ≤ 15)
> Layers: n layers, each with its <bbox> (only if layer_decomposition)
> Prompt: """
>   <the exact prompt that will be submitted>
>   """
> Checklist: output-type named ✓ text-in-quotes ✓ preservation stated (edits) ✓ size valid for model ✓
> ```

## Model selection

| Model | ID | Sizes | Notes |
|---|---|---|---|
| **Seedream 4.5** | `seedream-4-5-251128` | 2K, 4K | Default. **No 1K.** |
| **Seedream 5.0 Lite** | `seedream-5-0-260128` | 1K, 2K, 4K, adaptive | Newer, cheaper, stronger reference consistency & layout reasoning. |
| **Seedream 5.0 Pro** | `dola-seedream-5-0-pro-260628` | 1K, 2K | Highest fidelity, and the only model that can split an image into layers. Max 10 refs; no sequential sets, no `guidance_scale`. |

You may pass the aliases `4.5`, `5.0-lite` or `5.0-pro` as `model`. Default to **4.5** unless
the user asks for 5.0 Lite, cheaper cost, adaptive sizing, or complex layout/reference work
(where 5.0 Lite is stronger). Use **5.0 Pro** when the user asks for it, wants top fidelity,
or wants an image **decomposed into layers** — that mode exists on Pro only.

## Conditional MUST-READ table

Resolve top-to-bottom for every request; read what matches **before** drafting the prompt.

| If the request involves… | MUST read first |
|---|---|
| any submission (always) | [prompt-guidance](references/prompt-guidance.md) |
| editing an existing image | [editing-and-references](references/editing-and-references.md) |
| combining/blending multiple input images | [editing-and-references](references/editing-and-references.md) |
| a consistent multi-panel set / storyboard | [sequential-sets](references/sequential-sets.md) |
| splitting an image into layers (text / subject / background) | [models-and-sizes](references/models-and-sizes.md) (layer decomposition section) |
| text rendered inside the image (posters, logos, UI) | [prompt-guidance](references/prompt-guidance.md) (text-in-image section) |
| choosing size / model / cost trade-offs | [models-and-sizes](references/models-and-sizes.md) |
| a local reference image | [assets](references/assets.md) |

## Prerequisites

Install and configure before first use (run from the repo root):

```bash
git clone https://github.com/byteplus/byteplus-seedream-mcp
cd byteplus-seedream-mcp
pip install packages/seedream-sdk packages/seedream-mcp -e packages/seedream-cli
seedream auth login        # stores credentials in ~/.seedream/credentials
seedream skill install     # wires the MCP server into Claude Code & Claude Desktop
# Restart your AI client
```

Only `ARK_API_KEY` is required. `ARK_AK` / `ARK_SK` are needed only for uploading local
reference images to TOS.

## Available MCP tools

| Tool | Description |
|---|---|
| `seedream_generate` | **Start here.** Text-to-image, editing, reference, sequential sets, and layer decomposition — synchronous, returns image URL(s). |
| `seedream_upload_image_to_tos` | Upload a **local** image, get a public URL for `image_urls`. |
| `seedream_list_tos_buckets` | List TOS buckets so you can ask which to use. |
| `seedream_list_models` | List models, sizes, and features. |
| `seedream_ping` | Verify credentials and connectivity. |

## `seedream_generate` parameters

| Param | Meaning |
|---|---|
| `prompt` | Description / edit instruction. Quote literal text-in-image. |
| `model` | `4.5` (default), `5.0-lite` or `5.0-pro`, or a full model ID. |
| `size` | `1K`\*/`2K`/`4K`†/`adaptive`\* or `WxH`. (\*not on 4.5, †not on 5.0 Pro.) |
| `image_urls` | Reference image URLs (public HTTPS). |
| `seed` | Reproducibility. |
| `guidance_scale` | Prompt adherence 1.0–20.0 (higher = stricter, may reduce quality). |
| `sequential` + `num_images` | Consistent multi-panel set (refs + outputs ≤ 15). |
| `optimize_prompt` | Ask the API to expand the prompt (use sparingly). |
| `watermark` | Add a watermark. |
| `response_format` | `url` (default) or `b64_json`. |
| `output_format` | `png` or `jpeg`. **5.0 Pro / 5.0 Lite only** (API default `jpeg`). |
| `layer_decomposition` | Split the image in `image_urls` into layers, one output image per layer. **5.0 Pro only**, and needs `image_urls`. |

## Quick examples

```
# Text-to-image (Seedream 4.5, 2K)
seedream_generate(prompt='A premium summer coffee poster: iced cold brew in a clear cup
  with condensation on a sunlit table, warm late-afternoon light, clean layout, the
  headline "Summer Cold Brew".', size="2K")

# Seedream 5.0 Lite, 4K
seedream_generate(prompt="Vibrant editorial close-up portrait, sculptural hat, dramatic
  studio lighting.", model="5.0-lite", size="4K")

# Editing / reference — state what to change and what to keep
seedream_generate(prompt="Use Image 1. Change the background to a snowy forest at dusk.
  Keep the subject's pose, outfit, and the product label unchanged.",
  image_urls=["https://.../photo.png"])

# Consistent 4-panel set
seedream_generate(prompt="A 4-panel comic: a cat's morning routine, flat pastel style,
  consistent character design.", sequential=true, num_images=4)

# Layer decomposition — one output image per layer (Seedream 5.0 Pro only)
seedream_generate(prompt='Split the content in the image into three layers, including two
  text groups: <bbox>179 58 809 197</bbox>, <bbox>65 216 319 280</bbox>; and one parrot:
  <bbox>330 274 641 991</bbox>',
  model="5.0-pro", size="2K", image_urls=["https://.../poster.png"],
  output_format="png", layer_decomposition=true)
```

For layer decomposition, the prompt **is** the layer plan: state how many layers, then give
each layer a `<bbox>left top right bottom</bbox>` with coordinates on a **0–1000 scale**
relative to the input image. You get back a flattened base image at `z_index: 0` plus one
transparent PNG per layer at `z_index: 1..n`, each with a `name` and `bounding_box`.

⚠️ The decomposition is **intermittent** — the same request sometimes returns a single flat
image with no `z_index` and no error. Check for `z_index` before telling the user it worked,
and retry once if it's missing.

For a local reference image, first:
```
seedream_list_tos_buckets()                          # ask user which bucket
seedream_upload_image_to_tos(file_path="/path/to/ref.png", bucket="<name>")
# → pass the returned url in image_urls
```

## CLI equivalents

```bash
seedream generate -p "A serene mountain at sunset" --size 2K --output out/
seedream generate -p "edit: snowy background, keep pose" --ref ./photo.png --output out/
seedream generate -p "comic strip, 4 panels" --sequential -n 4 --model 5.0-lite
seedream generate -m 5.0-pro --layer-decomposition --output-format png \
  -r ./poster.png -o layers/ -p 'Split the content in the image into two layers, ...'
seedream models
seedream ping
```
