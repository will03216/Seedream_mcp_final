"""Unit tests for SeedreamClient — validation and payload building.

These tests do not hit the network; the HTTP layer is monkeypatched.
"""
from __future__ import annotations

import pytest

from seedream import SeedreamClient, ValidationError
from seedream import client as client_mod


@pytest.fixture
def client(monkeypatch):
    c = SeedreamClient(api_key="test-key")
    # Avoid credential resolution touching env/files.
    monkeypatch.setattr(c, "_api_key", lambda: "test-key")
    return c


def _fake_response(monkeypatch, capture):
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        capture["url"] = url
        capture["payload"] = payload
        return {"data": [{"url": "https://cdn.example.com/out.png"}], "usage": {"generated_images": 1}}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)


def test_text_to_image_builds_payload(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)

    result = client.generate("a red bicycle", size="2K")

    assert result.model == "seedream-4-5-251128"
    assert result.mode == "text-to-image"
    assert result.urls == ["https://cdn.example.com/out.png"]
    assert capture["url"].endswith("/images/generations")
    p = capture["payload"]
    assert p["prompt"] == "a red bicycle"
    assert p["size"] == "2K"
    assert p["model"] == "seedream-4-5-251128"
    assert "image" not in p


def test_model_alias_resolution(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-lite")
    assert capture["payload"]["model"] == "seedream-5-0-260128"


def test_45_rejects_1k(client):
    with pytest.raises(ValidationError):
        client.generate("x", model="4.5", size="1K")


def test_50lite_rejects_1k_and_adaptive(client):
    """Verified live: this model names '2k', '3k', '4k' as its only presets."""
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-lite", size="1K")
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-lite", size="adaptive")


def test_50lite_accepts_3k(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-lite", size="3K")
    assert capture["payload"]["size"] == "3K"


def test_pro_accepts_1_5k(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-pro", size="1.5K")
    assert capture["payload"]["size"] == "1.5K"


def test_explicit_wxh_size_accepted(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", size="2048x2048")
    assert capture["payload"]["size"] == "2048x2048"


def test_guidance_scale_range(client):
    with pytest.raises(ValidationError):
        client.generate("x", guidance_scale=25.0)


def test_reference_images_in_payload(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    result = client.generate("edit", image_urls=["https://a/1.png"])
    assert result.mode == "edit/reference"
    assert capture["payload"]["image"] == ["https://a/1.png"]
    assert capture["payload"]["sequential_image_generation"] == "disabled"


def test_sequential_options(client, monkeypatch):
    """The cap field is max_images, and the enable value is "auto".

    Verified live: {"n": 2} is dropped silently — a six-image prompt returned and
    billed six images — while {"max_images": 2} returned two.
    """
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("panels", sequential=True, num_images=4)
    p = capture["payload"]
    assert p["sequential_image_generation"] == "auto"
    assert p["sequential_image_generation_options"] == {"max_images": 4}


def test_sequential_caps_even_at_one_image(client, monkeypatch):
    """num_images=1 must still cap; previously no cap was sent below 2."""
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("panels", sequential=True, num_images=1)
    assert capture["payload"]["sequential_image_generation_options"] == {"max_images": 1}


def test_optimize_prompt_sends_mode(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="4.5", optimize_prompt=True)
    assert capture["payload"]["optimize_prompt_options"] == {"mode": "standard"}


def test_optimize_prompt_fast_is_pro_only(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-pro", image_urls=["u"],
                    optimize_prompt=True, optimize_prompt_mode="fast")
    assert capture["payload"]["optimize_prompt_options"] == {"mode": "fast"}
    with pytest.raises(ValidationError):
        client.generate("x", model="4.5", optimize_prompt=True, optimize_prompt_mode="fast")


def test_api_error_object_is_raised(client, monkeypatch):
    """A 200 body can still carry a top-level error object."""
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": [], "error": {"code": "OutputImageSensitiveContentDetected",
                                      "message": "blocked by content filter"}}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)
    with pytest.raises(client_mod.APIError, match="blocked by content filter"):
        client.generate("x")


def test_per_image_errors_surface(client, monkeypatch):
    """In a batch an individual image can fail while siblings succeed."""
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": [{"error": {"code": "Filtered", "message": "image 1 rejected"}}]}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)
    with pytest.raises(ValidationError, match="image 1 rejected"):
        client.generate("x")


def test_reference_plus_sequential_budget(client):
    with pytest.raises(ValidationError):
        client.generate("x", image_urls=["u"] * 13, sequential=True, num_images=5)


def test_pro_alias_resolution(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-pro", image_urls=["https://a/1.png"])
    assert capture["payload"]["model"] == "dola-seedream-5-0-pro-260628"
    # Pro rejects the batch key outright, even set to "disabled".
    assert "sequential_image_generation" not in capture["payload"]


def test_pro_rejects_4k(client):
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-pro", size="4K")


def test_pro_rejects_sequential_and_guidance(client):
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-pro", sequential=True, num_images=3)
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-pro", guidance_scale=5.0)


def test_pro_caps_references_at_ten(client):
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-pro", image_urls=[f"https://a/{i}.png" for i in range(11)])


def test_layer_decomposition_payload(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)

    result = client.generate(
        "Split the content in the image into two layers, including one text group: "
        "<bbox>179 58 809 197</bbox>; and one parrot: <bbox>330 274 641 991</bbox>",
        model="5.0-pro",
        size="2K",
        image_urls=["https://a/parrot.png"],
        output_format="jpeg",
        layer_decomposition=True,
    )

    p = capture["payload"]
    assert p["layer_decomposition"] is True
    assert p["output_format"] == "jpeg"
    assert p["image"] == ["https://a/parrot.png"]
    assert result.mode == "layer-decomposition"


def test_layer_decomposition_off_by_default(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-pro", image_urls=["https://a/1.png"])
    assert "layer_decomposition" not in capture["payload"]
    assert "output_format" not in capture["payload"]


def test_layer_decomposition_needs_an_input_image(client):
    with pytest.raises(ValidationError):
        client.generate("split into layers", model="5.0-pro", layer_decomposition=True)


def test_layer_decomposition_rejected_on_other_models(client):
    with pytest.raises(ValidationError):
        client.generate(
            "split into layers", model="4.5",
            image_urls=["https://a/1.png"], layer_decomposition=True,
        )


def test_layer_decomposition_returns_one_image_per_layer(client, monkeypatch):
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": [{"url": f"https://cdn.example.com/layer{i}.png"} for i in range(3)]}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)

    result = client.generate(
        "split into three layers", model="5.0-pro",
        image_urls=["https://a/1.png"], layer_decomposition=True,
    )
    assert len(result.images) == 3
    assert result.urls[0].endswith("layer0.png")


def test_layer_metadata_is_surfaced(client, monkeypatch):
    """Shape taken from a real 5.0 Pro layer_decomposition response.

    Note the API returns layers OUT of z_index order, hence GenerateResult.layers
    sorting rather than trusting response order.
    """
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": [
            {"url": "https://cdn/base.jpeg", "size": "2048x2048",
             "output_format": "jpeg", "z_index": 0},
            {"url": "https://cdn/layer_2.png", "size": "2454x319",
             "output_format": "png", "z_index": 2, "name": "WILD BEAUTY title text",
             "description": "Extract the yellow large serif title",
             "bounding_box": {"absolute": [363, 1481, 1686, 1653],
                              "normalized": [177, 723, 823, 807]}},
            {"url": "https://cdn/layer_1.png", "size": "850x2064",
             "output_format": "png", "z_index": 1, "name": "Scarlet macaw parrot",
             "description": "Extract the full body of the macaw",
             "bounding_box": {"absolute": [731, 626, 1301, 2010],
                              "normalized": [357, 306, 635, 981]}},
        ]}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)

    r = client.generate("split", model="5.0-pro", image_urls=["https://a/1.png"],
                        layer_decomposition=True)

    assert len(r.images) == 3
    assert r.base_image is not None and r.base_image.z_index == 0
    assert r.base_image.output_format == "jpeg"

    # Sorted by z_index, base excluded — the response listed layer 2 first.
    assert [layer.z_index for layer in r.layers] == [1, 2]
    assert [layer.name for layer in r.layers] == ["Scarlet macaw parrot", "WILD BEAUTY title text"]
    assert r.layers[0].bounding_box["normalized"] == [357, 306, 635, 981]
    assert r.layers[0].to_dict()["z_index"] == 1
    assert r.base_image.to_dict()["z_index"] == 0     # 0 must survive to_dict


def test_layer_downloads_named_by_z_index(client, monkeypatch, tmp_path):
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": [
            {"url": "https://cdn/base.jpeg", "output_format": "jpeg", "z_index": 0},
            {"url": "https://cdn/layer_1.png", "output_format": "png", "z_index": 1},
        ]}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)
    monkeypatch.setattr(client_mod.SeedreamClient, "_download",
                        staticmethod(lambda url, dest: dest.write_bytes(b"x")))

    r = client.generate_and_download(
        "split", str(tmp_path), model="5.0-pro", image_urls=["https://a/1.png"],
        output_format="jpeg", layer_decomposition=True,
    )

    names = sorted(p.name for p in tmp_path.iterdir())
    # Layers stay .png despite output_format=jpeg — they carry alpha.
    assert names == ["seedream-base.jpg", "seedream-layer1.png"]
    assert r.images[1].local_path.endswith("seedream-layer1.png")


def test_output_format_validated(client):
    with pytest.raises(ValidationError):
        client.generate("x", model="5.0-pro", output_format="webp")


def test_output_format_rejected_on_45(client):
    with pytest.raises(ValidationError):
        client.generate("x", model="4.5", output_format="png")


def test_empty_prompt_rejected(client):
    with pytest.raises(ValidationError):
        client.generate("   ")


def test_no_images_returned_raises(client, monkeypatch):
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": []}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)
    with pytest.raises(ValidationError):
        client.generate("x")
