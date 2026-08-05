# Shot library — archetypes

**This is the archetype catalogue, not the shipped shot lists.** Each category's actual set
lives in `templates/categories/<id>.json`, with the reasoning in
[`categories.md`](categories.md). Come here to *extend* a set: these are the poses, crops and
macro setups that work, with the reason each works, written so you can paste one into a
category file and adapt it.

The examples below are written for a **top**; the mechanics transfer to any category. In a
category file the concrete wording is replaced by placeholders — `{{wardrobe}}`,
`{{campaign.set}}`, `{{product.short_name}}` — see [`authoring.md`](authoring.md).

Every on-model shot follows the same envelope:

```text
{{ref_roles_sentence}} {{blocks.keep_onmodel}}

<<< THE ONE THING THIS SHOT IS FOR >>>

{{blocks.tail}}
```

The KEEP block is deliberately repeated in full on every shot. That repetition is what holds a
set together — de-duplicate the *source*, never the *rendered prompt*.

---

## 1 · Three-quarter turn — `1760x2352`, no extra ref

> Change only the pose and camera: full-body three-quarter view, her body turned about 35
> degrees to her right while her head turns back to the lens with a soft closed-lip smile,
> weight on the back foot, front foot slightly forward, one arm relaxed at her side and the
> other hand grazing her thigh. Eye-level, 85mm, head-to-toe framing, model centred.

## 2 · Walking — `1760x2352`, no extra ref

> Change only the pose and camera: full-body walking shot, mid-stride striding toward the
> lens, one foot lifted just off the floor, arms swinging naturally, hair and the hem of the
> garment lifting slightly with the movement, looking into the lens with an easy expression.
> Eye-level, 85mm, head-to-toe framing.

Append `crisp frozen motion, everything in sharp focus, no motion blur` — without it the
model adds shutter drag.

## 3 · Hands in pockets — `1760x2352`, no extra ref

> Change only the pose and camera: full-body front view, both thumbs hooked into the front
> pockets of her jeans with hands relaxed, weight shifted onto one hip, shoulders loose, chin
> slightly lifted, calm confident expression. The chest print stays fully visible and
> unobstructed. Eye-level, 85mm, head-to-toe framing.

## 4 · Low angle — `1760x2352`, no extra ref

Abstract phrasing ("dynamic low angle") is ignored. Describe the rig and its consequences,
and say the angle is the point:

> Change only the camera and pose — THE CAMERA POSITION IS THE POINT OF THIS SHOT: place the
> camera on the floor at knee height, close to her feet, and tilt it upward so we look UP at
> her. Worm's-eye perspective: her shoes and shins are large and nearest to the lens in the
> lower third, her legs converge upward, the garment and her face are seen from below with
> the underside of her chin and jawline visible, and the backdrop's floor-to-wall curve sits
> high in the upper part of the frame. Verticals converge toward the top. She stands with
> feet apart in a relaxed power stance, arms at her sides, looking down into the lens with a
> calm confident expression. 35mm wide-angle look, full body head-to-toe, model centred. The
> chest print stays fully readable despite the foreshortening.

## 5 · Waist-up crop — `1760x2352`, no extra ref

Drop `<bottoms> and <shoes>` from the KEEP block — they are out of frame.

> Change only the framing and pose: waist-up portrait crop, front view, head and shoulders in
> the upper third and the full chest print clearly readable in the lower two thirds. Arms
> relaxed and dropping out of the bottom of frame, gentle closed-lip smile, looking into the
> lens. Eye-level, 85mm, shallow background falloff.

Append `natural skin texture, visible fabric weave and soft print texture`.

## 6 · Back view — `1760x2352`, **+ the brand's back reference as Image 2**

The hero alone cannot invent the back print. Pass the original back photo and re-state its
artwork in full.

> Image 1 is the approved hero shot of the model. Image 2 is the BACK of the same garment
> photographed on a mannequin.
>
> Produce the back view of the same shot: the SAME woman (identical hair, skin tone and
> build) seen from directly behind, standing upright, arms relaxed at her sides, hair falling
> over her shoulders. SAME <bottoms> and <shoes>, SAME seamless <colour> studio backdrop and
> soft even lighting, SAME full-body head-to-toe framing at eye level.
>
> MUST PRESERVE EXACTLY from Image 2: the back print — <describe the artwork element by
> element, with all wording in double quotes, top to bottom> — reproduced with identical
> letterforms, colours, proportion and placement across the upper back, following the natural
> drape of the fabric. Keep the <colour> fabric, the <fit>, <seams> and <sleeves>. Do not add
> any extra text, logo or graphic.

---

# Macros — the exception: **product shots, no hero, no person**

Shots 7 and 8 are not on-model images at all. They are **flat-lay product photography of the
garment alone** — the detail tiles that sit alongside the model shots on a PDP. Nothing human
appears in them.

That drives two rules:

1. **No hero.** They carry no identity, so the hero adds nothing and makes the artwork a copy
   of a copy. Set `"use_hero": false` and feed the brand's product references directly.
