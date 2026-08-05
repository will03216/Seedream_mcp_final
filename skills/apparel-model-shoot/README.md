# apparel-model-shoot — how to use

Turn the garment photography a brand already has — flat lays, mannequin shots, ghost
mannequins, detail macros — into a full on-model PDP image set, using BytePlus **Seedream
5.0 Pro** at 2K.

No physical model, no studio, no shoot day. One product, one hero, eight images, about
three minutes.

<table>
<tr><th>You give it</th><th>You get back</th></tr>
<tr><td>front · back · detail macro<br>(mannequin or flat lay)<br>+ a campaign and a category</td>
<td>1 on-model hero + 6–9 PDP shots<br>tailored to the garment type:<br>poses · crops · back view · detail macros</td></tr>
</table>

**Eight categories** — `top` · `knitwear` · `bottom-denim` · `skirt` · `dress` · `outerwear` ·
`footwear` · `bag`. Only `top` is validated against real generations; the rest are authored
and proven to compose but never generated. See
[`references/categories.md`](references/categories.md).

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
├── product.json                 ← copy examples/summer-daze-tee/product.json here
└── refs/
    ├── front.png                ← required: straight-on front
    ├── back.png                 ← for back views and back-detail macros
    └── detail.jpg               ← for the detail macros
```

Some categories accept more roles — `inside` (outerwear lining, bag interior) and `sole`
(footwear). Shots that need a role you don't have are dropped if optional, or raise a clear
error if not.

Use straight-on, evenly lit references. Angled or lifestyle shots fight the hero's geometry —
leave them out.

```bash
mkdir -p my-product/refs
cp skills/apparel-model-shoot/examples/summer-daze-tee/product.json my-product/product.json
```

## 4. Write the product spec

Pick a **campaign** (the look) and a **category** (the shot list), then describe the garment.
That is the whole edit — you no longer copy wording between prompts by hand.

```json
{
  "campaign": "beige-studio-ss26",
  "category": "top",
  "product": {
    "short_name": "cream \"Summer Daze\" oversized tee",
    "fabric": "cotton jersey",
    "garment": "the cream / off-white fabric colour; the oversized boxy fit with dropped
                shoulder seams, short wide sleeves and a straight hem; the ribbed crew neckline",
    "artwork_front": "an orange spiky sun above the two-line retro serif wordmark
                      \"Summer Daze\" in light blue"
  },
  "refs": { "front": "refs/front.png", "back": "refs/back.png", "detail": "refs/detail.jpg" }
}
```

**The `garment` and `artwork` fields are the highest-leverage edit in the whole skill.**
Describe colour, fit, construction, and — word for word, in double quotes — every piece of
text and artwork on it. That text lands in the `MUST PRESERVE` block of every prompt. Vague
here means drift everywhere.

Available campaigns and categories:

```bash
ls skills/apparel-model-shoot/templates/campaigns
ls skills/apparel-model-shoot/templates/categories
```

Need one shot different? Add an override rather than forking a category:

```json
"overrides": {
  "fanout-4-lowangle": { "skip": true },
  "fanout-2-walking":  { "prompt": ["...fully replaced prompt..."] }
}
```

Schemas, the slot mechanic and substitution rules:
[`references/authoring.md`](references/authoring.md).

## 4b. Render and read the prompts before spending anything

```bash
cd my-product
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py render --spec product.json --qc
```

This writes `prompts.rendered.json` — the flat, fully-composed spec, exactly what will be
sent. Read it. Hand-edit it if you like; it can be passed straight to `--spec`. `--qc` also
writes a per-shot checklist derived from the category's `preserve_fields`.

Composition fails loudly: an unresolved placeholder, a missing required reference or a shot
whose reference role you haven't supplied all raise before a single call is made.

## 5. Generate the hero

```bash
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step1 --spec product.json --out v1
```

Three variants land in `generated/v1/step-1-hero/`. Review and pick one, judging in this order:

1. **Detail fidelity** — is the artwork, hardware or stitching the same shape, scale and position as the reference?
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
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step2 --spec product.json --out v1 \
  --hero generated/v1/step-1-hero/hero-selected.png
```

Six to nine images into `generated/v1/step-2-fan-outs/`, four calls at a time, roughly two
minutes.

On-model shots are generated **from the hero**, which is what keeps one model in one studio
across the set. Detail macros are flat-lay product shots with no person in them, so they bypass
the hero and read the brand's references directly (`"use_hero": false`).

Re-shoot the same product under a different look with one flag:

```bash
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step1 --spec product.json \
  --campaign golden-hour-rooftop --out v2
```

## 7. Review and re-roll

Check each fan-out **against the hero**, not against the brief:

- [ ] Product detail identical in shape, colour and position; any text spelled correctly
- [ ] Same face, hair and build
- [ ] Same co-styling and shoes; nothing added (jewellery and watches creep in)
- [ ] Same backdrop colour and floor-line height
- [ ] The shot did the thing it is named for — the most common miss
- [ ] Hands, especially in the pocket and walking shots
- [ ] Macros contain **no person at all**

Any single shot can be re-rolled independently:

```bash
python3 ../skills/apparel-model-shoot/scripts/run_workflow.py step2 --spec product.json --out v1 \
  --hero generated/v1/step-1-hero/hero-selected.png --only fanout-4-lowangle
```

Changed prompts and want to keep the old round for comparison? Use a new label —
`--out v2` writes to `generated/v2/`.

---

## Command reference

| | |
|---|---|
| `render` / `step1` / `step2` | compose only · heroes · the set |
| `--spec <path>` | product spec **or** a flat `prompts.json`; image paths resolve relative to it |
| `--campaign <id>` | override the campaign — re-shoot the set under a different look |
| `--category <id>` | override the category |
| `--out <label>` | write to `generated/<label>/` (on `render`, the output file path) |
| `--hero <path>` | required for `step2` — the approved hero |
| `--runs N` | override the number of hero variants (default 3) |
| `--only <id> …` | regenerate just these shots |
| `--qc` | `render` only — also emit the QC checklist |

Verify offline any time, no credentials needed:

```bash
python3 skills/apparel-model-shoot/scripts/test_compose.py
```

## Adding your own shots

Append an entry to the category's `fanouts` — `id`, `size_class`, `prompt`, optional
`ref_roles`, `use_hero`, `optional` and `requires_ref_roles`. It is picked up automatically,
including by the test suite. Ready-made bodies for side profile, seated, arms crossed, hem
detail, colourway swap and lifestyle background are in
[`references/shot-library.md`](references/shot-library.md); how to add a whole category is in
[`references/categories.md`](references/categories.md).

## Legacy flat specs

A spec containing `step2_fanouts` is treated as already composed and used verbatim, so
`prompts.json` files written before the template layer keep working unchanged.

## Costs and limits

One call per image; a full set is 9–12 calls (3 heroes + 6–9 shots). Seedream 5.0 Pro billing is
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
