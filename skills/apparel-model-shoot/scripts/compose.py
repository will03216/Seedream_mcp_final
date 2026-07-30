#!/usr/bin/env python3
"""Compose campaign + category + product into a flat prompts.json.

Composition is a BUILD STEP, not a runtime binding. The output is the same flat
shape run_workflow.py has always consumed — committed, diffable, hand-editable.

    templates/campaigns/<id>.json   the look   (model, set, light, wardrobe slots)
    templates/categories/<id>.json  the shots  (shot list, blocks, preserve_fields)
    <product>/product.json          the garment (refs by role, garment paragraph)
                    |
                    v  compose()
              prompts.json

Substitution is {{dotted.path}} only. No conditionals, loops, filters or includes:
a shot needing a conditional is two shots, or a product override.

Stdlib only — the skill's no-dependency property is load-bearing.
"""
import json, os, re

VAR = re.compile(r"\{\{\s*([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*)\s*\}\}")

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIRS = {"campaigns": "campaigns", "categories": "categories"}


class CompositionError(Exception):
    """Raised once, listing every problem found — iterating one error at a time
    across three files is miserable."""


# ---------------------------------------------------------------- loading

def join_prose(value):
    """Any string field may also be a list of strings, joined with newlines.

    Hand-editing 1500-char single-line JSON is the worst thing about a flat spec,
    and templating makes lines longer, not shorter.
    """
    if isinstance(value, list):
        return "\n".join(value)
    return value


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_template(kind, ref, base_dir):
    """A bare id resolves to templates/<kind>/<id>.json; anything with a separator
    or a .json suffix is treated as a path relative to the product spec."""
    if ref.endswith(".json") or os.sep in ref or "/" in ref:
        return os.path.join(base_dir, ref)
    return os.path.join(SKILL_ROOT, "templates", TEMPLATE_DIRS[kind], ref + ".json")


# ---------------------------------------------------------------- substitution

def deep_get(ctx, dotted):
    cur = ctx
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def render_str(text, ctx, misses, where):
    """Single pass. Substituted values are NOT re-scanned, so a campaign value
    containing '{{' cannot inject."""
    text = join_prose(text)
    if text is None:
        return None

    def repl(m):
        key = m.group(1)
        val = deep_get(ctx, key)
        if val is None:
            misses.append((where, key))
            return m.group(0)
        return join_prose(val)

    return VAR.sub(repl, text)


def render_any(value, ctx, misses, where):
    if isinstance(value, list):
        return "\n".join(render_str(v, ctx, misses, where) or "" for v in value)
    return render_str(value, ctx, misses, where)


# ---------------------------------------------------------------- derived values

def oxford(items):
    """['a'] -> 'a'  ·  ['a','b'] -> 'a and b'  ·  ['a','b','c'] -> 'a, b and c'

    Nulls are filtered structurally rather than with template conditionals, so a
    campaign that dresses no footwear never renders 'worn with  and .'
    """
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def build_wardrobe(wardrobe, product_slot, styling_slots, suppress_slots):
    """Render the slots the model wears BESIDES the product.

    The campaign knows nothing about categories — it just declares named slots.
    The category says which slot the product occupies and which others to show.
    Adding a category therefore costs zero campaign edits.
    """
    out = []
    for slot in styling_slots:
        if slot == product_slot or slot in (suppress_slots or []):
            continue
        out.append(wardrobe.get(slot))
    return oxford(out)


def build_refs(shot, category, product, use_hero, hero_label):
    """Return (ordered ref roles, numbered 'Image N is ...' sentence).

    Generated rather than hand-written because the numbering shifts whenever the
    hero is prepended or a ref is added, and a stale sentence tells the model the
    wrong thing about its own inputs.
    """
    roles = list(shot.get("ref_roles", []))
    # A role's wording depends on context: the first mention is indefinite
    # ("a garment"), a later one definite ("the same garment"), and a hero-less
    # macro introduces the garment itself. Shots may override per role.
    descriptions = dict(category.get("ref_descriptions", {}))
    descriptions.update(shot.get("ref_descriptions", {}))
    parts, ordered = [], []

    if use_hero:
        parts.append(hero_label)
    for role in roles:
        if role in product.get("refs", {}):
            ordered.append(role)
            parts.append(descriptions.get(role, "a reference image of the garment"))

    sentence = " ".join(
        "Image %d is %s." % (i + 1, text) for i, text in enumerate(parts)
    )
    return ordered, sentence


# ---------------------------------------------------------------- shots

def shot_size(shot, campaign):
    if "size" in shot:
        return shot["size"]
    return campaign["sizes"][shot["size_class"]]


def compose_shot(shot, ctx, campaign, category, product, misses, is_hero):
    use_hero = False if is_hero else shot.get("use_hero", True)
    hero_label = shot.get("hero_label", "the approved hero shot")
    roles, sentence = build_refs(shot, category, product, use_hero, hero_label)

    local = dict(ctx)
    local["ref_roles_sentence"] = sentence

    prompt = render_any(shot["prompt"], local, misses, shot["id"])
    entry = {
        "id": shot["id"],
        "size": shot_size(shot, campaign),
        "prompt": prompt,
    }
    if is_hero:
        entry["input_images"] = [product["refs"][r] for r in roles]
        entry["runs"] = shot.get("runs", 3)
    else:
        if not use_hero:
            entry["use_hero"] = False
        entry["extra_refs"] = [product["refs"][r] for r in roles]
    return entry


