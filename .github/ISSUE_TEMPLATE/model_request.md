---
name: Model / provider request
about: Ask for support for a new LLM, image, video, or TTS model or provider
title: "[Model] "
labels: []
---

**Model name**


**Provider**
Which category — LLM / Image / Video / TTS — and which existing
`providers/` interface it would implement (`LLMProvider` /
`ImageProvider` / `VideoProvider` / `TTSProvider` in `providers/base.py`).
Local or cloud-hosted?

**License**
The model/provider's own license (separate from OpenVideoStudio's own
Apache-2.0 code license — see `docs/LICENSE_STRATEGY.md`).

**Hardware requirements**
VRAM/compute needs, if known — especially relevant given this project's
6GB-VRAM baseline (see `docs/HARDWARE.md`).

**Expected use case**
What can't you do today that this model/provider would enable? What
should happen once it's wired up — e.g. "selecting `X` in
`config.toml`'s `[providers]` section produces a keyframe the same way
the SDXL provider does today."

**Are you interested in implementing this yourself?**
See [`docs/COMMUNITY_TRACKS.md`](../../docs/COMMUNITY_TRACKS.md)'s Model
Gateway and Provider Integrations tracks — most new providers are a
single new file plus a two-line registry entry in `providers/registry.py`.
