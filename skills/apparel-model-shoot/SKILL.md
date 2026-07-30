---
name: apparel-model-shoot
description: Turn flat-lay / mannequin / ghost-mannequin garment photos into a full on-model e-commerce shoot with BytePlus Seedream 5.0 Pro. Two steps — build one hero on-model image, then fan out a consistent PDP set (poses, angles, back view, fabric and print macros) from that hero. Use for apparel catalogue production, PDP image sets, model swaps, and lookbook expansion.
version: 1.0.0
---

# Apparel Model Shoot — mannequin ➜ hero ➜ fan-out set

Replaces a physical model shoot for graphic tees, knitwear, outerwear, denim and similar
soft goods. Input is whatever the brand already has (flat lay, mannequin, ghost mannequin,
detail macros). Output is a full PDP image set on a consistent model, in a consistent studio.

**Model:** `dola-seedream-5-0-pro-260628` · **Size:** 2K · synchronous, one call per image.

---

## The one rule that makes this work

> **Every image that shows a person is generated from the hero. Every image that shows only
> cloth is generated from the brand's product photography.**

The hero carries the model's face, hair, body, the styling, the backdrop and the lighting.
Once it exists, every on-model fan-out is a *pose/crop edit of a photo that already exists*,
which is a far easier ask than "invent a consistent person again". Fanning out from the
mannequin refs instead gives you eight different women in eight different studios.

The macros are the exception. They are flat-lay product shots — the garment alone, no person
in frame — so there is no identity to carry, and routing them through the hero means the
artwork is copied from a copy. Feed those the brand's originals directly
(`"use_hero": false`) and the print stays one generation from the source.

Because the model's default assumption is that a garment close-up has a body inside it, the
absence of a person is something you have to **state**, not omit.

```
step-0  brand's existing refs        step-1  hero            step-2  fan-outs
  front.png ┐                                                 ├ three-quarter
  back.png  ├─► [Seedream i2i] ─►  hero.png  ─► [Seedream i2i] ├ walking
  closeup   ┘   (2 refs)             ▲          (hero + 0-1    ├ hands in pockets
      │         × 3 variants         │           extra refs)   ├ low angle
      │         pick 1 ──────────────┘                         ├ waist-up crop
      │                                                        └ back view  (+ back.png)
      │
      └──────────────────────────────► [Seedream i2i] ─────────┬ fabric macro   no hero
                                       (product refs only)     └ print macro    no hero
```

---

## Pre-flight

1. **Sort the refs.** You need at minimum a straight-on front. Also useful: back, and a
   macro of neckline/fabric/print. Discard angled or lifestyle shots — they fight the
   hero's geometry.
2. **Read the garment out loud** before writing anything: colour, fit, neckline, sleeve,
   hem, and — word for word — every piece of text and artwork on it. That paragraph
   becomes the `MUST PRESERVE` block and gets pasted into every prompt.
3. **Pick the size once and keep it.** Portrait full-body → `1760x2352`. Square macro →
   `2048x2048`. Never mix aspect ratios inside one PDP set.
4. **Local files** go in as `data:image/<fmt>;base64,...` — no TOS upload needed for
   Seedream 5.0 Pro. Up to 10 reference images per call.

---

## Prompt structure

Every prompt in both steps is the same four blocks, in this order:

| Block | Purpose |
|---|---|
| **REFERENCE ROLES** | "Image 1 is X. Image 2 is Y." Name every input's job. |
| **CHANGE** | The one thing this image is for — the pose, the angle, the crop. |
| **KEEP** | Model identity, styling, set, lighting. Verbatim across the set. |
| **MUST PRESERVE** | The garment paragraph from pre-flight, plus "do not add any extra text, logo or graphic". |

Seedream 5.0 Pro rewards **concrete and physical** over adjectives. "Camera on the floor at
knee height tilted upward, verticals converging" works; "dynamic low angle" does not — see
Failure modes.

### Step 1 — hero template

