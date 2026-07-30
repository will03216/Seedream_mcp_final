#!/usr/bin/env python3
"""Two-step apparel workflow on Seedream 5.0 Pro (2K).  [apparel-model-shoot skill]

  step1  mannequin/flat refs      -> on-model hero (N variants, you pick one)
  step2  chosen hero (+ detail refs) -> fan-out set
         shots marked "use_hero": false run from the product refs alone

Usage:
  python run_workflow.py step1
  python run_workflow.py step2 --hero generated/step-1-hero/hero_v2.png
  python run_workflow.py step2 --hero ... --only fanout-6-backview
  python run_workflow.py step1 --spec path/to/prompts.json
  python run_workflow.py step1 --out v1          # -> generated/v1/step-1-hero/
"""
import argparse, base64, concurrent.futures, configparser, json, mimetypes, os, urllib.request, urllib.error

import compose as _compose

ROOT = os.getcwd()   # overridden by --spec: paths resolve relative to the spec file
URL = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"


_API_KEY = None


def api_key():
    """Resolved lazily and memoised. Resolving at import time would make every
    offline path — compose, render, the test suite — require credentials."""
    global _API_KEY
    if _API_KEY is None:
        key = os.environ.get("ARK_API_KEY")
        if not key:
            cfg = configparser.ConfigParser()
            cfg.read(os.path.expanduser("~/.seedream/credentials"))
            key = cfg["default"]["ark_api_key"]
        _API_KEY = key
    return _API_KEY


def to_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def generate(prompt, images, size):
    if len(images) > 10:
        raise ValueError("Seedream 5.0 Pro accepts at most 10 reference images; got %d"
                         % len(images))
    body = {
        "model": SPEC["model"],
        "prompt": prompt,
        "size": size,
        "watermark": False,
        "output_format": "png",
    }
    if len(images) == 1:
        body["image"] = to_data_uri(images[0])
    elif images:
        body["image"] = [to_data_uri(p) for p in images]
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def run_one(name, prompt, images, size, outdir):
    os.makedirs(outdir, exist_ok=True)
    try:
        resp = generate(prompt, images, size)
    except urllib.error.HTTPError as e:
        print(f"[FAIL] {name}: HTTP {e.code} {e.read().decode()[:300]}", flush=True)
        return None
    except Exception as e:
        print(f"[FAIL] {name}: {e}", flush=True)
        return None
    data = resp.get("data") or []
    if not data or not data[0].get("url"):
        print(f"[FAIL] {name}: {json.dumps(resp)[:300]}", flush=True)
        return None
    out = os.path.join(outdir, f"{name}.png")
    with urllib.request.urlopen(data[0]["url"], timeout=180) as r, open(out, "wb") as f:
        f.write(r.read())
    print(f"[ OK ] {name} -> {out} ({data[0].get('size')})", flush=True)
    return out


SPEC = None


def load_spec(spec_path, campaign=None, category=None):
    """Load a spec. Image paths resolve relative to its directory.

    A spec carrying "step2_fanouts" is already flat and is used as-is — that check
    is the whole backward-compatibility contract, so specs written before the
    template layer existed keep working untouched. Anything else is a product spec
    and gets composed from its campaign + category.
    """
    global SPEC, ROOT
    spec_path = os.path.abspath(spec_path)
    ROOT = os.path.dirname(spec_path)
    raw = _compose.load_json(spec_path)
    SPEC = raw if "step2_fanouts" in raw else _compose.compose(raw, ROOT, campaign, category)
    return SPEC


def outroot(label):
    return os.path.join(ROOT, "generated", label) if label else os.path.join(ROOT, "generated")


def step1(runs=None, label=""):
    s = SPEC["step1_hero"]
    refs = [os.path.join(ROOT, p) for p in s["input_images"]]
    outdir = os.path.join(outroot(label), "step-1-hero")
    n = runs or s.get("runs", 1)
    jobs = [(f"hero_v{i}", s["prompt"], refs, s["size"], outdir) for i in range(1, n + 1)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda j: run_one(*j), jobs))


def step2(hero, only=None, label=""):
    """Fan out from the approved hero.

    Shots with "use_hero": false (the garment macros) are generated from the brand's
    product references alone — they carry no model identity, so feeding them the hero
    only risks pulling the print away from the source photography.
    """
    hero = hero if os.path.isabs(hero) else os.path.join(ROOT, hero)
    outdir = os.path.join(outroot(label), "step-2-fan-outs")
    jobs = []
    for fo in SPEC["step2_fanouts"]:
        if only and fo["id"] not in only:
            continue
        refs = [os.path.join(ROOT, p) for p in fo.get("extra_refs", [])]
        if fo.get("use_hero", True):
            refs = [hero] + refs
        if not refs:
            print(f"[SKIP] {fo['id']}: no reference images", flush=True)
            continue
        jobs.append((fo["id"], fo["prompt"], refs, fo["size"], outdir))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda j: run_one(*j), jobs))


def render(spec_path, campaign=None, category=None, out=None, qc=False):
    """Compose a product spec into a flat prompts.json and write it beside the spec.

    Composition is a build step: the rendered file is the artifact you read, diff,
    hand-edit and commit. Nobody should have to mentally join three files to work
    out what the model was actually told.
    """
    spec_path = os.path.abspath(spec_path)
    base = os.path.dirname(spec_path)
    spec = load_spec(spec_path, campaign, category)
    out = out or os.path.join(base, "prompts.rendered.json")
    with open(out, "w", encoding="utf-8") as f:
        f.write(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    print("[ OK ] rendered -> %s (%d shots, status: %s)"
          % (out, 1 + len(spec["step2_fanouts"]), spec.get("status", "unknown")))
    if qc:
        qc_path = os.path.splitext(out)[0] + ".qc.md"
        with open(qc_path, "w", encoding="utf-8") as f:
            f.write(_compose.qc_checklist(_compose.load_json(spec_path), base,
                                          campaign, category))
        print("[ OK ] checklist -> %s" % qc_path)
    return spec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["step1", "step2", "render"])
    ap.add_argument("--hero")
    ap.add_argument("--runs", type=int)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--spec", default="prompts.json",
                    help="product spec or flat prompts.json; paths resolve relative to it")
    ap.add_argument("--out", default="",
                    help="version label -> generated/<label>/ (render: output file path)")
    ap.add_argument("--campaign", help="override the product's campaign — re-shoot the "
                                       "whole set under a different look")
    ap.add_argument("--category", help="override the product's category")
    ap.add_argument("--qc", action="store_true",
                    help="render: also emit the per-shot QC checklist")
    a = ap.parse_args()

    if a.step == "render":
        render(a.spec, a.campaign, a.category, a.out or None, a.qc)
    else:
        load_spec(a.spec, a.campaign, a.category)
        if a.step == "step1":
            step1(a.runs, a.out)
        else:
            if not a.hero:
                ap.error("step2 needs --hero <path to chosen hero>")
            step2(a.hero, a.only, a.out)
