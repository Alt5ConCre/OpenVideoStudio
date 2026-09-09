# InsightFace-Dependent Provider Licensing

This document exists because the most obvious way to implement real
face-identity conditioning — IP-Adapter FaceID, InstantID, PuLID — all
depend on [InsightFace](https://github.com/deepinsight/insightface)'s face
detection/recognition models (`buffalo_l`, `antelopev2`) to extract a face
embedding. InsightFace's own license terms restrict those specific model
*weights* to non-commercial research use, which is a materially different
license than this project's own Apache-2.0.

**This applies to any provider that depends on InsightFace, regardless of
which Protocol category it implements (`ImageProvider`, `IdentityProvider`,
or any future category in `studio/providers/base.py`) or which
`PROVIDERS[...]` dict entry it's registered under in
`studio/providers/registry.py`.** The license risk comes from *what the
provider loads at runtime* (an InsightFace model), not from *which Python
Protocol it happens to implement* — an `ImageProvider` that calls
InsightFace under the hood (e.g. through a ComfyUI node like
`InstantIDFaceAnalysis`) is exactly as exposed as an `IdentityProvider`
that does the same thing. Anyone adding such a provider anywhere under
`studio/providers/` must follow the rules below so that using
OpenVideoStudio's Apache-2.0 code never silently puts a user in violation
of a model license the project doesn't control.

## 1. Which current providers touch InsightFace

| Provider | File | Registered as | Depends on InsightFace? |
|---|---|---|---|
| `TextIdentityProvider` | `studio/providers/identity_text.py` | `PROVIDERS["identity"]["text"]` | No — pure text formatting from `CharacterAsset.description`. Safe. |
| `ImageReferenceIdentityProvider` | `studio/providers/identity_image.py` | `PROVIDERS["identity"]["image_reference"]` | No — hands back one of the Character Bible's own reference image `Path`s for img2img conditioning. No face-recognition model involved. Safe. |
| `InstantIDImageProvider` | `studio/providers/image/instantid_sdxl.py` | `PROVIDERS["image"]["instantid_sdxl"]` | **Yes** — its ComfyUI graph (`providers/workflows/character_instantid_v1_api.json`) includes an `InstantIDFaceAnalysis` node, which loads an InsightFace model to extract the face embedding InstantID conditions on. Subject to every rule below, the same as any InsightFace-backed `IdentityProvider` would be — being registered under `PROVIDERS["image"]` instead of `PROVIDERS["identity"]` changes nothing about the license exposure. |

`TextIdentityProvider` and `ImageReferenceIdentityProvider` are the only
two providers in this repository, in any category, that are unrestricted
for open-source and commercial use today, same as the rest of this
repository's Apache-2.0 code. `InstantIDImageProvider` is not — it is
registered in `registry.py` today, so the rules below apply to it now,
not just at some future registration point.

This table must be updated whenever a new provider — **in any category,
not just `identity`** — that depends on InsightFace is added anywhere
under `studio/providers/`.

## 2. Any InsightFace-dependent provider must be opt-in, never the default

Any provider — `ImageProvider`, `IdentityProvider`, or otherwise — built on
IP-Adapter FaceID, InstantID, PuLID, or anything else that loads
`buffalo_l`/`antelopev2` (or any other InsightFace model pack), including
`InstantIDImageProvider`, must:

- **Never be its category's implicit default in `PROVIDERS[...]`.** A
  caller must pass its registry name explicitly (e.g.
  `get_provider("image", "instantid_sdxl")`, or `get_provider("identity",
  "<insightface_backed_name>")` for a future identity provider) to use it
  — nothing in `creative/*.py`'s default pipeline path may select it
  automatically, regardless of which `PROVIDERS[...]` category it lives
  under.
- **Fail loudly, not silently, when its InsightFace dependency isn't
  installed.** Missing `insightface`/missing model weights must raise a
  clear error at provider construction, not degrade to some other identity
  method behind the user's back.
- **Document the license requirement at the point of opt-in** — the
  provider's module docstring and any config/CLI flag that enables it must
  say, in the user's path, that enabling it means accepting InsightFace's
  own model license (non-commercial research use — see below), separate
  from and in addition to OpenVideoStudio's own Apache-2.0 license.

This keeps the default OpenVideoStudio experience — and anything a
commercial user runs without deliberately opting in — entirely within
Apache-2.0 code and models this project actually controls the license of.

## 3. Model weights are never bundled in this repository

No InsightFace model file (`buffalo_l`, `antelopev2`, or any `.onnx`/
`.safetensors`/`.bin` derived from InsightFace's training data) may be
committed to this repository, shipped in a release artifact, or
auto-downloaded by default. A provider that needs one must:

- Document the exact model pack name, its official download source, and
  where it goes on disk (mirroring how `studio/providers/identity_image.py`
  and `docs/character_identity_architecture.md` already document Character
  Bible directory layout).
- Require the user to download it themselves (or trigger an explicit,
  clearly-labeled one-time download the user consents to at the moment
  they opt in) — never fetch it silently as a side effect of installing or
  running OpenVideoStudio.

## 4. InsightFace's actual license terms (quoted verbatim)

InsightFace has no standalone `LICENSE` file at its repository root —
these terms live in prose across three of its own `README.md` files. All
three are consistent with each other.

**[deepinsight/insightface — root `README.md`](https://github.com/deepinsight/insightface/blob/master/README.md#license):**

> The code of InsightFace is released under the MIT License. There is no
> limitation for both academic and commercial usage.
>
> The training data containing the annotation (and the models trained with
> these data) are available for non-commercial research purposes only.
>
> Both manual-downloading models from our github repo and auto-downloading
> models with our python-library follow the above license policy(which is
> for non-commercial research purposes only).
>
> `2025-11-24 Update:`
> 1. For inswapper series face swap models (e.g., inswapper_128.onnx/
>    inswapper-512-live), please contact contact@insightface.ai for
>    licensing and additional support.
> 2. For open-sourced face recognition models (e.g., buffalo_l package),
>    please contact recognition-oss-pack@insightface.ai for licensing.
> 3. For advanced face recognition SDK and models (e.g., InspireFace SDK),
>    please contact contact@insightface.ai for licensing and additional
>    support.

**[deepinsight/insightface — `python-package/README.md`](https://github.com/deepinsight/insightface/blob/master/python-package/README.md#license):**

> The code of InsightFace Python Library is released under the MIT
> License. There is no limitation for both academic and commercial usage.
>
> **The pretrained models we provided with this library are available for
> non-commercial research purposes only, including both auto-downloading
> models and manual-downloading models.**

**[deepinsight/insightface — `model_zoo/README.md`](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md):**

> :bell: **ALL models are available for non-commercial research purposes
> only.**

— immediately followed by the model table that lists `antelopev2` (407MB)
and `buffalo_l` (326MB) by name.

### What this means in practice

- InsightFace's **code** (MIT) is unrestricted, including commercial use.
- InsightFace's **model weights** — `buffalo_l`, `antelopev2`, and every
  other pack in their model zoo — are licensed for **non-commercial
  research purposes only**, a materially different (and non-open-source)
  restriction that has nothing to do with OpenVideoStudio's own
  Apache-2.0 license.
- `buffalo_l` carries an additional 2025-11-24 requirement to contact
  `recognition-oss-pack@insightface.ai` for licensing even though it's
  called an "open-sourced" package — its terms are not settled by simply
  reading the README once and assuming non-commercial use is
  pre-authorized.
- A commercial user of OpenVideoStudio who enables an InsightFace-backed
  provider — `InstantIDImageProvider` today, or any future provider in any
  category — is accepting InsightFace's license on top of
  OpenVideoStudio's, and must resolve it directly with InsightFace (the
  contact addresses above) if their use is commercial. OpenVideoStudio's
  own Apache-2.0 license cannot and does not grant rights to InsightFace's
  models.
