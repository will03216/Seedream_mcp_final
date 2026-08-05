# Seedream

Generate AI images with **BytePlus Seedream 4.5**, **Seedream 5.0 Lite** and **Seedream 5.0
Pro** — from your terminal, your AI client, or Claude Code.

---

## Choose your path

| I want to… | Use |
|---|---|
| Talk to Claude in natural language (Claude Desktop, Cursor, Windsurf) | [MCP Server](#-mcp-server) |
| Generate images from the terminal | [CLI](#-cli) |
| Use slash commands inside Claude Code | [Claude Code Skill](#-claude-code-skill) |

All three share the same credentials and the same underlying pipeline. The Seedream image
API is **synchronous** — a single call returns the finished image URL(s). There is no task
to poll.

---

## Models

| Model | ID | Sizes | Notes |
|---|---|---|---|
| **Seedream 4.5** | `seedream-4-5-251128` | 2K, 4K | Default. **No 1K.** |
| **Seedream 5.0 Lite** | `seedream-5-0-260128` | 2K, 3K, 4K | Newer, cheaper, stronger reference consistency & layout reasoning. **No 1K; no guidance_scale.** |
| **Seedream 5.0 Pro** | `dola-seedream-5-0-pro-260628` | 1K, 1.5K, 2K | Highest fidelity. Adds **layer decomposition**. Max 10 refs; **no 3K/4K, no sequential sets, no guidance_scale**. |

Aliases `4.5`, `5.0-lite` and `5.0-pro` are accepted anywhere a model is specified.

### Layer decomposition (5.0 Pro)

Split one image into its component layers — text groups, subject, background — each as a
transparent PNG cutout. Set `layer_decomposition`, pass the source image, and name each layer
in the prompt with a `<bbox>left top right bottom</bbox>` on a 0–1000 scale:

```
seedream_generate(
  prompt='Split the content in the image into two layers, including one text group:
          <bbox>179 58 809 197</bbox>; and one parrot: <bbox>330 274 641 991</bbox>',
  model="5.0-pro", size="2K", image_urls=["https://example.com/poster.png"],
  layer_decomposition=true
)
→ { count: 3, images: [
      { url: "…base.jpeg", z_index: 0 },                       # flattened composite
      { url: "…layer_1.png", z_index: 1, name: "Seedream title text",
        bounding_box: { absolute: […], normalized: […] } },
      { url: "…layer_2.png", z_index: 2, name: "Scarlet macaw parrot", … } ] }
```

You get **n + 1** images: the flattened base at `z_index: 0` plus one per layer. Layers are
always RGBA PNGs regardless of `output_format`, and are **not** returned in `z_index` order —
sort before compositing (the SDK's `result.layers` does).

⚠️ The decomposition is **intermittent**: the same request sometimes returns a single flat
image with no `z_index`, HTTP 200 and no error. Check for `z_index` before treating it as
done, and retry.

---

## Prerequisites

**Python 3.10+**, a local clone of this repo, and keys from the [BytePlus console](https://console.byteplus.com):

| Key | Where | Used for |
|---|---|---|
| `ARK_API_KEY` | ModelArk → API Keys | Image generation *(required)* |
| `ARK_AK` | IAM → Access Keys | TOS upload of **local** reference images *(optional)* |
| `ARK_SK` | IAM → Access Keys | TOS upload of local reference images *(optional)* |
| `SEEDREAM_TOS_BUCKET` | TOS console → Buckets | Default bucket for uploads *(optional)* |
| `SEEDREAM_TOS_REGION` | — | TOS region, default `ap-southeast-1` *(optional)* |

Plain text-to-image (and references you pass as public URLs) need only `ARK_API_KEY`.

---

## 🖥 MCP Server

Lets Claude Desktop, Cursor, and Windsurf generate images from natural language.

### Setup

```bash
git clone https://github.com/mittulmadaan/byteplus-seedream-mcp
cd byteplus-seedream-mcp
pip install packages/seedream-sdk packages/seedream-mcp -e packages/seedream-cli
seedream auth login        # stores credentials in ~/.seedream/credentials
seedream skill install     # patches Claude Desktop + Claude Code configs automatically
# Restart your AI client
```

Then just ask Claude: *"Generate a 4K poster of iced cold brew on a sunlit table with the
headline Summer Cold Brew"*

### Manual config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or the
equivalent on your OS:

```json
{
  "mcpServers": {
    "seedream": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "seedream_mcp"]
    }
  }
}
```

Set credentials via environment variables before launching your client.

### Hosted / Docker

```bash
docker build -f packages/seedream-mcp/docker/Dockerfile -t seedream-mcp .

docker run -p 8000:8000 \
  -e MCP_TRANSPORT=sse \
  -e ARK_API_KEY=<key> \
  -e ARK_AK=<ak> \
  -e ARK_SK=<sk> \
  -e MCP_AUTH_TOKEN=<strong-random-token> \
  seedream-mcp
```

Your BytePlus credentials stay server-side. Clients connect using `MCP_AUTH_TOKEN` only.
Point your MCP client at `http://your-host:8000/mcp` (streamable HTTP transport).

### How to use

Use `seedream_generate` for everything — it returns image URLs directly:

```
# Text-to-image
seedream_generate(prompt="A silver espresso machine, morning light, steam rising", size="2K")
→ { model: "seedream-4-5-251128", count: 1, images: [{ url: "https://..." }] }

# Seedream 5.0 Lite, 4K
seedream_generate(prompt="Editorial close-up portrait, sculptural hat, studio lighting",
                  model="5.0-lite", size="4K")

# Editing / reference — say what to change and what to keep
seedream_generate(
  prompt="Use Image 1. Replace the background with a snowy forest at dusk. Keep the
          subject's pose, outfit, and the product label unchanged.",
  image_urls=["https://example.com/photo.png"]
)

# Consistent multi-panel set
seedream_generate(prompt="A 4-panel comic of a cat's morning, flat pastel style",
                  sequential=true, num_images=4)
```

For a **local** reference image, upload it first:

```
seedream_list_tos_buckets()                                  # ask which bucket
seedream_upload_image_to_tos(file_path="/path/ref.png", bucket="<name>")
→ { url: "https://<bucket>.tos-....bytepluses.com/ref.png" }
# then pass that url in image_urls
```

### Available tools

| Tool | Description |
|---|---|
| `seedream_generate` | **Start here.** Text-to-image, editing, reference, sequential sets, layer decomposition. Returns URL(s). |
| `seedream_upload_image_to_tos` | Upload a **local** image; returns a public URL. |
| `seedream_list_tos_buckets` | List TOS buckets so Claude can ask which to use. |
| `seedream_list_models` | List models, sizes, and features. |
| `seedream_ping` | Verify credentials and connectivity. |

---

## 💻 CLI

Full-featured terminal interface.

### Setup

```bash
git clone https://github.com/mittulmadaan/byteplus-seedream-mcp
cd byteplus-seedream-mcp
pip install packages/seedream-sdk packages/seedream-mcp -e packages/seedream-cli
seedream auth login
```

### Generate an image

```bash
# Text-to-image
seedream generate -p "A serene mountain landscape at sunset with golden clouds" \
  --size 2K --output out/

# Seedream 5.0 Lite, 4K
seedream generate -p "Editorial portrait, dramatic studio lighting" \
  --model 5.0-lite --size 4K --output out/

# Editing / reference — local path auto-uploads to TOS
seedream generate -p "Replace the background with a snowy forest. Keep the pose." \
  --ref ./photo.png --bucket my-bucket --output out/

# Consistent multi-panel set
seedream generate -p "A 4-panel comic of a cat's morning, flat pastel style" \
  --sequential -n 4 --output out/

# Layer decomposition — one file per layer (Seedream 5.0 Pro)
seedream generate -m 5.0-pro --layer-decomposition --output-format png \
  -r ./poster.png --bucket my-bucket --output layers/ \
  -p 'Split the content in the image into two layers, including one text group:
      <bbox>179 58 809 197</bbox>; and one parrot: <bbox>330 274 641 991</bbox>'
```

### All flags

```bash
seedream generate \
  --prompt        "..."       # description / edit instruction (required)
  --model         5.0-lite    # 4.5 (default) | 5.0-lite | 5.0-pro | full model ID
  --size          2K          # 2K everywhere | 1K/1.5K Pro only | 3K/4K not on Pro | WxH
  --ref           <url|path>  # reference image; repeatable; local paths auto-upload
  --bucket        <name>      # TOS bucket for local --ref uploads
  --seed          42          # reproducible results
  --guidance-scale 7.5        # prompt adherence 1.0–10.0 (Seedream 4.5 only)
  --sequential                # generate a consistent multi-panel set
  --num-images    4           # images in a sequential set (refs + n ≤ 15)
  --optimize-prompt           # let the API optimize the prompt
  --optimize-prompt-mode standard  # standard | fast   (fast is 5.0 Pro only)
  --watermark                 # add a watermark
  --output-format png         # png | jpeg (5.0 Pro / 5.0 Lite only)
  --layer-decomposition       # split the --ref image into layers (5.0 Pro only)
  --output        out/        # download the image(s) into this directory
```

### Other commands

```bash
# Auth
seedream auth login           # store credentials interactively
seedream auth check           # verify keys are configured
seedream auth logout

# TOS object storage — upload a LOCAL file, get a public URL
seedream tos buckets                             # list buckets
seedream tos upload ./photo.png --bucket <name>  # upload, prints public URL

# Info
seedream models               # list models, sizes, features
seedream ping                 # verify credentials and connectivity

# Skill management
seedream skill install        # install into Claude Desktop + Claude Code
seedream skill check          # show install status
seedream skill uninstall
```

---

## 🧠 Claude Code Skill

Slash commands inside Claude Code, backed by the MCP server.

### Setup

```bash
git clone https://github.com/mittulmadaan/byteplus-seedream-mcp
cd byteplus-seedream-mcp
pip install packages/seedream-sdk packages/seedream-mcp -e packages/seedream-cli
seedream auth login
seedream skill install        # copies skill file + patches Claude Code settings
# Restart Claude Code
```

The skill lives in [`skills/seedream.md`](skills/seedream.md) with detailed prompting,
editing, and model-selection guidance in [`skills/references/`](skills/references/).

---

## SDK

For building custom integrations:

```python
from seedream import SeedreamClient

client = SeedreamClient()  # reads from env vars or ~/.seedream/credentials

# Text-to-image — synchronous, returns URLs directly
result = client.generate(
    prompt="A sunrise over mountains, warm light",
    model="4.5",
    size="2K",
)
print(result.urls)

# Editing with a reference image
result = client.generate(
    prompt="Replace the background with a beach. Keep the subject unchanged.",
    image_urls=["https://example.com/photo.png"],
    model="5.0-lite",
)

# Generate and download to a directory
result = client.generate_and_download(
    "A 4-panel comic of a cat's day", "out/",
    sequential=True, num_images=4,
)
for img in result.images:
    print(img.local_path)
```

Install: `pip install packages/seedream-sdk` (zero runtime dependencies — stdlib urllib only).

---

## Repo Structure

```
packages/
  seedream-sdk/          # core: HTTP client, TOS HMAC signing, config, types (zero deps)
  seedream-mcp/          # MCP server — thin wrappers over SDK
    docker/              # Dockerfile + docker-compose
  seedream-cli/          # CLI — typer + rich
    seedream_cli/commands/
      auth.py generate.py tos.py models.py skill.py

skills/
  seedream.md            # Claude Code skill definition
  references/            # prompting, editing, sequential sets, models, assets

.github/workflows/
  ci.yml                 # lint + test (Python 3.10 / 3.11 / 3.12)
  release-sdk.yml        # → PyPI on tag sdk/v*
  release-mcp.yml        # → PyPI + Docker Hub on tag mcp/v*
  release-cli.yml        # → PyPI on tag cli/v*
```

---

## Credentials

Resolution order (first non-empty value wins):

1. Constructor args: `SeedreamClient(api_key="...", ak="...", sk="...")`
2. Environment variables: `ARK_API_KEY` (or `BYTEPLUS_API_KEY`), `ARK_AK`, `ARK_SK`
3. `~/.seedream/credentials` — written by `seedream auth login`
4. `.env` file in CWD (requires `python-dotenv`)

> Never embed credentials in client config files or Docker images. Use `MCP_AUTH_TOKEN` to
> protect hosted SSE endpoints.

---

## Release

```bash
git tag sdk/v1.0.1 && git push --tags   # publishes seedream-sdk to PyPI
git tag mcp/v1.0.1 && git push --tags   # publishes seedream-mcp to PyPI + Docker Hub
git tag cli/v1.0.1 && git push --tags   # publishes seedream-cli to PyPI
```

---

## Support

- [BytePlus ModelArk — Seedream 4.0–5.0 tutorial](https://docs.byteplus.com/en/docs/ModelArk/1824121)
- [Image generation API](https://docs.byteplus.com/en/docs/ModelArk/1541523)
- [API key management](https://docs.byteplus.com/en/docs/ModelArk/1361424)

> **Note:** Seedream model IDs may change as BytePlus ships new versions. If a call returns
> an unknown-model error, re-check the docs above and update
> `packages/seedream-sdk/seedream/config.py`.
