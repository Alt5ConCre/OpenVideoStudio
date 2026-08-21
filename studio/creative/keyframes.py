"""Stage 3: storyboard -> one generated image per scene, via ImageProvider.
Only runs after the storyboard review gate — enforced in creative/pipeline.py."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable, Optional

from providers.base import ImageProvider
from creative.identity import (
    format_character_identity, format_environment_identity, ANTI_TEXT_NEGATIVE_PROMPT,
)


def _composed_image_prompt(storyboard: dict, scene: dict) -> str:
    """V0.3: prepend the deterministically-formatted, code-generated identity
    text (creative/identity.py) ahead of this scene's own image_prompt, so
    every keyframe draws from byte-identical character/environment wording
    instead of relying on the LLM to reproduce visual_identity consistently
    per scene (that drift was V0.2's known face-identity weakness)."""
    parts = [
        format_character_identity(storyboard.get("character_identity")),
        format_environment_identity(storyboard.get("environment_identity")),
        scene["image_prompt"],
    ]
    # ". " (not a bare space) between the three components — each is
    # already comma-dense internally, so a bare-space join let clauses
    # collide at the boundary (e.g. "realistic crude, modular..."),
    # blurring where character identity ends and environment/scene begin.
    return ". ".join(p.strip() for p in parts if p and p.strip())


def _composed_negative_prompt(scene: dict) -> str:
    """Add the shared anti-text negative fragment unless this exact scene
    was flagged as needing readable in-image text (storyboard.py's
    allow_generated_text) — see identity.py's ANTI_TEXT_NEGATIVE_PROMPT
    docstring for the V0.2 scene-3 map-lettering defect this addresses."""
    parts = [scene.get("negative_prompt", "")]
    if not scene.get("allow_generated_text"):
        parts.append(ANTI_TEXT_NEGATIVE_PROMPT)
    return ", ".join(p.strip() for p in parts if p and p.strip())


def generate_keyframes(
    image_provider: ImageProvider, storyboard: dict, out_dir: Path, width: int = 448, height: int = 768,
    seed_base: int = 0, checkpoint: Optional[Callable[[dict], None]] = None,
    reference_set: Optional[dict[str, Path]] = None, default_reference_denoise: float = 0.5,
) -> dict:
    """reference_set (optional): {name: path}, typically produced by
    creative.references.generate_reference_set. A scene opts into
    image-conditioning by setting its own `reference_image` field to one of
    reference_set's keys (and optionally `reference_denoise`, a per-scene
    override of default_reference_denoise) -- e.g. for a recurring
    character or a recurring piece of hardware. A scene with no
    `reference_image` (or when reference_set is None) generates exactly as
    before, pure txt2img -- this is purely additive, existing storyboards
    and callers are unaffected."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for scene in storyboard["scenes"]:
        n = scene["scene_number"]
        # Resume support: a scene whose keyframe already exists on disk from
        # a prior (possibly interrupted) run doesn't need costly regeneration.
        existing = scene.get("keyframe_path")
        if existing and Path(existing).exists():
            continue

        seed = seed_base + n
        ref_name = scene.get("reference_image")
        ref_path = (reference_set or {}).get(ref_name) if ref_name else None
        extra_kwargs = {}
        if ref_path is not None:
            extra_kwargs["reference_image_path"] = ref_path
            extra_kwargs["denoise"] = scene.get("reference_denoise", default_reference_denoise)
        path = image_provider.generate_image(
            prompt=_composed_image_prompt(storyboard, scene), negative_prompt=_composed_negative_prompt(scene),
            width=width, height=height, seed=seed, **extra_kwargs,
        )
        # ComfyUI writes into its own output/ tree; copy so the run directory stays self-contained.
        dest = out_dir / f"scene_{n:02d}.png"
        shutil.copy(path, dest)
        scene["keyframe_path"] = str(dest)
        scene["keyframe_seed"] = seed
        if checkpoint:
            checkpoint(storyboard)

    return storyboard


if __name__ == "__main__":
    import argparse
    import json

    from providers.image.comfyui_sdxl import ComfyUISDXLProvider

    parser = argparse.ArgumentParser(description="Generate keyframes for a storyboard JSON file")
    parser.add_argument("storyboard_json", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("keyframes_test"))
    args = parser.parse_args()

    storyboard = json.loads(args.storyboard_json.read_text(encoding="utf-8"))
    provider = ComfyUISDXLProvider()
    result = generate_keyframes(provider, storyboard, args.out_dir)
    for s in result["scenes"]:
        print(s["scene_number"], "->", s["keyframe_path"])
