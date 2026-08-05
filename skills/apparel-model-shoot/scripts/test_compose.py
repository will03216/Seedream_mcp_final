#!/usr/bin/env python3
"""Offline test suite. Stdlib unittest, no network, no credentials.

    python3 scripts/test_compose.py

The golden byte-diff (GoldenTop) is the load-bearing test. The eight shipped tee
prompts are production ground truth — validated across three full generation
rounds — so if composition cannot reproduce them exactly, the abstraction has
lost something. Everything else here is structural.
"""
import json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import compose  # noqa: E402

CAMPAIGN_DIR = os.path.join(SKILL, "templates", "campaigns")
CATEGORY_DIR = os.path.join(SKILL, "templates", "categories")
EXAMPLE = os.path.join(SKILL, "examples", "summer-daze-tee")

MIN_PX, MAX_PX = 921_600, 4_194_304


def categories():
    return sorted(f[:-5] for f in os.listdir(CATEGORY_DIR) if f.endswith(".json"))


def campaigns():
    return sorted(f[:-5] for f in os.listdir(CAMPAIGN_DIR) if f.endswith(".json"))


def compose_example(campaign=None, category=None, refs=None):
    product = compose.load_json(os.path.join(EXAMPLE, "product.json"))
    if refs is not None:
        product["refs"] = refs
    return compose.compose(product, EXAMPLE, campaign, category)


class GoldenTop(unittest.TestCase):
    """The abstraction must be lossless against the committed flat spec."""

    def setUp(self):
        self.got = compose_example()
        self.want = compose.load_json(os.path.join(HERE, "prompts.example.json"))

    def flat(self, spec):
        return {s["id"]: s for s in [spec["step1_hero"]] + spec["step2_fanouts"]}

    def test_prompts_are_byte_identical(self):
        """Every shipped shot must still render exactly. The category may ADD shots
        (the back-print macro was added after these were validated) but may never
        alter or drop one — those eight prompts are the production ground truth."""
        got, want = self.flat(self.got), self.flat(self.want)
        missing = sorted(set(want) - set(got))
        self.assertEqual(missing, [], "shipped shots dropped: %s" % missing)
        for sid in want:
            self.assertEqual(got[sid]["prompt"], want[sid]["prompt"],
                             "prompt drifted for %s" % sid)

    def test_sizes_and_hero_flags_match(self):
        got, want = self.flat(self.got), self.flat(self.want)
        for sid in want:
            self.assertEqual(got[sid]["size"], want[sid]["size"], sid)
            self.assertEqual(got[sid].get("use_hero", True),
                             want[sid].get("use_hero", True), sid)

    def test_ref_paths_and_order_match(self):
        got, want = self.flat(self.got), self.flat(self.want)
        for sid in want:
            key = "input_images" if sid == "hero" else "extra_refs"
            self.assertEqual([os.path.basename(p) for p in got[sid].get(key, [])],
                             [os.path.basename(p) for p in want[sid].get(key, [])],
                             "ref order drifted for %s — 'Image N is...' would desync" % sid)


class AllCategories(unittest.TestCase):
    """Every category must compose cleanly against every campaign."""

    def test_compose_without_error(self):
        for cat in categories():
            for camp in campaigns():
                with self.subTest(category=cat, campaign=camp):
                    compose_example(campaign=camp, category=cat)

    def test_no_placeholder_survives(self):
        for cat in categories():
            for camp in campaigns():
                spec = compose_example(campaign=camp, category=cat)
                for shot in [spec["step1_hero"]] + spec["step2_fanouts"]:
                    with self.subTest(category=cat, campaign=camp, shot=shot["id"]):
                        self.assertNotIn("{{", shot["prompt"])

    def test_sizes_legal_for_seedream_pro(self):
        for cat in categories():
            spec = compose_example(category=cat)
            for shot in [spec["step1_hero"]] + spec["step2_fanouts"]:
                w, h = (int(x) for x in shot["size"].split("x"))
                with self.subTest(category=cat, shot=shot["id"]):
                    self.assertEqual(w % 16, 0, "width not a multiple of 16")
                    self.assertEqual(h % 16, 0, "height not a multiple of 16")
                    self.assertGreaterEqual(w * h, MIN_PX)
                    self.assertLessEqual(w * h, MAX_PX)

    def test_ref_roles_are_declared(self):
        for cat in categories():
            spec = compose.load_json(os.path.join(CATEGORY_DIR, cat + ".json"))
            known = set(spec.get("required_ref_roles", [])) | set(spec.get("optional_ref_roles", []))
            shots = [spec["hero"]] + spec.get("fanouts", [])
            for shot in shots:
                for role in shot.get("ref_roles", []):
                    with self.subTest(category=cat, shot=shot["id"], role=role):
                        self.assertIn(role, known, "undeclared ref role")

    def test_ref_sentence_numbering_matches_actual_refs(self):
        """The generated 'Image N is...' must match the real list after hero-prepend."""
        for cat in categories():
            spec = compose_example(category=cat)
            for shot in spec["step2_fanouts"]:
                n_refs = len(shot.get("extra_refs", []))
                expected = n_refs + (0 if shot.get("use_hero") is False else 1)
                mentioned = shot["prompt"].count("Image %d is")
                claimed = sum(1 for i in range(1, 12)
                              if ("Image %d is" % i) in shot["prompt"])
                with self.subTest(category=cat, shot=shot["id"]):
                    if claimed:
                        self.assertEqual(claimed, expected,
                                         "prompt names %d images but %d refs are sent"
                                         % (claimed, expected))
                    self.assertLessEqual(expected, 10, "exceeds Seedream Pro ref cap")

    def test_flatlay_shots_negate_human_presence(self):
        for cat in categories():
            spec = compose_example(category=cat)
            for shot in spec["step2_fanouts"]:
                if shot.get("use_hero") is False:
                    with self.subTest(category=cat, shot=shot["id"]):
                        self.assertIn("NO human presence", shot["prompt"],
                                      "a product macro without an explicit human "
                                      "negation will be given a body by default")

    def test_every_category_declares_a_hero_kind(self):
        for cat in categories():
            spec = compose.load_json(os.path.join(CATEGORY_DIR, cat + ".json"))
            with self.subTest(category=cat):
                self.assertIn(spec.get("hero_kind"),
                              ("on-model-full-body", "on-body-crop"))
                self.assertIn(spec.get("status"),
                              ("validated", "smoke-tested", "draft"))


