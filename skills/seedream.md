---
name: seedream
description: Generate images with BytePlus Seedream 4.5 and 5.0 Lite — text-to-image, image editing, reference-based generation, multi-image composition, and consistent multi-panel sets, backed by the seedream MCP server.
version: 1.0.0
---

# Seedream Image Generation

Use this skill to generate AI images with **BytePlus Seedream 4.5** and **Seedream 5.0 Lite**
directly from Claude Code, backed by the `seedream` MCP server.

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
> Mode:  text-to-image | edit/reference | sequential-set
> Model: seedream-4-5-251128 (4.5) | seedream-5-0-260128 (5.0 Lite)
> Size:  2K            (4.5 has NO 1K — use 2K/4K)
> Refs:  [image1]=<role/url> · [image2]=… (all local files uploaded to TOS)
> Set:   n images (only if sequential; refs + n ≤ 15)
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

You may pass the aliases `4.5` or `5.0-lite` as `model`. Default to **4.5** unless the
user asks for 5.0 Lite, cheaper cost, adaptive sizing, or complex layout/reference work
(where 5.0 Lite is stronger).

## Conditional MUST-READ table

Resolve top-to-bottom for every request; read what matches **before** drafting the prompt.

| If the request involves… | MUST read first |
|---|---|
| any submission (always) | [prompt-guidance](references/prompt-guidance.md) |
| editing an existing image | [editing-and-references](references/editing-and-references.md) |
| combining/blending multiple input images | [editing-and-references](references/editing-and-references.md) |
| a consistent multi-panel set / storyboard | [sequential-sets](references/sequential-sets.md) |
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
| `seedream_generate` | **Start here.** Text-to-image, editing, reference, and sequential sets — synchronous, returns image URL(s). |
| `seedream_upload_image_to_tos` | Upload a **local** image, get a public URL for `image_urls`. |
| `seedream_list_tos_buckets` | List TOS buckets so you can ask which to use. |
| `seedream_list_models` | List models, sizes, and features. |
| `seedream_ping` | Verify credentials and connectivity. |

## `seedream_generate` parameters

| Param | Meaning |
|---|---|
| `prompt` | Description / edit instruction. Quote literal text-in-image. |
| `model` | `4.5` (default) or `5.0-lite`, or a full model ID. |
| `size` | `1K`\*/`2K`/`4K`/`adaptive`\* or `WxH`. (\*5.0 Lite only.) |
| `image_urls` | Reference image URLs (public HTTPS). |
| `seed` | Reproducibility. |
| `guidance_scale` | Prompt adherence 1.0–20.0 (higher = stricter, may reduce quality). |
| `sequential` + `num_images` | Consistent multi-panel set (refs + outputs ≤ 15). |
| `optimize_prompt` | Ask the API to expand the prompt (use sparingly). |
| `watermark` | Add a watermark. |
| `response_format` | `url` (default) or `b64_json`. |

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
```

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
seedream models
seedream ping
```
