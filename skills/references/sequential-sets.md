# Sequential Image Sets

Sequential generation produces a **consistent multi-image series** — comic panels,
storyboards, step-by-step guides, character turnarounds, product angle sets — where
subject identity and style hold across every image.

## How to invoke

```
seedream_generate(
  prompt="A 4-panel comic of a cat's morning: waking, stretching, eating, napping.
          Flat pastel style, consistent character design across all panels.",
  sequential=true,
  num_images=4,
)
```

- `sequential=true` enables set generation.
- `num_images=N` requests N images in the set.
- The result's `images` array is ordered — panel 1 first.

## The ≤ 15 rule

Input reference images **+** generated images must total **≤ 15**. So:

- Pure text-to-set: up to 15 generated images.
- With `k` reference images: up to `15 − k` generated images.

`seedream_generate` validates this and errors early if you exceed it.

## Writing a good set prompt

- Describe the **through-line** that must stay constant: character design, palette, style,
  camera treatment.
- Then describe **what changes** per image, in order ("Panel 1 … Panel 2 …" or "Angle 1 …").
- Keep the shared style description identical wording across the prompt so it doesn't drift.

## Reference-anchored sets

Pass one or more `image_urls` to anchor the set to an existing character or product, then
describe the variations. Seedream 5.0 Lite holds reference consistency best across a set.

## When NOT to use it

For a single image, leave `sequential` off — a plain text-to-image or single edit is
cheaper and simpler.
