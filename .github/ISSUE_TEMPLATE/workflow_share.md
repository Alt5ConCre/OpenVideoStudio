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

**What does this workflow produce?**
One or two sentences — style, subject, length.

**Prompt**
```
paste your starting prompt here
```

**Configuration**
- Aspect ratio / target duration:
- Providers used (default Ollama + ComfyUI + Edge TTS, or something
  else — see `providers/registry.py`):
- Any non-default `config.toml` settings:

**What made this work well**
Anything you learned — phrasing that reduced character drift, a
duration/style combination that rendered cleanly, a storyboard edit you
made at the review gate, etc.

**Known limitations**
Be as honest about this as `examples/hero_demo/README.md` is about its
own run — e.g. "character identity still drifts in scene 4" is more
useful to the next person than an unqualified success claim.

**Attach if you can**
Keyframes, the final video, or the storyboard JSON (strip any local file
paths first — see `docs/OPEN_SOURCE_SECURITY_AUDIT.md` for why that
matters).
