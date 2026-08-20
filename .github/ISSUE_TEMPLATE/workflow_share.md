---
name: Workflow share
about: Share a prompt, storyboard, or provider configuration that worked well
title: "[Workflow] "
labels: []
---

*There's no workflow marketplace yet (it's a long-term idea, not a
shipped feature — see `ROADMAP.md`'s Long-term vision section). Today,
sharing a workflow means posting it here or as a
[Discussion](../../discussions) so others can copy it, and optionally
opening a PR to add it under `examples/`.*

**Workflow name**


**Description**
What does this workflow produce — style, subject, length — and what's
the starting prompt?

**Required models**
Providers used (default Ollama + ComfyUI + Edge TTS, or something else —
see `providers/registry.py`), and any specific model files involved.

**Hardware requirements**
GPU/VRAM this was actually run on — see `docs/HARDWARE.md` for what's
independently verified versus what's a single report.

**Example output**
Attach keyframes, the final video, or the storyboard JSON if you can
(strip any local file paths first — see
`docs/OPEN_SOURCE_SECURITY_AUDIT.md` for why that matters).

**Known limitations**
Be as honest about this as `examples/hero_demo/README.md` is about its
own run — e.g. "character identity still drifts in scene 4" is more
useful to the next person than an unqualified success claim.
