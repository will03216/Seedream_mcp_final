#!/usr/bin/env python3
"""Run walmart/prompts.json scenarios against Seedream 5.0 Pro (exact prompts)."""
import base64, json, mimetypes, os, sys, urllib.request, time

WALMART = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WALMART, "output")
os.makedirs(OUT, exist_ok=True)

API_KEY = os.environ["ARK_API_KEY"]
MODEL = "dola-seedream-5-0-pro-260628"
URL = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"


def to_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def generate(prompt, images):
    body = {
        "model": MODEL,
        "prompt": prompt,
        "size": "2K",
        "watermark": False,
    }
    if len(images) == 1:
        body["image"] = to_data_uri(images[0])
    elif images:
        body["image"] = [to_data_uri(p) for p in images]

    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def main():
    with open(os.path.join(WALMART, "prompts.json")) as f:
        examples = json.load(f)["examples"]

    manifest = []
    for ex in examples:
        sid = ex["scenario_id"]
        imgs = [os.path.join(WALMART, p) for p in ex.get("input_images", [])]
        missing = [p for p in imgs if not os.path.exists(p)]
        if missing:
            print(f"[SKIP] {sid}: missing {missing}", flush=True)
            continue
        print(f"[RUN ] {sid} ({len(imgs)} refs)...", flush=True)
        try:
            resp = generate(ex["prompt"], imgs)
        except urllib.error.HTTPError as e:
            print(f"[FAIL] {sid}: HTTP {e.code} {e.read().decode()[:300]}", flush=True)
            continue
        except Exception as e:
            print(f"[FAIL] {sid}: {e}", flush=True)
            continue

        data = resp.get("data") or []
        if not data or not data[0].get("url"):
            print(f"[FAIL] {sid}: no image in response {json.dumps(resp)[:300]}", flush=True)
            continue

        url = data[0]["url"]
        outpath = os.path.join(OUT, f"{sid}.jpeg")
        with urllib.request.urlopen(url, timeout=120) as r, open(outpath, "wb") as out:
            out.write(r.read())
        size = data[0].get("size", "?")
        print(f"[ OK ] {sid} -> {outpath} ({size})", flush=True)
        manifest.append({"scenario_id": sid, "output": os.path.basename(outpath),
                         "size": size, "prompt": ex["prompt"], "input_images": ex.get("input_images", [])})

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nDone. {len(manifest)}/{len(examples)} generated. Manifest: {os.path.join(OUT,'manifest.json')}")


if __name__ == "__main__":
    main()