class OptionalShotGating(unittest.TestCase):
    def test_optional_shot_dropped_when_ref_absent(self):
        for cat in categories():
            spec = compose.load_json(os.path.join(CATEGORY_DIR, cat + ".json"))
            optional = [s for s in spec.get("fanouts", []) if s.get("optional")]
            if not optional:
                continue
            needed = set()
            for s in optional:
                needed |= set(s.get("requires_ref_roles", []))
            all_roles = (set(spec.get("required_ref_roles", []))
                         | set(spec.get("optional_ref_roles", [])))
            # keep every role except those the optional shots depend on
            refs = {r: "x.png" for r in all_roles if r not in needed}
            # any non-optional shot needing a dropped role would (correctly) error
            blocked = any(not s.get("optional")
                          and needed & set(s.get("ref_roles", []))
                          for s in spec.get("fanouts", []))
            if blocked:
                continue
            got = compose_example(category=cat, refs=refs)
            ids = {s["id"] for s in got["step2_fanouts"]}
            for s in optional:
                with self.subTest(category=cat, shot=s["id"]):
                    self.assertNotIn(s["id"], ids,
                                     "optional shot survived without its ref — it "
                                     "would hallucinate the detail it exists to show")


class RefGating(unittest.TestCase):
    def test_required_shot_with_absent_ref_errors_loudly(self):
        """A shot naming an absent ref would ship 'MUST PRESERVE from Image 2'
        with no Image 2 attached."""
        product = compose.load_json(os.path.join(EXAMPLE, "product.json"))
        product["refs"] = {k: v for k, v in product["refs"].items() if k != "back"}
        with self.assertRaises(compose.CompositionError) as ctx:
            compose.compose(product, EXAMPLE)
        msg = str(ctx.exception)
        self.assertIn("fanout-6-backview", msg)
        self.assertIn("'back'", msg)
        self.assertIn("mark the shot optional", msg)


class Failures(unittest.TestCase):
    def test_missing_required_ref_raises(self):
        with self.assertRaises(compose.CompositionError):
            compose_example(refs={})

    def test_unresolved_placeholder_raises(self):
        product = compose.load_json(os.path.join(EXAMPLE, "product.json"))
        del product["product"]["artwork_front"]
        with self.assertRaises(compose.CompositionError) as ctx:
            compose.compose(product, EXAMPLE)
        self.assertIn("artwork_front", str(ctx.exception))

    def test_errors_are_reported_together(self):
        product = compose.load_json(os.path.join(EXAMPLE, "product.json"))
        del product["product"]["artwork_front"]
        del product["product"]["garment"]
        with self.assertRaises(compose.CompositionError) as ctx:
            compose.compose(product, EXAMPLE)
        self.assertIn("artwork_front", str(ctx.exception))
        self.assertIn("garment", str(ctx.exception))


class Wardrobe(unittest.TestCase):
    def test_product_slot_excluded_from_styling(self):
        w = {"top": "a tee", "bottom": "jeans", "footwear": "sneakers"}
        self.assertEqual(compose.build_wardrobe(w, "top", ["bottom", "footwear"], []),
                         "jeans and sneakers")
        self.assertEqual(compose.build_wardrobe(w, "bottom", ["top", "footwear"], []),
                         "a tee and sneakers")

    def test_nulls_filtered_not_rendered_as_gaps(self):
        w = {"top": "a tee", "bottom": None, "footwear": "sneakers"}
        self.assertEqual(compose.build_wardrobe(w, "outer", ["top", "bottom", "footwear"], []),
                         "a tee and sneakers")

    def test_suppressed_slots_dropped(self):
        w = {"top": "a tee", "bottom": "jeans", "footwear": "sneakers"}
        self.assertEqual(
            compose.build_wardrobe(w, "dress", ["top", "bottom", "footwear"], ["top", "bottom"]),
            "sneakers")

    def test_oxford_comma(self):
        self.assertEqual(compose.oxford(["a"]), "a")
        self.assertEqual(compose.oxford(["a", "b"]), "a and b")
        self.assertEqual(compose.oxford(["a", "b", "c"]), "a, b and c")


class BackwardCompatibility(unittest.TestCase):
    def test_flat_spec_passes_through_unmodified(self):
        import run_workflow
        flat_path = os.path.join(HERE, "prompts.example.json")
        raw = compose.load_json(flat_path)
        got = run_workflow.load_spec(flat_path)
        self.assertEqual(got, raw, "a committed flat spec must be used verbatim")

    def test_import_without_credentials(self):
        saved = os.environ.pop("ARK_API_KEY", None)
        try:
            import importlib, run_workflow
            importlib.reload(run_workflow)
        finally:
            if saved is not None:
                os.environ["ARK_API_KEY"] = saved


if __name__ == "__main__":
    unittest.main(verbosity=2)
