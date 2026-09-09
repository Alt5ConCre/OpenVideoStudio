from __future__ import annotations

import json

import pytest

from identity import CharacterBibleError, load_character_asset
from providers.base import IdentityProvider
from providers.identity_text import TextIdentityProvider
from providers.identity_image import ImageReferenceIdentityProvider
from providers.registry import get_provider


def _write_bible(root, description=None):
    root.mkdir()
    (root / "description.json").write_text(
        json.dumps(description or {
            "schema_version": "1",
            "character_id": "char_1",
            "name_or_role": "Mara",
            "approx_age": "early 30s",
            "wardrobe": "rust-red flight jacket",
        }),
        encoding="utf-8",
    )
    return root


def test_character_bible_loader_collects_assets_by_role(tmp_path):
    root = _write_bible(tmp_path / "char_1")
    for directory, filename in (
        ("reference_images/front", "front.png"),
        ("reference_images/side", "side.webp"),
        ("clothing", "jacket.jpg"),
        ("accessories", "compass.png"),
        ("embeddings", "provider-a.safetensors"),
    ):
        target = root / directory
        target.mkdir(parents=True)
        (target / filename).write_bytes(b"fixture")

    asset = load_character_asset(root)

    assert asset.character_id == "char_1"
    assert [reference.view for reference in asset.reference_images] == ["front", "side"]
    assert [path.name for path in asset.clothing] == ["jacket.jpg"]
    assert [path.name for path in asset.accessories] == ["compass.png"]
    assert [path.name for path in asset.embeddings] == ["provider-a.safetensors"]


def test_character_bible_requires_description_and_character_id(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(CharacterBibleError, match="Missing"):
        load_character_asset(empty)

    root = _write_bible(tmp_path / "bad", {"name_or_role": "anonymous"})
    with pytest.raises(CharacterBibleError, match="character_id"):
        load_character_asset(root)


def test_text_provider_implements_protocol_and_applies_canonical_identity(tmp_path):
    asset = load_character_asset(_write_bible(tmp_path / "char_1"))
    provider = get_provider("identity", "text")

    assert isinstance(provider, IdentityProvider)
    identity = provider.encode_character(asset)
    request = provider.apply_identity("walking through rain", identity)

    assert identity.character_id == "char_1"
    assert identity.method == "canonical_text"
    assert request.prompt.startswith("Mara, early 30s, rust-red flight jacket")
    assert request.prompt.endswith("walking through rain")
    assert request.metadata["character_id"] == "char_1"


def test_text_provider_rejects_another_providers_encoding(tmp_path):
    asset = load_character_asset(_write_bible(tmp_path / "char_1"))
    provider = TextIdentityProvider()
    identity = provider.encode_character(asset)
    foreign = type(identity)(
        character_id=identity.character_id,
        provider="other",
        method=identity.method,
        payload=identity.payload,
    )

    with pytest.raises(ValueError, match="belongs to provider"):
        provider.apply_identity("prompt", foreign)


def _write_bible_with_reference_images(root):
    root = _write_bible(root)
    for view, filename in (("front", "front.png"), ("side", "side.png")):
        target = root / "reference_images" / view
        target.mkdir(parents=True)
        (target / filename).write_bytes(b"fixture")
    return root


def test_image_reference_provider_implements_protocol_and_uses_first_reference(tmp_path):
    asset = load_character_asset(_write_bible_with_reference_images(tmp_path / "char_1"))
    provider = get_provider("identity", "image_reference")

    assert isinstance(provider, IdentityProvider)
    identity = provider.encode_character(asset)
    request = provider.apply_identity("walking through rain", identity)

    assert identity.provider == "image_reference"
    assert identity.payload == asset.reference_images[0].path
    assert identity.payload.name == "front.png"
    assert request.prompt == "walking through rain"  # unchanged -- conditioning is image-only
    assert request.controls["reference_image_path"] == asset.reference_images[0].path
    assert request.metadata["character_id"] == "char_1"


def test_image_reference_provider_requires_at_least_one_reference_image(tmp_path):
    asset = load_character_asset(_write_bible(tmp_path / "char_1"))
    provider = ImageReferenceIdentityProvider()

    with pytest.raises(ValueError, match="no reference_images"):
        provider.encode_character(asset)


def test_image_reference_provider_rejects_another_providers_encoding(tmp_path):
    asset = load_character_asset(_write_bible_with_reference_images(tmp_path / "char_1"))
    provider = ImageReferenceIdentityProvider()
    identity = provider.encode_character(asset)
    foreign = type(identity)(
        character_id=identity.character_id,
        provider="other",
        method=identity.method,
        payload=identity.payload,
    )

    with pytest.raises(ValueError, match="belongs to provider"):
        provider.apply_identity("prompt", foreign)
