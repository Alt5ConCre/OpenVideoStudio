# Roadmap

Status labels used throughout: **DONE** (shipped, tested), **HELP
WANTED** (a real community contribution track, see
`docs/COMMUNITY_TRACKS.md`), **RESEARCH** (open-ended, contributions can
be experiments/benchmarks, not only code), **PLANNED** (maintainer-led,
not started).

## v0.1-alpha — DONE

- Prompt → script → storyboard → keyframes → clips → narration →
  subtitles → final video
- Local generation via Ollama + ComfyUI (SDXL + LTX-Video)
- Edge TTS narration, FFmpeg/NVENC assembly

## v0.2 — DONE

- ~60-second pipeline, duration-accuracy fixes
- Resumable runs, per-scene checkpointing (a scene whose keyframe/clip
  already exists on disk is skipped on rerun — this makes targeted
  regeneration possible by clearing one scene's artifact path and
  rerunning with `force=True`, though there's no UI for it yet; see
  `docs/COMMUNITY_TRACKS.md` Track F)
- LTX freeze/motion QC
- Storyboard schema validation
- Prompt-based visual continuity (single shared `visual_identity` string)

## v0.3 — DONE

- Structured character/environment identity, generated once and reused
  verbatim across every scene (`creative/identity.py`) — replaces v0.2's
  single free-text `visual_identity` string, which drifted on facial
  identity across scenes
- Stronger continuity fields (`narrative_purpose`, `continuity_from_previous`,
  `visual_change`, `camera_change`) plus soft narrative-quality warnings
- Stronger semantic validation at LLM output boundaries (rejects
  parseable-but-wrong-shaped responses instead of silently coercing them)
- Real Ollama + ComfyUI end-to-end validation
- 67/67 tests passing
- Independently reviewed and cleared (see the project's development
  history)

## Community Tracks — HELP WANTED / RESEARCH

Not scheduled to any version — these grow through contribution, on their
own timeline. Full detail in `docs/COMMUNITY_TRACKS.md`.

| Track | Status |
|---|---|
| AI Art Studio (character/environment bibles, reference conditioning, Krita integration) | HELP WANTED |
| Universal Model Gateway (OpenAI-compatible, llama.cpp, vLLM, enterprise endpoints) | HELP WANTED |
| Character Consistency (face-reference conditioning, benchmarks) | RESEARCH / HELP WANTED |
| Provider Integrations (additional image/video models) | HELP WANTED |
| Platform Support (Linux, macOS, Apple Silicon, Docker) | HELP WANTED |
| Timeline / Editor | HELP WANTED |
| AI Video QC (final-video freeze QC, duplicate-shot/audio QC) | HELP WANTED |
| Documentation / Localization | HELP WANTED |

## v0.4+ — PLANNED

Maintainer-led, not yet started, no committed timeline:

- Multi-minute videos (beyond the currently-verified ~60-second range)
- A formal plugin ecosystem for providers (today's registration is a
  one-file-plus-one-line pattern in `providers/registry.py`; a real
  plugin SDK is Track B's "Provider plugin SDK" item, tracked as HELP
  WANTED, but a stable plugin *contract* is a maintainer-led decision)
- Pro Mode UI (script → character design → environment design →
  storyboard review → keyframe review → video generation → edit → final
  video) — the pipeline stages already exist; the guided UI layer over
  them does not
- Additional providers beyond what ships in v0.3 or lands via Track D

## Long-term vision — PLANNED, no version assigned, not started

These are direction-setting ideas, not scheduled work — they exist so
contributors can see where the project is trying to go beyond v0.4, not
because any of them has a design or an owner yet. See
[`docs/architecture.md`](docs/architecture.md)'s "Long-term vision"
diagram for how these relate to each other conceptually. None of this
exists in code today.

- **Character Memory System** — a persistent identity/appearance store,
  beyond today's single-shot identity object (`creative/identity.py`).
  Builds on whatever [Track C](docs/COMMUNITY_TRACKS.md#track-c--character-consistency)
  (Character Consistency) establishes first; there's no memory system to
  build until identity representation itself is more solid.
- **Scene Graph System** — a structured, queryable representation of
  scenes/characters/objects/relationships, replacing today's flat
  per-scene storyboard dict. Would be a significant internal data-model
  change, not a small addition.
- **Visual Workflow Editor** — a node/graph-based editor for the pipeline
  itself (distinct from the Timeline Editor in
  [Track F](docs/COMMUNITY_TRACKS.md#track-f--timeline--editor), which
  edits the *output* video, not the generation pipeline).
- **Better asset management** — organizing/searching/reusing generated
  keyframes, clips, and identities across projects, instead of today's
  one-run-directory-per-generation layout.
- **Multi-agent video production** — exploring whether specialized
  agents (writing, art direction, continuity checking) produce better
  results than today's single-pass script/storyboard/identity calls. Pure
  research direction at this point — no design exists.
- **Collaborative workflow sharing / community workflow marketplace** —
  today, "sharing a workflow" means posting a prompt and settings via a
  [Workflow share](.github/ISSUE_TEMPLATE/workflow_share.md) issue or a
  Discussion (see `docs/contribution.md`). An actual marketplace would
  need real infrastructure — hosting, moderation, versioning — that
  doesn't exist and isn't designed yet. Don't read "marketplace" here as
  a promise of a specific feature; it's a direction, not a spec.

If one of these interests you, the honest starting point for most of
them is a GitHub Discussion proposing a design, not a PR — see
`CONTRIBUTING.md`'s "What needs discussion first."

## What this roadmap deliberately does not promise

No date commitments beyond what's already DONE. No feature on this list
is claimed to exist in the product until it's actually merged and tested
— see `docs/OPEN_SOURCE_LAUNCH_STRATEGY.md`'s overclaiming failure mode
for why that distinction is enforced strictly here.
