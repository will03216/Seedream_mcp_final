"""Typed result dataclasses returned by SeedreamClient methods."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImageResult:
    """A single generated image."""
    url: str | None = None
    b64_json: str | None = None
    size: str | None = None
    local_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.url:
            out["url"] = self.url
        if self.b64_json:
            out["b64_json"] = self.b64_json
        if self.size:
            out["size"] = self.size
        if self.local_path:
            out["local_path"] = self.local_path
        return out


@dataclass
class GenerateResult:
    """Result of a synchronous /images/generations call."""
    model: str
    images: list[ImageResult] = field(default_factory=list)
    mode: str = ""
    usage: dict | None = None
    raw: dict = field(default_factory=dict)

    @property
    def urls(self) -> list[str]:
        return [img.url for img in self.images if img.url]

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "model": self.model,
            "count": len(self.images),
            "images": [img.to_dict() for img in self.images],
        }
        if self.mode:
            out["mode"] = self.mode
        if self.usage:
            out["usage"] = self.usage
        return out


@dataclass
class TOSUploadResult:
    """Result of uploading a local file to a TOS bucket."""
    bucket: str
    key: str
    url: str
    region: str = ""
    size: int = 0
    content_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "bucket": self.bucket,
            "key": self.key,
            "url": self.url,
        }
        if self.region:
            out["region"] = self.region
        if self.size:
            out["size"] = self.size
        if self.content_type:
            out["content_type"] = self.content_type
        return out
