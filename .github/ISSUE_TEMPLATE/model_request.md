---
name: Model / provider request
about: Ask for support for a new LLM, image, video, or TTS model or provider
title: "[Model] "
labels: []
---

**What problem does this solve?**
What can't you do today that this model/provider would enable?

**Which category?**
LLM / Image / Video / TTS — and which existing `providers/` interface it
would implement (`LLMProvider` / `ImageProvider` / `VideoProvider` /
`TTSProvider` in `providers/base.py`).

**Model / provider details**
- Name and link (model card, API docs, or repository):
- Local or cloud-hosted:
- License (for the model weights, if applicable — separate from
  OpenVideoStudio's own Apache-2.0 code license, see
  `docs/LICENSE_STRATEGY.md`):
- Hardware requirements, if known:

**Expected behavior**
What should happen once this is wired up — e.g. "selecting `X` in
`config.toml`'s `[providers]` section produces a keyframe the same way
the SDXL provider does today."

**Possible solution**
If you've looked at `providers/registry.py` and have a rough idea of what
the new provider file would need to implement, sketch it here. Not
required — "I don't know the codebase well enough yet" is a fine answer.

**Are you interested in implementing this yourself?**
See [`docs/COMMUNITY_TRACKS.md`](../../docs/COMMUNITY_TRACKS.md)'s Model
Gateway and Provider Integrations tracks — most new providers are a
single new file plus a two-line registry entry.
