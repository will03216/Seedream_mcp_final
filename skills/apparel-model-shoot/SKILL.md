---
name: apparel-model-shoot
description: Turn flat-lay / mannequin / ghost-mannequin product photos into a full on-model e-commerce shoot with BytePlus Seedream 5.0 Pro. Build one hero on-model image, then fan out a consistent PDP set (poses, angles, back view, fabric and detail macros) from it. Per-category shot lists for tops, knitwear, jeans and denim, skirts, dresses, outerwear, footwear and bags, plus reusable campaign looks. Use for apparel catalogue production, PDP image sets, model swaps, seasonal campaign re-shoots, and lookbook expansion.
version: 2.0.0
---

# Apparel Model Shoot — mannequin ➜ hero ➜ fan-out set

Replaces a physical model shoot for apparel and soft accessories. Input is whatever the
brand already has (flat lay, mannequin, ghost mannequin, detail macros). Output is a full PDP
image set on a consistent model, in a consistent studio.

A shoot is three choices: a **campaign** (the look), a **category** (the shot list), and a
**product** (the garment). Eight categories ship, from tees to jeans to footwear.

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

Every shot's full prompt lives in its category file — see
[`references/categories.md`](references/categories.md) for the shot lists and
[`references/shot-library.md`](references/shot-library.md) for archetypes to paste when
extending a set.

Run **3 hero variants** and pick one. `seed` is ignored on Pro, so variants come free from
re-running the same prompt. Judge them in this order: (1) print/detail fidelity, (2) fit and
drape, (3) framing margins, (4) face. Copy the winner to `hero-selected.png` — that filename
is the contract for step 2.

---

## Composition model

A prompt is composed from three files, then written out flat:

```
templates/campaigns/<id>.json   the look    (model, set, light, camera, wardrobe slots)
templates/categories/<id>.json  the shots   (shot list, blocks, preserve_fields)
<product>/product.json          the garment (refs by role, garment paragraph)
                    │
                    ▼  scripts/compose.py
            prompts.json  ← flat, committed, diffable, hand-editable
```

**Composition is a build step.** Run `render` and read the composed `prompts.json` — that is
the artifact, and it is the same format the runner has always consumed, so specs written
before the template layer keep working untouched.

**Wardrobe slots.** A campaign declares named slots (`top`, `bottom`, `outer`, `footwear`) and
knows nothing about categories. A category says which slot the *product* occupies and which
others to render — so a tee is shot over the campaign's jeans, while jeans are shot under the
campaign's top. Adding a category costs zero campaign edits.

Schemas, substitution rules and hazards: [`references/authoring.md`](references/authoring.md).

## Categories

| Category | Shots | Hero | Status |
|---|---|---|---|
| `top` — tees, shirts, blouses | 10 | full body | **validated** |
| `knitwear` — jumpers, cardigans | 7 | full body | draft |
| `bottom-denim` — jeans, trousers | 9 | full body | draft |
| `skirt` | 7 | full body | draft |
| `dress` — one-piece | 8 | full body | draft |
| `outerwear` — jackets, coats | 8 | full body | draft |
| `footwear` — shoes, boots | 7 | on-body crop | draft |
| `bag` — handbags, totes | 7 | on-body crop | draft |

**`validated` means real references, full set generated and reviewed. `draft` means authored
and proven to compose, but never generated.** Only `top` is validated — say so in a customer
call.

Per-category shot lists and the reasoning behind them:
[`references/categories.md`](references/categories.md). Shot archetypes to paste when
extending a set: [`references/shot-library.md`](references/shot-library.md).

Activewear, swimwear and suiting are **product specs**, not categories — a legging is
`bottom-denim` with different `preserve_fields`.

---

## Running it

```bash
# 1. compose and read the prompts before spending anything
python3 scripts/run_workflow.py render --spec my-product/product.json --qc

# 2. three hero variants, pick one
python3 scripts/run_workflow.py step1 --spec my-product/product.json --out v1
cp generated/v1/step-1-hero/hero_v3.png generated/v1/step-1-hero/hero-selected.png

# 3. the rest of the set
python3 scripts/run_workflow.py step2 --spec my-product/product.json --out v1 \
        --hero generated/v1/step-1-hero/hero-selected.png

# re-roll one shot after a prompt tweak
python3 scripts/run_workflow.py step2 --spec ... --out v1 --hero ... --only fanout-4-lowangle

# re-shoot the entire set under a different look
python3 scripts/run_workflow.py step1 --spec ... --campaign golden-hour-rooftop --out v2
```

`--out <label>` writes to `generated/<label>/` — keep each round in its own folder so
versions stay comparable. `--spec` also accepts a flat `prompts.json`, which is used verbatim.

Verify offline at any time, no credentials needed:

```bash
python3 scripts/test_compose.py
```

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
