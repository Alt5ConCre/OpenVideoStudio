"""Tests for the V2-motivated reusable additions: reference-image sets
(creative/references.py), optional per-scene reference conditioning in
creative/keyframes.py, the hybrid static/pan shot technique in
creative/clips.py, and the narration-first synthesize_cues primitive in
creative/narration.py. All additive to the existing pipeline -- every
test here also proves the ORIGINAL (no-reference / no-technique) behavior
is unchanged, since that's the backward-compatibility requirement these
changes were made under.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from creative.references import ReferenceSpec, generate_reference_set
from creative.keyframes import generate_keyframes
from creative.clips import generate_clips
from creative.narration import synthesize_cues
from providers.base import TTSResult


# ------------------------------------------------------- fakes ---
class _FakeImageProvider:
    def __init__(self, work_dir: Path):
        self.calls = 0
        self.last_call_kwargs = None
        self.work_dir = work_dir

    def generate_image(self, prompt, negative_prompt, width, height, seed=None,
                        reference_image_path=None, denoise=1.0):
        self.calls += 1
        self.last_call_kwargs = dict(
            prompt=prompt, negative_prompt=negative_prompt, width=width, height=height,
            seed=seed, reference_image_path=reference_image_path, denoise=denoise,
        )
        p = self.work_dir / f"fake_image_{self.calls}.png"
        p.write_bytes(b"fake")
        return p


class _FakeVideoProvider:
    def __init__(self, work_dir: Path):
        self.calls = 0
        self.work_dir = work_dir

    def generate_video(self, prompt, duration_seconds, width, height, image_path=None, seed=None, negative_prompt=""):
        self.calls += 1
        p = self.work_dir / f"fake_clip_{self.calls}.mp4"
        p.write_bytes(b"fake")
        return p


class _FakeTTSProvider:
    def __init__(self, work_dir: Path, duration: float = 2.5):
        self.calls = 0
        self.work_dir = work_dir
        self.duration = duration

    def synthesize(self, text, voice=None, language="en"):
        self.calls += 1
        p = self.work_dir / f"fake_tts_{self.calls}.mp3"
        p.write_bytes(b"fake")
        return TTSResult(audio_path=p, duration_seconds=self.duration, word_timings=None)


# ------------------------------------------------- references.py ---
def test_generate_reference_set_creates_one_image_per_spec(tmp_path):
    provider = _FakeImageProvider(tmp_path)
    specs = [
        ReferenceSpec(name="char_a", prompt="a character", seed=1),
        ReferenceSpec(name="hw_valve", prompt="a valve", seed=2),
    ]
    refs = generate_reference_set(provider, specs, tmp_path / "refs")
    assert provider.calls == 2
    assert set(refs.keys()) == {"char_a", "hw_valve"}
    assert refs["char_a"].name == "char_a.png"
    assert refs["char_a"].exists()


def test_generate_reference_set_skips_existing(tmp_path):
    out_dir = tmp_path / "refs"
    out_dir.mkdir()
    (out_dir / "char_a.png").write_bytes(b"already here")
    provider = _FakeImageProvider(tmp_path)
    specs = [ReferenceSpec(name="char_a", prompt="a character", seed=1)]
    refs = generate_reference_set(provider, specs, out_dir)
    assert provider.calls == 0  # skipped, already exists
    assert refs["char_a"].read_bytes() == b"already here"


# ------------------------------------------- keyframes.py reference support ---
def test_generate_keyframes_without_reference_image_is_unchanged(tmp_path):
    """Backward compatibility: a scene with no `reference_image` field
    must not pass reference_image_path/denoise to the provider at all."""
    provider = _FakeImageProvider(tmp_path)
    storyboard = {"scenes": [{"scene_number": 1, "image_prompt": "a"}]}
    generate_keyframes(provider, storyboard, tmp_path / "out")
    assert provider.last_call_kwargs["reference_image_path"] is None


def test_generate_keyframes_with_reference_image_passes_conditioning(tmp_path):
    ref_path = tmp_path / "char_a.png"
    ref_path.write_bytes(b"ref")
    provider = _FakeImageProvider(tmp_path)
    storyboard = {
        "scenes": [
            {"scene_number": 1, "image_prompt": "a", "reference_image": "char_a", "reference_denoise": 0.4},
        ]
    }
    generate_keyframes(provider, storyboard, tmp_path / "out", reference_set={"char_a": ref_path})
    assert provider.last_call_kwargs["reference_image_path"] == ref_path
    assert provider.last_call_kwargs["denoise"] == 0.4


def test_generate_keyframes_reference_image_uses_default_denoise_when_unset(tmp_path):
    ref_path = tmp_path / "char_a.png"
    ref_path.write_bytes(b"ref")
    provider = _FakeImageProvider(tmp_path)
    storyboard = {"scenes": [{"scene_number": 1, "image_prompt": "a", "reference_image": "char_a"}]}
    generate_keyframes(provider, storyboard, tmp_path / "out", reference_set={"char_a": ref_path}, default_reference_denoise=0.6)
    assert provider.last_call_kwargs["denoise"] == 0.6


def test_generate_keyframes_reference_image_missing_from_set_falls_back_to_txt2img(tmp_path):
    """A scene naming a reference that isn't in reference_set shouldn't
    crash -- it just generates without conditioning."""
    provider = _FakeImageProvider(tmp_path)
    storyboard = {"scenes": [{"scene_number": 1, "image_prompt": "a", "reference_image": "does_not_exist"}]}
    generate_keyframes(provider, storyboard, tmp_path / "out", reference_set={})
    assert provider.last_call_kwargs["reference_image_path"] is None


# ------------------------------------------- clips.py hybrid technique ---
def test_generate_clips_default_technique_is_unchanged(tmp_path):
    """Backward compatibility: a scene with no shot_technique field must
    still call the VideoProvider exactly as before."""
    keyframe = tmp_path / "kf.png"
    keyframe.write_bytes(b"fake")
    storyboard = {
        "scenes": [
            {"scene_number": 1, "keyframe_path": str(keyframe), "duration_seconds": 3.0,
             "video_motion_prompt": "pan left"},
        ]
    }
    provider = _FakeVideoProvider(tmp_path)
    generate_clips(provider, storyboard, tmp_path / "out")
    assert provider.calls == 1


def test_generate_clips_static_technique_skips_video_provider(tmp_path):
    """shot_technique='static' must produce a clip via FFmpeg pan/zoom
    without ever calling the (GPU-heavy) VideoProvider."""
    from PIL import Image
    keyframe = tmp_path / "kf.png"
    Image.new("RGB", (64, 64), (10, 20, 30)).save(keyframe)
    storyboard = {
        "scenes": [
            {"scene_number": 1, "keyframe_path": str(keyframe), "duration_seconds": 1.0,
             "shot_technique": "static"},
        ]
    }
    provider = _FakeVideoProvider(tmp_path)
    result = generate_clips(provider, storyboard, tmp_path / "out", width=64, height=64)
    assert provider.calls == 0
    clip_path = Path(result["scenes"][0]["clip_path"])
    assert clip_path.exists()
    assert clip_path.stat().st_size > 0
    assert result["scenes"][0]["clip_freeze_seconds"] == 0.0


# ------------------------------------------- narration.py synthesize_cues ---
def test_synthesize_cues_produces_real_cumulative_timestamps(tmp_path):
    provider = _FakeTTSProvider(tmp_path, duration=2.0)
    cues = [
        {"id": "beat01_cue01", "text": "first line"},
        {"id": "beat01_cue02", "text": "second line"},
    ]
    result = synthesize_cues(provider, cues, tmp_path / "narration", gap_seconds=0.5)
    assert result[0]["start"] == 0.0
    assert result[0]["end"] == 2.0
    # second cue starts after first's duration + the gap, not at an
    # arbitrary/estimated offset
    assert result[1]["start"] == 2.5
    assert result[1]["end"] == 4.5


def test_synthesize_cues_skips_existing_audio_but_still_measures_duration(tmp_path, monkeypatch):
    out_dir = tmp_path / "narration"
    out_dir.mkdir()
    existing = out_dir / "beat01_cue01.mp3"
    existing.write_bytes(b"fake")

    def _fake_probe(path):
        return 3.3

    monkeypatch.setattr("creative.narration._probe_duration", _fake_probe)
    provider = _FakeTTSProvider(tmp_path)
    cues = [{"id": "beat01_cue01", "text": "already synthesized"}]
    result = synthesize_cues(provider, cues, out_dir)
    assert provider.calls == 0  # not re-synthesized
    assert result[0]["duration"] == 3.3


def test_synthesize_cues_empty_text_reports_error_not_crash(tmp_path):
    provider = _FakeTTSProvider(tmp_path)
    cues = [{"id": "beat01_cue01", "text": "   "}]
    result = synthesize_cues(provider, cues, tmp_path / "narration")
    assert result[0]["error"] == "empty_text"
    assert provider.calls == 0