2. **No person, stated as a hard negative.** "Macro of the garment" is not enough — the model
   will happily supply a neck, a chin, hair or body curvature under the cloth because almost
   every garment macro in its training data has a body in it. You must name the absence.

Because there is no hero to inherit from, both prompts also state their own lighting.

Both are square `2048x2048`. Say **flat-lay, laid flat, photographed from directly above** —
that single phrase is what removes the implied body.

## 7 · Neckline / fabric macro — `2048x2048`, refs: **closeup + front**, no hero

> Image 1 is a macro of the garment's neckline, fabric and print. Image 2 is the full front
> of the same garment on a mannequin.
>
> Produce a square macro detail photograph of the GARMENT ALONE — flat-lay product
> photography, no person and no mannequin anywhere in the frame. The garment is laid flat and
> face-up on a smooth <colour> surface and photographed from directly above, the fabric
> relaxed with soft natural creases.
>
> Framing: tight crop on the ribbed crew neckline. The collar arcs across the upper third of
> the frame, the neck opening lies open below it revealing the inside back neck with its small
> woven care labels, and the uppermost edge of the print enters at the bottom edge.
>
> ABSOLUTELY NO human presence: no skin, no neck, no throat, no chin, no jaw, no hair, no
> shoulders, no body underneath the fabric. Nothing but cloth.
>
> MUST PRESERVE EXACTLY from Image 1: the <colour> fabric and its fine knit texture, the
> ribbed collar with its topstitching and seam, the woven care labels, and the crisp matte
> print sitting on the fabric weave. Do not redraw, recolour or reposition the print. Do not
> add any extra text, logo or graphic.
>
> Soft even large-softbox light, gentle shadow in the fabric folds.
>
> Extreme detail macro product photography, 100mm macro look, razor-sharp fabric texture,
> even depth of field.

Care-label micro-text will garble at this magnification. Accept it or crop tighter.

## 8 · Print macro — `2048x2048`, refs: **front + closeup**, no hero

The whole artwork, flat and parallel to the sensor, floating in blank fabric. No garment
architecture in frame at all — the collar creeping in is the usual miss, so negate it by name.

> Image 1 is the full front of a garment on a mannequin. Image 2 is a macro of the same
> garment's fabric and print texture.
>
> Produce a square macro detail photograph of the PRINT ALONE — flat-lay product photography,
> no person and no mannequin anywhere in the frame. The garment is laid flat and face-up on a
> smooth <colour> surface and photographed from directly above, square-on and parallel to the
> fabric, relaxed with only faint natural creases.
>
> Framing: the frame is filled edge to edge by <fabric> with the complete artwork centred —
> <describe the artwork, wording in double quotes> — the whole artwork visible with a
> comfortable margin of blank fabric all around it. The artwork must sit UPRIGHT AND PERFECTLY
> LEVEL: the lines of the wordmark run exactly horizontal and parallel to the bottom edge of
> the frame, <the emblem> sits directly above the wordmark on a vertical centre line, and the
> artwork is centred both left-to-right and top-to-bottom. Do not rotate, tilt, skew or offset
> the artwork. No collar, no neckline, no hem, no sleeve, no seam in frame — nothing but the
> printed panel.
>
> ABSOLUTELY NO human presence: no skin, no hands, no arms, no neck, no hair, no body
> curvature under the fabric. Nothing but flat cloth.
>
> MUST PRESERVE EXACTLY from the references: the artwork's shape, letterforms, spelling,
> colours and proportion, plus the soft matte print texture visibly sitting on the fabric
> weave, with faint fibres breaking the ink edges. Do not redraw, recolour, resize or
> reposition the print. Do not add any extra text, logo or graphic.
>
> Soft even large-softbox light, near-shadowless.
>
> Extreme detail macro product photography, 100mm macro look, razor-sharp texture, flat even
> depth of field.

### If you *do* want an on-body detail tile

Some brands prefer the print shown on the worn garment. That is a different shot — give it
the hero (`use_hero: true`), keep the identity KEEP block, and ask for "the soft weight and
folds of a garment on a living body". Do not try to get both from one prompt; the flat-lay
and the worn crop pull in opposite directions.

---

## Extensions

Same envelope, swap the body:

- **Side profile** — "full-body side view, her left shoulder to the lens, looking straight
  ahead, arms at her sides; the silhouette of the shoulder seam and hem is the subject."
- **Seated** — "seated on a matching <colour> cube, elbows on knees, leaning slightly
  forward; the garment falls in soft folds; full body, eye-level."
- **Arms crossed** — "front view, arms folded across her chest below the print, weight on one
  hip. The print stays fully visible above her forearms."
- **Hem / sleeve detail** — "macro of the <hem / cuff> as worn, the stitch line running
  diagonally across the frame, hand or hip just out of focus behind."
- **Colourway** — add to CHANGE: "recolour the garment body to <colour>, keeping the print
  artwork, its colours and its position exactly as they are." Verify the print did not
  re-tint to match.
- **Lifestyle background** — "replace the studio backdrop with <location>, <light>. Keep the
  model, pose, garment and camera framing identical; relight her to match the new
  environment." Do this last, from an approved studio shot.
