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


def test_50lite_accepts_1k(client, monkeypatch):
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("x", model="5.0-lite", size="1K")
    assert capture["payload"]["size"] == "1K"


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
    capture: dict = {}
    _fake_response(monkeypatch, capture)
    client.generate("panels", sequential=True, num_images=4)
    p = capture["payload"]
    assert p["sequential_image_generation"] == "enabled"
    assert p["sequential_image_generation_options"] == {"n": 4}


def test_reference_plus_sequential_budget(client):
    with pytest.raises(ValidationError):
        client.generate("x", image_urls=["u"] * 13, sequential=True, num_images=5)


def test_empty_prompt_rejected(client):
    with pytest.raises(ValidationError):
        client.generate("   ")


def test_no_images_returned_raises(client, monkeypatch):
    def fake_request(url, *, method, headers, payload, timeout, correlation_id=""):
        return {"data": []}
    monkeypatch.setattr(client_mod, "request_with_retry", fake_request)
    with pytest.raises(ValidationError):
        client.generate("x")
