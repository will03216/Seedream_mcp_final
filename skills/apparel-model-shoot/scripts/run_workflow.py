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

ROOT = os.getcwd()   # overridden by --spec: paths resolve relative to the spec file
URL = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"


def api_key():
    key = os.environ.get("ARK_API_KEY")
    if key:
        return key
    cfg = configparser.ConfigParser()
    cfg.read(os.path.expanduser("~/.seedream/credentials"))
    return cfg["default"]["ark_api_key"]


API_KEY = api_key()


def to_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def generate(prompt, images, size):
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
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
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


def load_spec(spec_path):
    """Load prompts.json. All image paths in it resolve relative to its directory."""
    global SPEC, ROOT
    spec_path = os.path.abspath(spec_path)
    ROOT = os.path.dirname(spec_path)
    with open(spec_path) as f:
        SPEC = json.load(f)


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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["step1", "step2"])
    ap.add_argument("--hero")
    ap.add_argument("--runs", type=int)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--spec", default="prompts.json",
                    help="prompt spec file; image paths resolve relative to it")
    ap.add_argument("--out", default="",
                    help="version label -> generated/<label>/ instead of generated/")
    a = ap.parse_args()
    load_spec(a.spec)
    if a.step == "step1":
        step1(a.runs, a.out)
    else:
        if not a.hero:
            ap.error("step2 needs --hero <path to chosen hero>")
        step2(a.hero, a.only, a.out)
