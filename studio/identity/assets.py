"""Load and validate a Character Bible without invoking any AI model."""
from __future__ import annotations

import json
from pathlib import Path

from identity.models import CharacterAsset, ReferenceImage

REFERENCE_VIEWS = ("front", "45_degree", "side", "back", "full_body")
_ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".safetensors", ".pt", ".bin", ".npy"}


class CharacterBibleError(ValueError):
    pass


def _files(directory: Path) -> tuple[Path, ...]:
    if not directory.is_dir():
        return ()
    return tuple(
        sorted(
            (path.resolve() for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in _ASSET_EXTENSIONS),
            key=lambda path: path.as_posix().lower(),
        )
    )


def load_character_asset(root: Path) -> CharacterAsset:
    """Return the canonical asset set represented by ``root``.

    The loader is deterministic and read-only. It rejects an absent or
    malformed description instead of reconstructing identity from a scene
    prompt, preserving the Character Bible as the source of truth.
    """

    root = Path(root).resolve()
    description_path = root / "description.json"
    if not description_path.is_file():
        raise CharacterBibleError(f"Missing Character Bible description: {description_path}")

    try:
        description = json.loads(description_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CharacterBibleError(f"Invalid Character Bible description: {description_path}: {exc}") from exc
    if not isinstance(description, dict):
        raise CharacterBibleError("Character Bible description.json must contain a JSON object")

    character_id = description.get("character_id")
    if not isinstance(character_id, str) or not character_id.strip():
        raise CharacterBibleError("Character Bible description.json requires a non-empty character_id")

    references: list[ReferenceImage] = []
    references_root = root / "reference_images"
    for view in REFERENCE_VIEWS:
        references.extend(ReferenceImage(path=path, view=view) for path in _files(references_root / view))

    return CharacterAsset(
        character_id=character_id.strip(),
        root=root,
        description=description,
        reference_images=tuple(references),
        clothing=_files(root / "clothing"),
        accessories=_files(root / "accessories"),
        embeddings=_files(root / "embeddings"),
        bible_version=str(description.get("schema_version", "1")),
    )
