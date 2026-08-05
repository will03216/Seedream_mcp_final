# tshirt-2-workflow — worked example

Reference implementation for the [`apparel-model-shoot`](../../skills/apparel-model-shoot/README.md)
skill. Model `dola-seedream-5-0-pro-260628`, 2K, watermark off, PNG.

| Folder | Contents |
|---|---|
| `step-0-input-references/` | Brand's existing photography: mannequin front, mannequin back, neckline macro. |
| `step-1-hero-image/`, `step-2-fan-outs/` | Target references supplied with the test case. |
| `generated/` | First pass — macros still on-model. Superseded. |
| `generated/v1/` | Second pass — macros moved off the hero, still had a person in them. Superseded. |
| `generated/v2/` | Hand-written flat spec, 8 fan-outs. Superseded. |
| `generated/v3/` | **Current set** — composed from `product.json`, 3 heroes (`hero-selected.png` = v1) + **9** fan-outs. |
| `generated/v3-golden/` | 2 heroes under the `golden-hour-rooftop` campaign — proof the look is swappable. |
| `product.json` | The composed spec's source: campaign + category + garment. |
| `prompts.json` | Every prompt used, verbatim. |
| — | The runner lives in the skill: `../../skills/apparel-model-shoot/scripts/run_workflow.py` |

```bash
SK=../../skills/apparel-model-shoot/scripts/run_workflow.py

python3 $SK render --spec product.json --qc          # read the prompts first
python3 $SK step1  --spec product.json --out v3
cp generated/v3/step-1-hero/hero_v1.png generated/v3/step-1-hero/hero-selected.png
python3 $SK step2  --spec product.json --out v3 --hero generated/v3/step-1-hero/hero-selected.png

# same garment, different look
python3 $SK step1  --spec product.json --campaign golden-hour-rooftop --runs 2 --out v3-golden
```

The old hand-written `prompts.json` still works unchanged — a spec containing `step2_fanouts`
is used verbatim.

Auth from `ARK_API_KEY` or `~/.seedream/credentials`. 11 calls for the full set.

## Notes from these runs

- All 3 hero variants were usable in all three rounds. v3 won each time on print fidelity and
  oversized drape — a stable enough pattern to expect, not to rely on.
- Both prints reproduce accurately, including the back wordmark and the woven care labels
  visible through the neck opening.
- Three prompt fixes, all now folded into the skill:
  - **low angle** rendered eye-level until the camera rig was described physically;
  - the **neckline macro** rendered the nape until "front" was stated and the nape negated;
  - **fanouts 7 and 8** are flat-lay product macros, not on-model shots. Two corrections:
    they now run from the product references alone (`"use_hero": false`), and they explicitly
    negate any human presence. "Macro of the garment" was not enough — the model supplied a
    neck, chin and hair by default, because virtually every garment macro it has seen has a
    body in it. Saying "flat-lay, laid flat, photographed from directly above" plus a named
    negation ("no skin, no neck, no chin, no hair, no body underneath the fabric") fixed both.
    Shot 8 is also square 2048x2048, matching the supplied target.
  - the **print macro** came back rotated and off-centre in v2. "Flat-lay from directly above"
    constrains the camera, not the garment's rotation under it, so the artwork itself now has
    to be pinned: "upright and perfectly level, wordmark parallel to the bottom edge, do not
    rotate, tilt, skew or offset". This one varies run to run — re-roll if it drifts.
- Care-label micro-text garbles slightly at 2048px macro — the legible-text floor.

## v3 — first run through the composed template layer

- All 9 fan-outs passed QC. Identity, garment, styling and set held across the set.
- **The new back-print macro is the headline result.** At full length (`fanout-6-backview`)
  the back print is small and soft; in the dedicated macro every character is crisp —
  "Condé Nast" with its accent, "Traveler Club", the half-sun disc, level and centred. That is
  the finding that motivated the shot, reproduced.
- Both front macros came out cleaner than any earlier round: cloth only, level, centred.
- **Campaign swap works.** `--campaign golden-hour-rooftop` re-cast the model (male, different
  build and colouring), moved the set to a rooftop at golden hour, swapped the wardrobe to grey
  trousers and tan boots, and changed the grade — with the chest print preserved intact. One
  flag, no prompt edits.
- The documented cream-on-warm-concrete contrast risk did **not** materialise: the low sun
  backlights the model and rim-lights the shoulders, which separates the garment as effectively
  as tonal contrast would. The hazard note in `authoring.md` was corrected to say so.
