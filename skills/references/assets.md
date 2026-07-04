# Assets — Using Local Reference Images

Seedream's generation API fetches reference images over HTTP. It cannot read a local file
path. To use a local image as a reference, upload it to TOS (object storage) first and pass
the returned **public URL** in `image_urls`.

## The flow

1. **Discover buckets** (if the user hasn't named one):
   ```
   seedream_list_tos_buckets()
   ```
   Show the list and ask which bucket to use — accounts often have several.

2. **Upload the local file**:
   ```
   seedream_upload_image_to_tos(file_path="/Users/you/ref.png", bucket="my-bucket")
   → { url: "https://my-bucket.tos-ap-southeast-1.bytepluses.com/ref.png", ... }
   ```
   The object is written with a public-read ACL so the URL is directly fetchable.

3. **Generate** with the returned URL:
   ```
   seedream_generate(prompt="...", image_urls=["https://my-bucket.../ref.png"])
   ```

The CLI does steps 1–3 in one go: `seedream generate --ref ./photo.png ...` auto-uploads
any local path passed to `--ref` (set `--bucket` or `SEEDREAM_TOS_BUCKET`).

## Credentials

TOS upload uses IAM access keys, **separate** from the generation API key:

| Credential | Used for |
|---|---|
| `ARK_API_KEY` | Image generation (always required) |
| `ARK_AK` / `ARK_SK` | TOS upload of local reference images (only for this) |

If a user only ever passes public image URLs, they never need `ARK_AK` / `ARK_SK`.

## Defaults

Set `SEEDREAM_TOS_BUCKET` (and optionally `SEEDREAM_TOS_REGION`, default
`ap-southeast-1`) to skip the bucket prompt on every upload.

## Tips

- Already-public URLs (e.g. a link the user pastes) need no upload — pass them straight
  through in `image_urls`.
- Uploaded URLs are durable public objects; treat the bucket as shared storage, not a
  scratch space, and don't upload anything sensitive without the user's okay.
