"""Provider interfaces for AI Creation mode.

Deliberately thin (Protocols, not ABCs with shared machinery) — a contributor
adding a new provider only needs to match one of these shapes and register it
in providers/registry.py. Nothing in creative/ or core/ ever imports a
concrete provider class; they only ever talk to these interfaces.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from identity.models import CharacterAsset, IdentityApplication, IdentityEncoding


class LLMProvider(Protocol):
    def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2000) -> str: ...


class ImageProvider(Protocol):
    def generate_image(
        self, prompt: str, negative_prompt: str, width: int, height: int, seed: Optional[int] = None,
        # Optional reference-image conditioning (img2img) -- not every
        # provider implements this; callers that need it (e.g.
        # creative/keyframes.py's optional per-scene `reference_image`
        # field, see creative/references.py) should check the concrete
        # provider's own docs. ComfyUISDXLProvider implements both.
        reference_image_path: Optional[Path] = None, denoise: float = 1.0,
    ) -> Path: ...


class VideoProvider(Protocol):
    def generate_video(
        self, prompt: str, duration_seconds: float, width: int, height: int,
        image_path: Optional[Path] = None,  # None = text-to-video, for future providers
        seed: Optional[int] = None, negative_prompt: str = "",
    ) -> Path: ...


@dataclass
class TTSResult:
    audio_path: Path
    duration_seconds: float
    word_timings: Optional[list[tuple[float, str]]] = None  # None if the provider can't supply it


class TTSProvider(Protocol):
    def synthesize(self, text: str, voice: str, language: str) -> TTSResult: ...


@runtime_checkable
class IdentityProvider(Protocol):
    """Model-agnostic character identity control.

    Implementations may use reference images, embeddings, fine-tunes, face
    features, text, or a future mechanism. The creative pipeline only passes
    canonical assets in and opaque, provider-owned conditioning out.
    """

    def encode_character(self, character_asset: CharacterAsset) -> IdentityEncoding: ...

    def apply_identity(self, prompt: str, identity: IdentityEncoding) -> IdentityApplication: ...
