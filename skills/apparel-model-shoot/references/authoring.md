# Authoring — schemas, slots, substitution

Three layers compose into one flat `prompts.json`:

```
templates/campaigns/<id>.json   the look    — reusable across every product
templates/categories/<id>.json  the shots   — reusable across every brand
<product>/product.json          the garment — per SKU
```

**Composition is a build step, not a runtime binding.** `render` writes a flat spec in the
format the runner has always consumed. That file is the artifact you read, diff, hand-edit
and commit — nobody should have to mentally join three files to work out what the model was
actually told.

```bash
python3 scripts/run_workflow.py render --spec my-product/product.json --qc
```

---

## Campaign

The look. Knows nothing about garment categories.

| Field | |
|---|---|
| `id`, `label`, `status` | |
| `model_casting` | prose describing the model |
| `pronoun` | `{noun, subject, object, possessive}` — **not optional politeness.** Nine prompts say "woman"/"her"; without this a male-model campaign is nine hand-edits |
| `model_reference` | default `null` — see Hazards |
| `set` / `set_short` | full form for the hero, condensed for fan-out KEEP blocks |
| `light` / `light_short` | same split |
| `camera_full_body`, `camera_crop` | |
| `grade` | the photographic style tail |
| `flatlay_surface`, `flatlay_light` | for product macros |
| `footwear_noun` | bare noun ("sneakers"/"boots") so prose can say "her sneakers" |
| `accessories_rule` | |
| `wardrobe` / `wardrobe_short` | slot map: `top`, `bottom`, `outer`, `footwear` — any may be `null` |
| `sizes` | `{full_body, crop, macro}` — set-level, because "never mix aspect ratios in one PDP set" is a set rule |

**Why full and short forms.** The hero states the set in full; fan-out KEEP blocks restate it
condensed. Both wordings are load-bearing and were validated as-is.

## Category

The shot list. Knows nothing about a specific garment or look.

| Field | |
|---|---|
| `id`, `label`, `status`, `note` | |
| `hero_kind` | `on-model-full-body` or `on-body-crop` |
| `product_slot` | which wardrobe slot the product occupies |
| `styling_slots` | which other slots to render |
| `suppress_slots` | slots this garment replaces (a dress suppresses `top` and `bottom`) |
| `garment_noun`, `garment_noun_short` | |
| `preserve_fields` | list — feeds the `MUST PRESERVE` prose **and** the QC checklist |
| `required_ref_roles`, `optional_ref_roles` | |
| `ref_descriptions` | `{role: prose}`, overridable per shot |
| `blocks` | named fragments, referenced as `{{blocks.name}}` |
| `hero` | `{id, size_class, ref_roles, runs, prompt}` |
| `fanouts[]` | `{id, size_class, use_hero, ref_roles, requires_ref_roles, optional, hero_label, ref_descriptions, prompt}` |

**`blocks` lives inside each category file, not in a shared blocks.json.** A category file
must be readable as a self-contained unit. Cross-category duplication of envelopes is fine —
the envelopes genuinely differ (denim's KEEP names rise/leg/wash, a top's names
neckline/sleeve/hem).

**The whole shot prompt is the template, not an envelope plus a "change" clause.** Four of the
eight validated tee shots deviate structurally: the waist-up crop *drops* bottoms and shoes
from KEEP, the back view replaces KEEP wholesale, and the two macros restate their own
lighting and add a human-presence negation. Fill-in-the-blank models the easy shots and
forces hacks on the hard ones.

## Product

| Field | |
|---|---|
| `campaign`, `category` | ids, or paths to `.json` files |
| `model` | Seedream model id |
| `product` | `{name, short_name, fabric, garment, garment_short, artwork_front, artwork_back, …}` — any key referenced as `{{product.*}}` |
| `refs` | **by role**, not position: `{front, back, detail, inside, sole, …}` |
| `overrides` | `{shot_id: {prompt: [...]}}` or `{shot_id: {skip: true}}` |
| `campaign_overrides` | shallow merge, e.g. `{wardrobe: {footwear: "tan loafers"}}` |

`overrides` is the escape hatch that stops anyone forking a category file per product.

---

## The slot mechanic

A campaign declares **named wardrobe slots**. A category says which slot the product occupies
and which others to render. `{{wardrobe}}` is then computed — product slot excluded,
suppressed slots removed, nulls filtered, Oxford-comma joined.

