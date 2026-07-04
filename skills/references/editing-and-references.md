# Editing & Reference-Based Generation

Seedream accepts one or more reference images in `image_urls`. Use them for editing an
existing image, borrowing a style, placing a product, or composing several inputs.

## Golden rule: say what changes AND what stays

Editing quality lives or dies on **preservation constraints**. Every edit prompt should
pair a direct instruction with an explicit list of what must remain fixed.

> **Change:** replace the background with a snowy forest at dusk.
> **Keep:** the subject's pose, facial identity, outfit, and the product label unchanged.

Common things to preserve: pose, composition, camera angle, facial identity, product
material/color, branding/logo text, lighting direction.

## Naming multiple images

When you pass several references, identify each one's role by number, in argument order:

> Use **Image 1** as the background. Take the character from **Image 2** and place them
> seated at the table in Image 1. Match Image 1's lighting. Keep the character's clothing
> from Image 2 unchanged.

Be explicit — Seedream binds roles from the prompt, not from guesswork.

## Typical patterns

- **Background swap** — "Replace the background with X. Keep the subject and its edges clean."
- **Style transfer** — "Render the subject of Image 1 in the painterly style of Image 2.
  Preserve the subject's shape and composition."
- **Product placement** — "Place the product from Image 1 onto the marble countertop in
  Image 2, matching perspective and reflections. Keep the product label sharp and unchanged."
- **Local edit** — "Change only the car's color to matte black. Leave everything else
  identical."

## Model choice for references

Seedream **5.0 Lite** has stronger reference consistency and layout reasoning — prefer it
for multi-image composition, precise preservation, and complex layout intent. 4.5 is fine
for single-reference edits and style borrowing.

## Local files

Reference images must be **public URLs**. Upload local files first with
`seedream_upload_image_to_tos` (see [assets.md](assets.md)), then pass the returned URL.

## Budget

Input reference images + generated images must total **≤ 15**. For a single edit that
means up to 14 references.
