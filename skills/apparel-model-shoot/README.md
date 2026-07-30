# apparel-model-shoot — how to use

Turn the garment photography a brand already has — flat lays, mannequin shots, ghost
mannequins, detail macros — into a full on-model PDP image set, using BytePlus **Seedream
5.0 Pro** at 2K.

No physical model, no studio, no shoot day. One product, one hero, eight images, about
three minutes.

<table>
<tr><th>You give it</th><th>You get back</th></tr>
<tr><td>front · back · neckline macro<br>(mannequin or flat lay)</td>
<td>1 on-model hero + 8 PDP shots:<br>three-quarter · walking · hands in pockets · low angle ·
waist-up · back view · fabric macro · print macro</td></tr>
</table>

Worked example with real inputs and outputs: [`../../test_case/tshirt-2-workflow/`](../../test_case/tshirt-2-workflow/).

---

## 1. Install

```bash
git clone https://github.com/byteplus/byteplus-seedream-mcp
cd byteplus-seedream-mcp
```

The runner is plain Python 3 with no third-party dependencies — nothing to `pip install`.

## 2. Authenticate

You need a BytePlus ModelArk API key with access to Seedream 5.0 Pro. Either:

```bash
export ARK_API_KEY=your-modelark-api-key
```

or put it in `~/.seedream/credentials` (the runner checks the env var first, then this file):

```ini
[default]
ark_api_key = your-modelark-api-key
```

That is all. Reference images are sent inline as base64, so no TOS bucket, no `ARK_AK`/`ARK_SK`,
no upload step.

**Check it works:**

```bash
curl -sS -X POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations \
  -H "Authorization: Bearer $ARK_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"dola-seedream-5-0-pro-260628","prompt":"a red apple","size":"1K"}' | head -c 200
```

A JSON body with a `data[0].url` means you are ready.

## 3. Set up a product folder

One folder per garment:

```
my-product/
├── prompts.json                 ← copy scripts/prompts.example.json here and edit
└── refs/
    ├── front.png                ← required: straight-on front
    ├── back.png                 ← for the back view
    └── closeup.jpg              ← for the two macros
```

Use straight-on, evenly lit references. Angled or lifestyle shots fight the hero's geometry —
leave them out.

```bash
mkdir -p my-product/refs
cp skills/apparel-model-shoot/scripts/prompts.example.json my-product/prompts.json
```

## 4. Edit `prompts.json`

Everything the model sees lives in this one file. Three things to change:

**a. Point the paths at your references** — `step1_hero.input_images` and each fan-out's
`extra_refs`, relative to `prompts.json`.

**b. Write the garment paragraph.** This is the single most important edit. Describe colour,
fit, neckline, sleeve, hem, and — word for word, in double quotes — every piece of text and
artwork on the garment. This paragraph goes into the `MUST PRESERVE` block of **every** prompt.
Vague here means drift everywhere.

> …the cream / off-white fabric colour; the oversized boxy fit with dropped shoulder seams,
> short wide sleeves and a straight hem; the ribbed crew neckline; and the chest print — an
> orange spiky sun above the two-line retro serif wordmark **"Summer Daze"** in light blue —
> including its exact shape, letterforms, proportion, colours and centred position…

**c. Cast the model and set.** In `step1_hero.prompt`, edit the `MODEL:`, `STYLING:` and `SET:`
lines, then mirror the same wording into the `Keep the SAME…` line of every fan-out. They must
match verbatim — that repetition is what holds the set together.

Full prompt anatomy and per-shot templates: [`SKILL.md`](SKILL.md) ·
[`references/shot-library.md`](references/shot-library.md).

## 5. Generate the hero

```bash
cd my-product
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step1 --out v1
```

Three variants land in `generated/v1/step-1-hero/`. Review and pick one, judging in this order:

1. **Print fidelity** — is the artwork the same shape, scale and position as the reference?
2. **Fit and drape** — does it hang like the real garment?
3. **Framing** — even margin above the head and below the shoes.
4. **Face** — last, because it is the easiest to re-roll.

```bash
cp generated/v1/step-1-hero/hero_v3.png generated/v1/step-1-hero/hero-selected.png
```

The filename `hero-selected.png` is the contract for step 2. Not happy with any of the three?
Re-run step 1 — `seed` has no effect on Seedream Pro, so every run is a fresh variant.

## 6. Generate the set

```bash
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step2 --out v1 \
  --hero generated/v1/step-1-hero/hero-selected.png
```

Eight images into `generated/v1/step-2-fan-outs/`, four calls at a time, roughly two minutes.

Shots 1-6 are generated **from the hero**, which is what keeps one woman in one studio across
the set. Shots 7-8 are flat-lay product macros with no person in them, so they bypass the hero
and read the brand's references directly (`"use_hero": false` in the spec).

## 7. Review and re-roll

Check each fan-out **against the hero**, not against the brief:

- [ ] Print identical in shape, colour and position; spelling correct
- [ ] Same face, hair and build
- [ ] Same denim wash, same shoes; nothing added (jewellery and watches creep in)
- [ ] Same backdrop colour and floor-line height
- [ ] The shot did the thing it is named for — the most common miss
- [ ] Hands, especially in the pocket and walking shots
- [ ] Macros contain **no person at all**

Any single shot can be re-rolled independently:

```bash
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step2 --out v1 \
  --hero generated/v1/step-1-hero/hero-selected.png --only fanout-4-lowangle
```

Changed prompts and want to keep the old round for comparison? Use a new label —
`--out v2` writes to `generated/v2/`.

---

## Command reference

| | |
|---|---|
| `step1` / `step2` | which stage to run |
| `--spec <path>` | prompt spec (default `prompts.json`); all image paths resolve relative to it |
| `--out <label>` | write to `generated/<label>/` instead of `generated/` |
| `--hero <path>` | required for `step2` — the approved hero |
| `--runs N` | override the number of hero variants (default 3) |
| `--only <id> …` | regenerate just these fan-outs |

## Adding your own shots

Append an entry to `step2_fanouts` — `id`, `size`, `prompt`, optional `extra_refs` and
`use_hero`. It is picked up automatically. Ready-made bodies for side profile, seated, arms
crossed, hem detail, colourway swap and lifestyle background are in
[`references/shot-library.md`](references/shot-library.md).

## Costs and limits

One call per image; a full set is 11 calls (3 heroes + 8 shots). Seedream 5.0 Pro billing is
per output pixel — `output_tokens = width × height / 256`. Hard limits: **no 4K**, one image
per call, up to 10 reference images, and `sequential`, `stream` and `guidance_scale` all error.
Returned URLs expire after 24 hours; the runner downloads immediately.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `KeyError: 'ark_api_key'` | No credentials — set `ARK_API_KEY` or create `~/.seedream/credentials`. |
| `HTTP 400 InvalidParameter` on size | Total pixels must be 921,600–4,194,304 and each dimension a multiple of 16. `4K` is not a valid preset. |
| `[SKIP] … no reference images` | A fan-out has `use_hero: false` and an empty `extra_refs`. |
| Model looks different across shots | A fan-out was run from the product refs instead of the hero. |
| A person appears in a macro | Add the explicit negation — see the macro section of the shot library. |
| Camera angle ignored | Describe the physical camera position, not the style word. |

More failure modes, each with the prompt language that fixes it, in [`SKILL.md`](SKILL.md).

## Before you ship

Only run this on garment photography the brand owns or is licensed to use. The output depicts
a synthetic model — several markets now require AI-generated models in advertising to be
labelled, so check the destination market's disclosure rules.
