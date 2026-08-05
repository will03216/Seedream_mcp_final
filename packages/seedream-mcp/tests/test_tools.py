"""Tests for the Seedream MCP tool wrappers."""
from __future__ import annotations

from unittest.mock import patch

from seedream import GenerateResult, ImageResult
from seedream.exceptions import ValidationError
from seedream_mcp import server


def test_generate_success():
    fake = GenerateResult(
        model="seedream-4-5-251128",
        images=[ImageResult(url="https://cdn/out.png")],
        mode="text-to-image",
    )
    with patch.object(server, "_client") as mk:
        mk.return_value.generate.return_value = fake
        out = server.seedream_generate("a cat")
    assert out["model"] == "seedream-4-5-251128"
    assert out["count"] == 1
    assert out["images"][0]["url"] == "https://cdn/out.png"
    assert "message" in out


def test_generate_error_is_wrapped():
    with patch.object(server, "_client") as mk:
        mk.return_value.generate.side_effect = ValidationError("bad size")
        out = server.seedream_generate("x", size="1K", model="4.5")
    assert out["status"] == "error"
    assert "bad size" in out["error"]


def _layer_result() -> GenerateResult:
    return GenerateResult(
        model="dola-seedream-5-0-pro-260628",
        images=[
            ImageResult(url="https://cdn/base.jpeg", output_format="jpeg", z_index=0),
            ImageResult(url="https://cdn/layer_1.png", output_format="png", z_index=1,
                        name="Scarlet macaw parrot",
                        bounding_box={"normalized": [357, 306, 635, 981]}),
            ImageResult(url="https://cdn/layer_2.png", output_format="png", z_index=2,
                        name="WILD BEAUTY title text"),
        ],
        mode="layer-decomposition",
    )


def test_layer_decomposition_is_passed_through():
    with patch.object(server, "_client") as mk:
        mk.return_value.generate.return_value = _layer_result()
        out = server.seedream_generate(
            "split into two layers",
            model="5.0-pro",
            image_urls=["https://cdn/src.png"],
            output_format="png",
            layer_decomposition=True,
        )
    kwargs = mk.return_value.generate.call_args.kwargs
    assert kwargs["layer_decomposition"] is True
    assert kwargs["output_format"] == "png"
    assert out["count"] == 3                      # base image + 2 layers
    assert "2 layer(s) ready" in out["message"]
    # The metadata the caller needs to composite must survive to the tool result.
    assert out["images"][0]["z_index"] == 0
    assert out["images"][1]["name"] == "Scarlet macaw parrot"
    assert out["images"][1]["bounding_box"]["normalized"] == [357, 306, 635, 981]


def test_layer_decomposition_silently_not_applied_is_reported():
    """The API intermittently returns one flat image and no layers, with HTTP 200."""
    fake = GenerateResult(
        model="dola-seedream-5-0-pro-260628",
        images=[ImageResult(url="https://cdn/flat.jpeg", size="2048x2048")],
        mode="layer-decomposition",
    )
    with patch.object(server, "_client") as mk:
        mk.return_value.generate.return_value = fake
        out = server.seedream_generate(
            "split into two layers", model="5.0-pro",
            image_urls=["https://cdn/src.png"], layer_decomposition=True,
        )
    assert "did not apply" in out["message"]
    assert "retry" in out["message"]


def test_list_models():
    out = server.seedream_list_models()
    ids = {m["model_id"] for m in out["models"]}
    assert "seedream-4-5-251128" in ids
    assert "seedream-5-0-260128" in ids
    assert "dola-seedream-5-0-pro-260628" in ids

    pro = next(m for m in out["models"] if m["model_id"] == "dola-seedream-5-0-pro-260628")
    assert pro["features"]["layer_decomposition"] is True
    assert pro["max_reference_images"] == 10
