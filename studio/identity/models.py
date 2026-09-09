"""Stable data contracts shared by character bibles and identity providers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ReferenceImage:
    path: Path
    view: str


@dataclass(frozen=True)
class CharacterAsset:
    """A validated, immutable view of one on-disk Character Bible."""

    character_id: str
    root: Path
    description: Mapping[str, Any]
    reference_images: tuple[ReferenceImage, ...] = ()
    clothing: tuple[Path, ...] = ()
    accessories: tuple[Path, ...] = ()
    embeddings: tuple[Path, ...] = ()
    bible_version: str = "1"


@dataclass(frozen=True)
class IdentityEncoding:
    """Opaque output of ``encode_character`` owned by one provider."""

    character_id: str
    provider: str
    method: str
    payload: Any
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IdentityApplication:
    """Prompt plus provider-specific controls ready for generation."""

    prompt: str
    controls: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
