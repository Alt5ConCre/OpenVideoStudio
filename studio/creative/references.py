"""Reusable reference-image generation.

Generic capability, not tied to any specific project: generate a NAMED SET
of stable visual references (a recurring character, a piece of hardware,
any recurring visual subject) once via txt2img, for later reuse as
image-conditioning input to keyframe generation -- see
creative/keyframes.py's optional per-scene `reference_image` field, which
reads from the dict this module returns.

Motivation: V0.3's identity system (creative/identity.py) keeps character/
environment consistency at the TEXT level -- the same formatted description
is injected into every scene's prompt. That measurably helps wardrobe and
setting, but a diffusion model re-reading the same text description each
time is not the same as re-drawing the same reference image, and visual
identity (especially faces) still drifts scene to scene. This module adds
the other half: real image-conditioning via ComfyUISDXLProvider's existing
`reference_image_path`/`denoise` parameters (already present in
providers/image/comfyui_sdxl.py, previously unused by any creative/*.py
caller). This is real reference-image conditioning (img2img via VAEEncode),
not identity-specialized -- it biases composition/color/rough structure
toward the reference, not a face-identity lock (that would need
IPAdapter-FaceID/InstantID/PuLID, new node packages/model downloads, out of
scope here -- see docs/COMMUNITY_TRACKS.md Track C).
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from providers.base import ImageProvider


@dataclass
class ReferenceSpec:
    """One reference image to generate. `name` is the key later scenes use
    (creative/keyframes.py scene field `reference_image`) to select it."""
    name: str
    prompt: str
    seed: int
    negative_prompt: str = ""


def generate_reference_set(
    image_provider: ImageProvider,
    specs: list[ReferenceSpec],
    out_dir: Path,
    width: int = 448,
    height: int = 768,
) -> dict[str, Path]:
    """Generates one txt2img reference image per spec into out_dir, named
    `{spec.name}.png`. Resumable: a spec whose output file already exists
    on disk is skipped (same pattern as creative/keyframes.py's per-scene
    skip-if-exists). Returns {spec.name: path}, suitable for passing
    straight into creative/keyframes.generate_keyframes's `reference_set`
    parameter."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    refs: dict[str, Path] = {}
    for spec in specs:
        dest = out_dir / f"{spec.name}.png"
        if not dest.exists():
            path = image_provider.generate_image(
                prompt=spec.prompt,
                negative_prompt=spec.negative_prompt,
                width=width,
                height=height,
                seed=spec.seed,
            )
            shutil.copy(path, dest)
        refs[spec.name] = dest
    return refs
