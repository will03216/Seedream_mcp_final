# tshirt-2-workflow — worked example

Reference implementation for the [`apparel-model-shoot`](../../skills/apparel-model-shoot/README.md)
skill. Model `dola-seedream-5-0-pro-260628`, 2K, watermark off, PNG.

| Folder | Contents |
|---|---|
| `step-0-input-references/` | Brand's existing photography: mannequin front, mannequin back, neckline macro. |
| `step-1-hero-image/`, `step-2-fan-outs/` | Target references supplied with the test case. |
| `generated/` | First pass — macros still on-model. Superseded. |
| `generated/v1/` | Second pass — macros moved off the hero, still had a person in them. Superseded. |
| `generated/v2/` | **Current set** — 3 hero variants (`hero-selected.png` = v3) + 8 fan-outs, all QC-passed. |
| `prompts.json` | Every prompt used, verbatim. |
| `run_workflow.py` | Local copy of the skill's runner. |

```bash
python3 run_workflow.py step1 --out v2
cp generated/v2/step-1-hero/hero_v3.png generated/v2/step-1-hero/hero-selected.png
python3 run_workflow.py step2 --out v2 --hero generated/v2/step-1-hero/hero-selected.png
```

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