```text
Image 1 is the front of a garment photographed flat on a headless mannequin.
Image 2 is a macro of the same garment's neckline, fabric and print.

Task: produce a studio e-commerce hero photograph of a real human model wearing this
exact garment. Remove the mannequin entirely.

MODEL:   <age, build, skin tone, hair, expression>. <Stance: upright, square-on to
         camera, arms relaxed at sides, weight even on both feet.>
STYLING: the garment worn <untucked> over <bottoms> and <shoes>. No jewellery, no bag,
         no other accessories.
SET:     seamless <colour> studio backdrop, soft even large-softbox frontal light,
         subtle contact shadow under the shoes, no harsh shadows on the backdrop.
CAMERA:  full-body head-to-toe framing, model centred, eye-level, 85mm lens look,
         small even margin above the head and below the shoes.

MUST PRESERVE EXACTLY from the references, unchanged: <colour>; <fit, seams, sleeves,
hem>; <neckline>; and <the artwork — shape, letterforms, exact quoted wording, colours,
position, print texture>. Do not redraw, restyle, recolour, resize or reposition the
print. Do not add any extra text, logo or graphic anywhere on the garment.

Photorealistic fashion e-commerce photography, natural skin texture, true-to-life
<fabric>, sharp focus throughout, no motion blur.
```

Run **3 variants** and pick. `seed` is ignored on Pro, so variants come free from
re-running the same prompt. Judge them on, in order: (1) print fidelity, (2) fit and drape,
(3) framing margins, (4) face. Copy the winner to `hero-selected.png` — that filename is
the contract for step 2.

### Step 2 — fan-out template

```text
Image 1 is the approved hero shot. [Image 2 is <the back / a fabric macro>.]

Keep the SAME woman (identical face, hair, skin tone and build), the SAME <garment>
with its print unchanged in shape, colour, size and position, the SAME <bottoms> and
<shoes>, and the SAME seamless <colour> studio backdrop and soft even lighting.

Change only <the pose and camera>: <one concrete physical description>.

Photorealistic fashion e-commerce photography, sharp focus, no motion blur,
no extra text or logos.
```

---

## Shot catalogue

A standard 8-image PDP set. Ready-to-paste `Change only…` bodies are in
[`references/shot-library.md`](references/shot-library.md).

