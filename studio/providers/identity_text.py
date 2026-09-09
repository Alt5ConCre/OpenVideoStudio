"""Text-only baseline identity provider.

This preserves today's deterministic prompt behavior behind the same
interface that future identity providers will implement.
"""
from __future__ import annotations

from identity.models import CharacterAsset, IdentityApplication, IdentityEncoding


class TextIdentityProvider:
    provider_name = "text"

    def encode_character(self, character_asset: CharacterAsset) -> IdentityEncoding:
        description = character_asset.description
        fields = (
            "name_or_role", "approx_age", "gender_presentation", "hair", "face_shape",
            "skin_tone", "eye_features", "distinctive_features", "wardrobe",
            "accessories", "body_build", "visual_style",
        )
        text = ", ".join(
            str(description[field]).strip()
            for field in fields
            if description.get(field) is not None and str(description[field]).strip()
        )
        return IdentityEncoding(
            character_id=character_asset.character_id,
            provider=self.provider_name,
            method="canonical_text",
            payload=text,
            metadata={"bible_version": character_asset.bible_version},
        )

    def apply_identity(self, prompt: str, identity: IdentityEncoding) -> IdentityApplication:
        if identity.provider != self.provider_name:
            raise ValueError(
                f"Identity encoding belongs to provider {identity.provider!r}, not {self.provider_name!r}"
            )
        identity_text = str(identity.payload).strip()
        conditioned = ", ".join(part for part in (identity_text, prompt.strip()) if part)
        return IdentityApplication(
            prompt=conditioned,
            metadata={"character_id": identity.character_id, "identity_method": identity.method},
        )
