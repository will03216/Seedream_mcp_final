#!/usr/bin/env python3
"""Generate 5 images each for two infographic prompts via Seedream 5.0 Pro."""
import json, os, sys, urllib.request, concurrent.futures

API_KEY = os.environ["ARK_API_KEY"]
MODEL = "dola-seedream-5-0-pro-260628"
URL = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated", "cse_infographics_v4")
os.makedirs(OUT, exist_ok=True)

_IMAGE1_OLD = (
    "Flat 2D vector infographic, pure white background, three evenly spaced horizontal "
    "rows in a clean column grid. "
    "Left column, each row: a large icon with a bold name caption directly beneath it "
    "and a smaller color-legend line under that. Middle column: a bold black "
    "right-pointing arrow. Right column: a bold headline with a lighter descriptive "
    "sentence beneath it. "
    "Row 1: green megaphone icon, caption \"Megaphone\", legend \"Green: Opportunity\", "
    "arrow, headline \"Better communication channels.\", subtext \"Enhance internal and "
    "external messaging flow.\" "
    "Row 2: a red-and-green checklist form icon, caption \"Form\", legend \"Red + Green: "
    "Capability + Opportunity\", arrow, headline \"Simpler enrollment.\", subtext "
    "\"Streamline the signup process for easy participation.\" "
    "Row 3: a cluster of small yellow thought/speech bubbles, caption \"Thought "
    "bubbles\", legend \"Yellow: Motivation\", arrow, headline \"Address fear and "
    "beliefs.\", subtext \"Understand psychological barriers and boost confidence.\" "
    "Consistent icon size and line weight, clean modern sans-serif, rows aligned on a "
    "shared grid, generous white space, minimalist corporate infographic style."
)

IMAGE1 = _IMAGE1_OLD

IMAGE2 = (
    "Flat 2D vector infographic, monochrome green on white, bold modern style, digital/"
    "glitch accents. At the top, a full-width dashed green arrow header labeled \"CHANNEL "
    "INPUT\" pointing right toward a row of green human pictograms. "
    "Below it, six parallel horizontal lanes, each a single thick green arrow flowing "
    "left to right into its own row of 4-5 green human pictogram figures on the right, "
    "forming a clean aligned grid. "
    "In the middle-left, five channel icons drawn as OUTLINE line-art inside rounded-"
    "square badges with a green border and white fill, in one neat horizontal row, each "
    "labeled beneath: \"TV\", \"RADIO\", \"LETTER\", \"POSTER\", \"SMS\". At the "
    "bottom-left, a separate rounded-square badge cluster labeled \"SOCIAL MEDIA\" using a "
    "generic heart and share glyph (no real brand logos). "
    "Top two lane arrows are intact and reach their people. The lower lane arrows are "
    "violently shattered mid-flight with jagged lightning-bolt breaks and fragment "
    "shards, stopping short; the pictograms in those broken lanes have a \"?\" confusion "
    "mark above their heads. Scatter small green dash and fragment accents along the left "
    "and right edges for a digital texture. Two-tone green: dark-green outlines, medium-"
    "green fills. Generous white space."
)

# Only regenerate image 2 this round.
JOBS = [("image2", IMAGE2, "2K")]


def generate(prompt, size):
    body = {"model": MODEL, "prompt": prompt, "size": size, "watermark": False}
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def one(job, i):
    name, prompt, size = job
    try:
        resp = generate(prompt, size)
        url = resp["data"][0]["url"]
        fn = os.path.join(OUT, f"{name}_v{i}.jpeg")
        urllib.request.urlretrieve(url, fn)
        print(f"[OK] {name}_v{i} -> {fn}", flush=True)
        return fn
    except Exception as e:
        print(f"[ERR] {name}_v{i}: {e}", flush=True)
        return None


tasks = [(job, i) for job in JOBS for i in range(1, 6)]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    list(ex.map(lambda t: one(*t), tasks))
print("DONE ->", OUT)