| # | Shot | References | Size |
|---|---|---|---|
| 1 | Three-quarter turn | hero | 1760x2352 |
| 2 | Walking, mid-stride | hero | 1760x2352 |
| 3 | Hands in pockets | hero | 1760x2352 |
| 4 | Low angle (worm's-eye) | hero | 1760x2352 |
| 5 | Waist-up crop | hero | 1760x2352 |
| 6 | Back view | hero + back.png | 1760x2352 |
| 7 | Neckline / fabric macro | **closeup + front** (`use_hero: false`) | 2048x2048 |
| 8 | Print macro | **front + closeup** (`use_hero: false`) | 2048x2048 |

Shots 7-8 are **flat-lay product shots of the garment alone** — no person in frame. They
restate their own lighting (no hero to inherit it from) and must negate human presence
explicitly; see the macro section of the shot library.

Extend with: seated, arms crossed, side profile, hem/sleeve detail, folded flat-lay,
colourway swap, or a lifestyle background swap. Same template either way.

---

## Running it

```bash
python scripts/run_workflow.py step1 --out v1
# review generated/v1/step-1-hero/hero_v*.png, then:
cp generated/v1/step-1-hero/hero_v3.png generated/v1/step-1-hero/hero-selected.png
python scripts/run_workflow.py step2 --out v1 --hero generated/v1/step-1-hero/hero-selected.png

# re-roll individual shots after a prompt tweak
python scripts/run_workflow.py step2 --out v1 --hero ... --only fanout-4-lowangle
```

`--out <label>` writes to `generated/<label>/` — keep each round of prompt changes in its
own folder so the customer can compare versions. Omit it to write to `generated/`.

Copy `scripts/prompts.example.json` to `prompts.json` and edit. Auth comes from
`ARK_API_KEY` or `~/.seedream/credentials`. Calls run 4-wide; a full set is ~8 calls.

---

## QC checklist

Check every fan-out against the hero, not against the brief:

- [ ] **Print** — artwork identical in shape, colour and proportion; spelling correct; no
      drift in size or chest position.
- [ ] **Identity** — same face, same hair length and parting, same build.
- [ ] **Styling** — same wash of denim, same sneaker silhouette; nothing added
      (jewellery, watches, belts creep in).
- [ ] **Set** — same backdrop colour and the same floor-to-wall line height.
- [ ] **Brief** — the shot actually did the thing it was named for. This is the most
      common miss; see below.
- [ ] **Anatomy** — hands, especially in pocket and walking shots.

Re-roll individual shots freely — each is one independent call.

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Camera direction ignored (asked low-angle, got eye-level) | Abstract camera language reads as style, not geometry | Describe the *physical* rig and its consequences: "camera on the floor at knee height tilted upward, sneakers largest and nearest in the lower third, verticals converging, backdrop curve high in frame". State that the angle is the point of the shot. |
| A "front" macro comes back showing the nape | Neck macros are ambiguous; the training prior for visible care labels is the back | Say "the FRONT of the garment, shot from the front" and negate explicitly: "never the back of her neck or the nape". |
| Model identity drifts across the set | On-model fan-outs generated from the original garment refs instead of the hero | Always pass the hero as Image 1 for any shot containing a person. |
| Macro print looks softer or subtly off vs. the source | Macro routed through the hero — a copy of a copy | Set `"use_hero": false` and feed the brand's originals directly. |
| **A neck, chin, hair or shoulder appears in a garment macro** | "Macro of the garment" is not a negation. Nearly every garment macro in training data has a body in it, so one is supplied by default | Say **"flat-lay, laid flat and face-up, photographed from directly above"**, then negate by name: "no person and no mannequin anywhere in the frame… no skin, no neck, no chin, no hair, no body underneath the fabric. Nothing but cloth." |
| Collar or seam creeps into a print-only macro | Same cause — the model reconstructs the garment around the print | Negate the parts individually: "no collar, no neckline, no hem, no sleeve, no seam in frame". |
| Artwork in a flat-lay macro comes out rotated or off-centre | "Flat-lay from directly above" fixes the *camera*, not the *garment's* rotation under it | Constrain the artwork itself: "UPRIGHT AND PERFECTLY LEVEL — the wordmark runs exactly horizontal and parallel to the bottom edge of the frame… do not rotate, tilt, skew or offset." Re-roll; this one varies run to run. |
| Macro loses the studio look | No hero to inherit lighting from | State the lighting in the macro prompt itself. |
| Print subtly redrawn or recentred | `MUST PRESERVE` block dropped from a fan-out prompt to save length | Keep it verbatim in every prompt. It is the cheapest insurance in the workflow. |
| Care-label micro-text garbles at extreme macro | Below the model's legible-text floor | Accept, or crop tighter so the label is out of frame. |
| Extra logos / text appear | No negative constraint | Keep "no extra text or logos" in every prompt. |
| Aspect ratio varies across the set | `size` preset `2K` lets the model choose the aspect from the prompt | Always pass explicit `WxH`. |

---

## Constraints worth knowing (Seedream 5.0 Pro)

- `size`: presets `1K` / `2K` only (**no 4K**), or explicit `WxH` — total pixels in
  `[921,600 , 4,194,304]`, each dimension a multiple of 16.
- Up to **10** reference images per call; **one** output image per call.
- **Not supported** (these error): `sequential_image_generation`, `stream`,
  `guidance_scale`, `size: "4K"`. `seed` is accepted but has no effect.
- `output_format`: `png` or `jpeg`. `watermark: false` to disable.
- Full parameter reference: `../../SEEDREAM_5_0_PRO_REQUESTS.md`.

## Rights

Only run this on garment photography the brand owns or is licensed to use. The output
depicts a synthetic model — check the destination market's disclosure rules for AI-generated
models in advertising (several jurisdictions now require a label).

## Worked example

`test_case/tshirt-2-workflow/` — 3 mannequin refs ➜ 3 hero variants ➜ 8 fan-outs, with
the exact prompts in `prompts.json` and outputs under `generated/`.
