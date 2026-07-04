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


def test_list_models():
    out = server.seedream_list_models()
    ids = {m["model_id"] for m in out["models"]}
    assert "seedream-4-5-251128" in ids
    assert "seedream-5-0-260128" in ids
