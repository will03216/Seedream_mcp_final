# Categories — what each garment type actually needs

Eight categories ship. Shot counts vary because garment types genuinely need different
things; a set padded to a uniform eight would be filler.

| Category | Shots | Hero | Status | Product slot |
|---|---|---|---|---|
| [`top`](#top) | 10 | full body | **validated** | `top` |
| [`knitwear`](#knitwear) | 7 | full body | draft | `top` |
| [`bottom-denim`](#bottom-denim) | 9 | full body | draft | `bottom` |
| [`skirt`](#skirt) | 7 | full body | draft | `bottom` |
| [`dress`](#dress) | 8 | full body | draft | `dress` |
| [`outerwear`](#outerwear) | 8 | full body | draft | `outer` |
| [`footwear`](#footwear) | 7 | on-body crop | draft | `footwear` |
| [`bag`](#bag) | 7 | on-body crop | draft | `accessory` |

> **Status is not decoration.** `validated` means real references, full set generated and
> reviewed. `draft` means authored and proven to compose, but **never generated**. Only
> `top` is validated. Say so in a customer call.

Optional shots are gated on a reference role: if the brand has no `inside` photo, the lining
macro is silently dropped rather than inventing a lining. A **non**-optional shot whose
reference is missing is a loud composition error, because its prose would say "MUST PRESERVE
from Image 2" with no Image 2 attached.

---

## top

Tees, shirts, blouses. The validated set, plus a back-print macro.

| Shot | Hero | Refs |
|---|---|---|
| hero — front, square-on, arms relaxed | step 1 | front + detail |
| three-quarter turn, 35° | ✓ | — |
| walking, mid-stride | ✓ | — |
| hands in pockets | ✓ | — |
| low angle, worm's-eye | ✓ | — |
| waist-up crop, print readable | ✓ | — |
| back full-length | ✓ | back |
| neckline / fabric macro | — | detail + front |
| front-print macro | — | front + detail |
| **back-print macro** | — | back + detail |

**Why the back-print macro.** Fine text on a back print — tour dates, city lists — comes out
*soft at full length* but *crisp and fully legible in a dedicated close-up*. A graphic tee's
back print is often the reason someone buys it, and shipping it only at full length
under-sells it. The rule generalises: **any garment carrying fine text needs its own macro.**

---

## knitwear

Jumpers, cardigans, knit tops. Structurally close to `top`, but the macros are texture-led
rather than print-led.

hero · three-quarter · back full · waist-up crop (neckline rib) · on-body sleeve/cuff ·
knit-texture macro · rib macro.

**Why it's its own category.** `preserve_fields` is gauge, stitch pattern, cable relief and
rib depth — nothing to do with a print. And the texture macros specify **low raking side
light**: flat frontal light renders a knit as flat colour and destroys the only thing the
shot exists to show.

**Why the cuff is shot on the body.** How a cuff rib gathers and holds at the wrist is a wear
property; a flat-lay shows a flat tube.

---

## bottom-denim

Jeans, trousers. The product moves to the `bottom` slot, so the model wears a plain top —
this is the category that stresses the slot mechanic hardest.

| Shot | Hero | Refs | Why |
|---|---|---|---|
| hero — front, hands out of pockets | step 1 | front + detail | Rise, leg line, hem break, front hardware |
| **back full-length** | ✓ | back | **The money shot** |
| back crop, waist to mid-thigh | ✓ | back | Arcuate, rivets, bartacks resolved |
| three-quarter / side, 45° | ✓ | — | Side seam, inseam, leg profile |
| front waist crop | ✓ | detail | Shank button, fly, loops, whiskering |
| walking, mid-stride | ✓ | — | Denim drape and stack in motion |
| hem break over the shoe | ✓ | — | On-body: a wear property |
| flat-lay front + back | — | front + back | True wash and fading pattern |
| hardware macro | — | detail + front | Button, rivets, topstitch |

**Why the back leads.** For denim the seat, yoke, pocket placement and arcuate stitching are
the primary purchase drivers. It carries the longest `MUST PRESERVE` in the category and is
first in the fan-out order.

**Why a back crop as well as a back view.** Same finding as the tee's back print: stitching
at full length reads soft, and stitching is *the* brand signature in denim.

**The category styling rule** — in the file, not left to chance: the top is tucked so the
waistband and rise stay visible, and **hands stay out of the pockets** on every shot but the
pocket crop. A hand in a front pocket hides the exact geometry the shot exists to sell.

---

## skirt

Occupies the `bottom` slot like trousers, but sells on length, volume and movement — so it
gets a movement shot and a seated shot instead of a walking shot.

hero · back full (closure, vent) · three-quarter · movement half-turn · waist crop · seated ·
fabric/hem macro.

---

## dress

One-piece. Occupies a `dress` slot that **suppresses both `top` and `bottom`**, so the
campaign styles footwear only.

hero · back full (zip/tie, back neckline) · three-quarter · **movement half-turn** ·
waist-up crop (bodice, neckline, straps) · **seated** · fabric macro · closure macro.

**Why movement and seated matter more here.** Drape and volume only read in motion, and how a
skirt falls when seated is a common reason for returns — invisible in every standing shot.

---

## outerwear

Jackets, coats, blazers.

| Shot | Hero | Refs |
|---|---|---|
| hero — front, **fastened** | step 1 | front + detail |
| front, **open** | ✓ | — |
| back full-length | ✓ | back |
| three-quarter, hands in pockets | ✓ | — |
| collar / hood crop | ✓ | — |
| closure macro | — | detail + front |
| cuff macro | — | detail |
| lining macro — **optional** | — | inside |

**Why two states.** Half of all outerwear is worn open. The open shot is a normal fan-out
*from the fastened hero* — modelling it as a second step-1 hero would generate a second
person.

**Why hands-in-pockets lives here.** On a tee it is a near-duplicate of the hero. On a coat,
pocket placement is a genuine feature.

**The lining macro is the proof of optional gating.** Most brands never supply an inside
reference. Without gating, the model invents a lining.

---

## footwear

`hero_kind: on-body-crop`. **No face anywhere in the set.**

hero — on-foot three-quarter, lower legs only · side profile (product) · top-down pair
(product) · heel/back (product) · sole macro (product) · on-foot stride crop · material macro.

**Why the hero has no face.** A shoe hero that includes a model's face spends the frame on the
wrong subject. That also means the usual identity KEEP block doesn't apply — there is no face
to hold — so the shots lock the shoe and the trouser hem instead.

**Why any on-body shots at all.** How the hem breaks over the shoe, and how the shoe flexes
mid-stride, are wear properties no product shot can show.

---

## bag

`hero_kind: on-body-crop`. Torso-and-hand crop, no head.

hero — held at the side, torso crop · worn crossbody · product front · product back ·
interior (optional) · hardware macro · strap-attachment macro.

**Why the hero is on a body.** Scale. A bag photographed alone gives a customer no idea how
large it is; a hand and forearm answer it instantly. The set then alternates deliberately:
on-body for scale and drop length, product-only for true colour and construction.

---

## Not categories

**Activewear, swimwear and suiting are product specs, not categories.** A legging is
`bottom-denim` with different `preserve_fields`; a sports bra is `top`; a blazer is
`outerwear`. Write the difference into the product spec's `garment` paragraph and, if needed,
override individual shots. Adding them as categories is how a schema goes fake-general.

## Adding a category

1. Copy the closest existing file in `templates/categories/`.
2. Set `hero_kind`, `product_slot`, `styling_slots` and any `suppress_slots`.
3. Rewrite `preserve_fields` — this is the highest-leverage field; it feeds both the
   `MUST PRESERVE` prose and the QC checklist.
4. Rewrite `blocks`, then the shots. Ask of each shot: *what does this garment type sell on,
   and which shot shows it?* Drop shots that don't earn their slot.
5. Set `"status": "draft"` and leave it there until someone generates a real set.
6. `python3 scripts/test_compose.py` — the suite picks up new categories automatically.

Schemas and the substitution rules: [`authoring.md`](authoring.md).
