"""Image-reference identity provider — real img2img conditioning instead of
text-only description.

TextIdentityProvider (providers/identity_text.py) only conditions the
PROMPT TEXT, which measurably helps wardrobe/setting but lets facial
identity drift scene to scene (see creative/identity.py's module
docstring — that's V0.2's known weakness). This provider instead hands
back one of the Character Bible's own reference images, for the caller to
pass straight into ImageProvider.generate_image's existing
reference_image_path/denoise img2img path (implemented by
ComfyUISDXLProvider) — real image conditioning, not a text description
of one.

Picking "the first reference image" is deliberately the simplest possible
selection rule for a first working version — it doesn't try to pick the
best-lit/most front-facing image or combine multiple references. That
refinement (or a proper face-identity lock via IPAdapter-FaceID/
InstantID/PuLID) is future work, not required for this interface to be
useful today.
"""
from __future__ import annotations

from identity.models import CharacterAsset, IdentityApplication, IdentityEncoding


class ImageReferenceIdentityProvider:
    provider_name = "image_reference"

    def encode_character(self, character_asset: CharacterAsset) -> IdentityEncoding:
        if not character_asset.reference_images:
            raise ValueError(
                f"Character {character_asset.character_id!r} has no reference_images "
                "for ImageReferenceIdentityProvider to use"
            )
        reference = character_asset.reference_images[0]
        return IdentityEncoding(
            character_id=character_asset.character_id,
            provider=self.provider_name,
            method="first_reference_image",
            payload=reference.path,
            metadata={"view": reference.view, "bible_version": character_asset.bible_version},
        )

    def apply_identity(self, prompt: str, identity: IdentityEncoding) -> IdentityApplication:
        if identity.provider != self.provider_name:
            raise ValueError(
                f"Identity encoding belongs to provider {identity.provider!r}, not {self.provider_name!r}"
            )
        return IdentityApplication(
            prompt=prompt,
            controls={"reference_image_path": identity.payload},
            metadata={"character_id": identity.character_id, "identity_method": identity.method},
        )


if __name__ == "__main__":
    import argparse

    from identity import load_character_asset
    from providers.image.comfyui_sdxl import ComfyUISDXLProvider

    parser = argparse.ArgumentParser(
        description=(
            "Real-generation smoke test: renders the same character with two "
            "different prompts, with and without image_reference identity "
            "conditioning, so the four outputs can be compared by eye."
        )
    )
    parser.add_argument("character_bible_root", type=Path, help="Path to a Character Bible directory")
    parser.add_argument("--out-dir", type=Path, default=Path("identity_image_test"))
    parser.add_argument("--denoise", type=float, default=0.55)
    parser.add_argument("--width", type=int, default=448)
    parser.add_argument("--height", type=int, default=768)
    args = parser.parse_args()

    asset = load_character_asset(args.character_bible_root)
    identity = ImageReferenceIdentityProvider().encode_character(asset)
    print(f"Using reference image: {identity.payload}")

    prompts = [
        ("scene_a", "standing in a rain-soaked alley at night, neon reflections"),
        ("scene_b", "sitting at a wooden desk in warm daylight, reading a letter"),
    ]

    provider = ComfyUISDXLProvider()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, prompt in prompts:
        application = ImageReferenceIdentityProvider().apply_identity(prompt, identity)
        with_ref = provider.generate_image(
            prompt=application.prompt, negative_prompt="", width=args.width, height=args.height,
            seed=1, reference_image_path=application.controls["reference_image_path"], denoise=args.denoise,
        )
        without_ref = provider.generate_image(
            prompt=prompt, negative_prompt="", width=args.width, height=args.height, seed=1,
        )
        import shutil
        shutil.copy(with_ref, args.out_dir / f"{name}_with_reference.png")
        shutil.copy(without_ref, args.out_dir / f"{name}_without_reference.png")
        print(f"{name}: wrote {name}_with_reference.png and {name}_without_reference.png")

    print(f"\nCompare pairs in {args.out_dir} -- the *_with_reference.png images "
          "should look more like the same character across scene_a/scene_b than "
          "the *_without_reference.png ones do.")