def shot_availability(shot, product):
    """Return (keep, problem).

    A shot that names a ref role the product doesn't supply cannot be rendered
    honestly: its prose says "MUST PRESERVE from Image 2" while no Image 2 is
    sent. Optional shots are dropped silently — that is what optional means.
    Everything else is a loud error naming the fix.
    """
    have = set(product.get("refs", {}))
    needed = set(shot.get("requires_ref_roles", [])) | set(shot.get("ref_roles", []))
    missing = sorted(needed - have)
    if not missing:
        return True, None
    if shot.get("optional"):
        return False, None
    return False, ("shot '%s' needs ref role%s %s which the product does not "
                   "provide — supply the reference, or mark the shot optional"
                   % (shot["id"], "" if len(missing) == 1 else "s",
                      ", ".join("'%s'" % m for m in missing)))


def apply_overrides(shot, overrides):
    """Product-level escape hatch, so nobody forks a category file per product."""
    patch = (overrides or {}).get(shot["id"])
    if not patch:
        return shot
    if patch.get("skip"):
        return None
    merged = dict(shot)
    merged.update({k: v for k, v in patch.items() if k != "skip"})
    return merged


# ---------------------------------------------------------------- entry point

def compose(product, base_dir, campaign_id=None, category_id=None):
    campaign = load_json(resolve_template(
        "campaigns", campaign_id or product["campaign"], base_dir))
    category = load_json(resolve_template(
        "categories", category_id or product["category"], base_dir))

    for key, value in (product.get("campaign_overrides") or {}).items():
        if isinstance(value, dict) and isinstance(campaign.get(key), dict):
            campaign[key].update(value)
        else:
            campaign[key] = value

    misses, problems = [], []

    for role in category.get("required_ref_roles", []):
        if role not in product.get("refs", {}):
            problems.append("missing required ref role '%s' for category '%s'"
                            % (role, category["id"]))

    ctx = {
        "campaign": campaign,
        "category": category,
        "product": product.get("product", {}),
        "wardrobe": build_wardrobe(
            campaign.get("wardrobe", {}), category["product_slot"],
            category.get("styling_slots", []), category.get("suppress_slots")),
        "wardrobe_short": build_wardrobe(
            campaign.get("wardrobe_short", campaign.get("wardrobe", {})),
            category["product_slot"], category.get("styling_slots", []),
            category.get("suppress_slots")),
        "preserve_fields": oxford(category.get("preserve_fields", [])),
    }

    # Pass 1 — blocks. Blocks may not reference other blocks.
    blocks = {}
    for name, text in (category.get("blocks") or {}).items():
        raw = join_prose(text)
        if "{{blocks." in raw:
            problems.append("block '%s' references another block; blocks are flat"
                            % name)
        blocks[name] = render_str(raw, ctx, misses, "blocks.%s" % name)
    ctx["blocks"] = blocks

    # Pass 2 — shots.
    hero = compose_shot(category["hero"], ctx, campaign, category, product,
                        misses, is_hero=True)

    fanouts = []
    for shot in category.get("fanouts", []):
        shot = apply_overrides(shot, product.get("overrides"))
        if shot is None:
            continue
        keep, problem = shot_availability(shot, product)
        if problem:
            problems.append(problem)
        if not keep:
            continue
        fanouts.append(compose_shot(shot, ctx, campaign, category, product,
                                    misses, is_hero=False))

    for where, key in misses:
        problems.append("unresolved {{%s}} in %s" % (key, where))
    for entry in [hero] + fanouts:
        if "{{" in entry["prompt"]:
            problems.append("placeholder survived render in %s" % entry["id"])

    if problems:
        raise CompositionError(
            "composition failed (%d problem%s):\n  - %s"
            % (len(problems), "" if len(problems) == 1 else "s",
               "\n  - ".join(problems)))

    return {
        "model": product.get("model", "dola-seedream-5-0-pro-260628"),
        "note": "COMPOSED by compose.py from campaign '%s' + category '%s'. "
                "Edit the templates, not this file." % (campaign["id"], category["id"]),
        "campaign": campaign["id"],
        "category": category["id"],
        "status": category.get("status", "draft"),
        "step1_hero": hero,
        "step2_fanouts": fanouts,
    }


def qc_checklist(product, base_dir, campaign_id=None, category_id=None):
    category = load_json(resolve_template(
        "categories", category_id or product["category"], base_dir))
    lines = ["# QC checklist — %s" % category["label"], ""]
    lines.append("Check every fan-out against the approved hero, not against the brief.")
    lines.append("")
    for field in category.get("preserve_fields", []):
        lines.append("- [ ] %s" % field)
    for extra in ("Same face, hair and build as the hero",
                  "Same styling and set; nothing added",
                  "The shot did what it is named for",
                  "Hands and anatomy",
                  "Flat-lay macros contain no person at all"):
        lines.append("- [ ] %s" % extra)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise SystemExit("usage: compose.py <product.json> [out.json]")
    spec_path = os.path.abspath(sys.argv[1])
    result = compose(load_json(spec_path), os.path.dirname(spec_path))
    out = sys.argv[2] if len(sys.argv) > 2 else "-"
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if out == "-":
        sys.stdout.write(text)
    else:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote %s" % out)
