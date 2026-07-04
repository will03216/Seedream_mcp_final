"""Tests for the model registry and alias resolution."""
from __future__ import annotations

from seedream.config import (
    DEFAULT_MODEL,
    MODELS,
    model_caps,
    resolve_model,
)


def test_default_model_is_registered():
    assert DEFAULT_MODEL in MODELS


def test_both_models_present():
    assert "seedream-4-5-251128" in MODELS
    assert "seedream-5-0-260128" in MODELS


def test_resolve_aliases():
    assert resolve_model("4.5") == "seedream-4-5-251128"
    assert resolve_model("5.0-lite") == "seedream-5-0-260128"
    assert resolve_model("lite") == "seedream-5-0-260128"
    # Passthrough of a canonical ID.
    assert resolve_model("seedream-4-5-251128") == "seedream-4-5-251128"
    # Empty → default.
    assert resolve_model("") == DEFAULT_MODEL


def test_45_sizes_exclude_1k():
    assert "1K" not in model_caps("seedream-4-5-251128")["sizes"]


def test_50lite_sizes_include_1k():
    assert "1K" in model_caps("seedream-5-0-260128")["sizes"]
