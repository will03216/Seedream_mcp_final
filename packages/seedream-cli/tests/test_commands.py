"""Smoke tests for the Seedream CLI wiring (no network)."""
from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from seedream import GenerateResult, ImageResult
from seedream_cli.main import app

runner = CliRunner()


def test_help_lists_command_groups():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for grp in ("auth", "generate", "tos", "models", "ping", "skill"):
        assert grp in result.output


def test_models_command():
    fake = {
        "default_model": "seedream-4-5-251128",
        "models": [
            {"model_id": "seedream-4-5-251128", "label": "Seedream 4.5", "alias": "4.5",
             "sizes": ["2K", "4K"], "default_size": "2K", "features": {"seed": True}},
        ],
    }
    with patch("seedream_cli.commands.models.SeedreamClient") as mk:
        mk.return_value.list_models.return_value = fake
        result = runner.invoke(app, ["models"])
    assert result.exit_code == 0
    assert "seedream-4-5-251128" in result.output


def test_generate_text_to_image():
    fake = GenerateResult(
        model="seedream-4-5-251128",
        images=[ImageResult(url="https://cdn/out.png", size="2K")],
        mode="text-to-image",
    )
    with patch("seedream_cli.commands.generate.SeedreamClient") as mk:
        mk.return_value.generate.return_value = fake
        result = runner.invoke(app, ["generate", "-p", "a cat"])
    assert result.exit_code == 0
    assert "https://cdn/out.png" in result.output


def test_generate_layer_decomposition_flag():
    fake = GenerateResult(
        model="dola-seedream-5-0-pro-260628",
        images=[ImageResult(url=f"https://cdn/layer{i}.png") for i in range(2)],
        mode="layer-decomposition",
    )
    with patch("seedream_cli.commands.generate.SeedreamClient") as mk:
        mk.return_value.generate.return_value = fake
        result = runner.invoke(app, [
            "generate", "-p", "split into two layers", "-m", "5.0-pro",
            "-r", "https://cdn/src.png", "--layer-decomposition", "--output-format", "png",
        ])
    assert result.exit_code == 0
    kwargs = mk.return_value.generate.call_args.kwargs
    assert kwargs["layer_decomposition"] is True
    assert kwargs["output_format"] == "png"
    assert "https://cdn/layer0.png" in result.output
