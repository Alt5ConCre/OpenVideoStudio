"""Stage 5: per-scene narration_text -> speech audio, via TTSProvider."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from providers.base import TTSProvider


def synthesize_cues(
    tts_provider: TTSProvider, cues: list[dict], out_dir: Path,
    language: str = "en", voice: Optional[str] = None, gap_seconds: float = 0.35,
) -> list[dict]:
    """Narration-FIRST primitive: synthesize a flat list of narration cues
    -- [{"id": "beat01_cue01", "text": "..."}, ...], in any grouping a
    caller wants (per-sentence, per-beat, per-scene) -- independent of any
    storyboard/scene structure, since in a narration-first workflow the
    narration is finalized BEFORE scenes/shots are designed, not derived
    from them.

    Unlike generate_narration below (which times each scene off a
    duration_seconds estimated from word count, then reconciles against
    the actual clip afterward -- see creative/pipeline.py's run_edit
    retiming), every cue's duration here is the real ffprobe-measured
    length of its own synthesized audio, and start/end are cumulative real
    timestamps -- no estimation. A caller building a narration-first
    timeline sizes shots to these measured durations, not the other way
    around.

    Returns cues with `audio_path`, `duration`, `start`, `end` added (and
    `word_timings` if the provider reports them). Resumable: a cue whose
    `id`.mp3/.wav already exists in out_dir is not re-synthesized, but its
    real duration is still measured and folded into the cumulative
    timeline -- the same resume discipline as generate_narration below."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    cursor = 0.0
    for c in cues:
        cue_id = c["id"]
        text = c["text"].strip()
        if not text:
            results.append({**c, "error": "empty_text"})
            continue

        existing = next(iter(out_dir.glob(f"{cue_id}.*")), None)
        if existing is not None:
            duration = _probe_duration(existing)
            audio_path = existing
            word_timings = None
        else:
            result = tts_provider.synthesize(text, voice=voice, language=language)
            audio_path = out_dir / f"{cue_id}{Path(result.audio_path).suffix}"
            shutil.copy(result.audio_path, audio_path)
            duration = result.duration_seconds
            word_timings = result.word_timings

        entry = {
            **c, "audio_path": str(audio_path), "duration": duration,
            "start": cursor, "end": cursor + duration,
        }
        if word_timings:
            entry["word_timings"] = word_timings
        results.append(entry)
        cursor += duration + gap_seconds

    return results


def _probe_duration(path: Path) -> float:
    import subprocess
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def generate_narration(tts_provider: TTSProvider, storyboard: dict, out_dir: Path, language: str = "en", voice: str = None) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for scene in storyboard["scenes"]:
        n = scene["scene_number"]
        text = scene.get("narration_text", "").strip()
        if not text:
            scene["narration_error"] = "empty_narration_text"
            continue

        result = tts_provider.synthesize(text, voice=voice, language=language)
        dest = out_dir / f"scene_{n:02d}.mp3"
        shutil.copy(result.audio_path, dest)
        scene["narration_path"] = str(dest)
        scene["narration_duration"] = result.duration_seconds
        scene["narration_word_timings"] = result.word_timings

    return storyboard


if __name__ == "__main__":
    import argparse
    import json

    from providers.tts.edge_tts_provider import EdgeTTSProvider

    parser = argparse.ArgumentParser(description="Generate narration for a storyboard JSON file")
    parser.add_argument("storyboard_json", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("narration_test"))
    parser.add_argument("--language", default="en")
    args = parser.parse_args()

    storyboard = json.loads(args.storyboard_json.read_text(encoding="utf-8"))
    provider = EdgeTTSProvider()
    result = generate_narration(provider, storyboard, args.out_dir, args.language)
    for s in result["scenes"]:
        print(s["scene_number"], "->", s.get("narration_path", s.get("narration_error")), s.get("narration_duration"))
