# Prompt Guidance — Seedream 4.5 / 5.0 Lite

The Seedream prompt guides recommend **coherent natural language** with a clear scene
description. Clarity beats length. AI-inflated prompts are **not** automatically better
than a concise prompt written by a human.

## The scaffold

Turn any brief into a concise, concrete prompt by filling — in this order — only the
pieces that are missing:

1. **Output type** — poster, logo, infographic, UI mockup, product render, storyboard,
   editorial photo, icon set. State it when it matters; it strongly steers layout.
2. **Subject** — who/what, with the concrete attributes that matter.
3. **Action / pose** — what the subject is doing.
4. **Setting / environment** — where, time of day, season.
5. **Composition** — framing, angle, focal length feel, rule-of-thirds, negative space.
6. **Lighting** — name it (soft window light, hard noon sun, studio softbox, golden hour).
7. **Style** — precise descriptors (crisp commercial photography, flat vector, watercolor,
   3D render). Avoid vague adjectives like "beautiful", "amazing".

Stop once the prompt is concrete enough to control the result. Do not pad with decorative
adjectives unless the user explicitly wants maximal style steering.

## Text inside the image

Wrap the **exact** words that must appear in the image in double quotes:

> Design a minimalist café poster. Bold headline `"Summer Cold Brew"`, subtitle
> `"Now $4"`, centered, clean sans-serif.

Keep in-image text short and specify placement. Long paragraphs render poorly.

## Enhancement policy

- Treat "enhancement" as **clarification**, not inflation.
- Enhance most when the brief is underspecified, ambiguous, or missing output-type /
  preservation constraints.
- Do **not** enhance an already-good, specific prompt unless the user asks.
- Prefer doing the rewrite yourself in-conversation. The API `optimize_prompt` flag is a
  fallback — use it sparingly and note that it may drift from the user's intent.

## guidance_scale

Controls how strictly the image follows the prompt:

- **1–5** — more creative freedom, softer adherence.
- **~7 (default)** — balanced.
- **10–20** — strict adherence; can introduce artifacts or reduce visual quality.

Only set it when the user wants tighter control or is troubleshooting drift.

## Worked example

- Raw brief: `summer coffee poster`
- Better prompt: *"Design a premium but approachable summer coffee poster for a café.
  Show a clear plastic cup of iced cold brew with visible condensation on a sunlit outdoor
  table, warm late-afternoon light, crisp commercial photography, clean layout, and the
  headline `\"Summer Cold Brew\"`."*