| Category | product slot | renders |
|---|---|---|
| top, knitwear | `top` | bottom + footwear |
| bottom-denim, skirt | `bottom` | top + footwear |
| dress | `dress` (suppresses top, bottom) | footwear |
| outerwear | `outer` | top + bottom + footwear |
| footwear | `footwear` | bottom |
| bag | `accessory` | top + bottom |

Adding a category costs **zero campaign edits**. A category-keyed wardrobe map would be an
N×M matrix requiring every campaign to enumerate every category.

---

## Substitution

`{{dotted.path}}`. Two fixed passes: blocks first, then shot prompts. That's the whole
language.

- Substituted values are **not re-scanned** — a campaign value containing `{{` cannot inject.
- Blocks may **not** reference other blocks; that's an error.
- **Any string field may be a list of strings**, joined with newlines. Use it. Hand-editing a
  1,500-character single-line JSON string is the worst thing about a flat spec.
- Derived values available everywhere: `{{wardrobe}}`, `{{wardrobe_short}}`,
  `{{preserve_fields}}`, `{{ref_roles_sentence}}`, `{{blocks.*}}`.

### `{{ref_roles_sentence}}` — always use it

It generates `"Image 1 is …. Image 2 is …."` from the actual ref list, **after** the hero is
prepended. Hand-writing that sentence is how it silently desyncs: shots 7 and 8 of the tee set
pass the same two references in opposite orders, and adding a ref or flipping `use_hero`
renumbers everything. A stale sentence tells the model the wrong thing about its own inputs.

Per-shot `ref_descriptions` exist because wording is contextual — the first mention of a
garment is indefinite ("a garment"), a later one definite ("the same garment").

### Missing keys: strict, always

Composition fails loudly and reports **every** problem at once — unresolved keys, missing
required ref roles, blocks referencing blocks. There is no lenient mode, deliberately:

- leaving the placeholder in ships `{{campaign.set}}` into a paid API call and a customer
  deliverable;
- substituting empty string produces a silently degraded prompt that reads like a model
  quality problem;
- lenient modes exist to be left on.

There is no escape syntax for a literal `{{`, and a surviving `{{` after render is an error.

### Out of scope, permanently

No conditionals, loops, filters, includes or defaults. **A shot needing a conditional is two
shots, or a product override.** Hold this line — it is what keeps `compose.py` under 300 lines
and the JSON readable by a merchandiser. The first `{{#if hood}}` request will arrive while
authoring outerwear; the answer is a second shot.

---

## Hazards

**Backdrop must contrast with the garment — but separation can come from light, not just
tone.** The validated campaign is a cream tee on a cream backdrop on a cream flat-lay surface,
and it works only because it was tuned that way. Tested on the second campaign: a cream tee on
warm concrete *also* held, because the low sun backlights the model and rim-lights the
shoulders. The lesson is that tonal contrast and lighting separation are interchangeable — a
front-lit warm-concrete campaign would have failed. Check that a garment has one or the other
before you shoot, not after.

**`model_reference` competes with the garment references.** A bare portrait passed as a third
reference fights the garment refs for fidelity, and print fidelity is the number-one QC
criterion. It defaults to `null` and is unvalidated. If you want one model across many
products, prefer reusing an **approved hero from a previous product** — it already carries the
set, light and grade, so it fights the garment less.

**Ten reference images is the hard cap** on Seedream 5.0 Pro, and the hero counts as one.

**`status` is a promise.** Eight category files look like eight supported categories. Only
`top` is `validated`. Don't let a `draft` be shown as proven.

---

## Verifying

```bash
python3 scripts/test_compose.py     # stdlib unittest, no network, no credentials
```

The suite discovers categories and campaigns automatically, so a new file is covered the
moment you write it. The load-bearing test is the **golden byte-diff**: the eight shipped tee
prompts must render byte-identical to `scripts/prompts.example.json`. They are production
ground truth from three full generation rounds — if composition can't reproduce them exactly,
the abstraction has lost something.

A category may **add** shots. It may never alter or drop a validated one.

> The single most likely way to break this skill is to "tidy up" the repeated KEEP block
> during a refactor. DRY-ing the **source** is the point of this design. DRY-ing the
> **rendered prompt** breaks the model — that repetition is what holds a set together. The
> golden test is the only thing standing in the way.
