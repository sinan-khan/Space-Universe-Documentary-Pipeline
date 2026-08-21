from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .captions import write_srt
from .media import download_asset, write_media_manifest
from .models import Scene
from .piper_tts import PiperTTS
from .planner import plan_scenes, retime_scenes
from .providers.gemini import GeminiProvider
from .providers.nasa_images import NASAImageVideoProvider
from .research.models import ResearchPacket
from .video_builder import build_slideshow, mux_audio, render_short
from .shorts import make_shorts


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "documentary"


def _split_for_visuals(script: str, max_scenes: int = 120) -> list[str]:
    """Keep visual/caption units short enough for frequent visual changes."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if not sentences:
        return []
    # One to three sentences per scene; cap the total number for long scripts.
    groups: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        current.append(sentence)
        if len(current) >= 2 or sum(len(x.split()) for x in current) >= 32:
            groups.append(" ".join(current))
            current = []
    if current:
        groups.append(" ".join(current))
    return groups[:max_scenes]


def _probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _validate_media(path: Path, minimum_seconds: float = 0.5) -> None:
    if not path.is_file() or path.stat().st_size < 4096:
        raise RuntimeError(f"Invalid or empty media file: {path}")
    duration = _probe_duration(path)
    if duration < minimum_seconds:
        raise RuntimeError(f"Media duration too short: {path} ({duration:.3f}s)")


def build_documentary(topic: str, output_dir: str | Path = "artifacts") -> Path:
    root = Path(output_dir) / _slug(topic)
    media_dir = root / "media"
    root.mkdir(parents=True, exist_ok=True)

    # Build the script first so visual searches can follow the actual narration.
    packet = ResearchPacket(
        topic=topic,
        angle="Cinematic, factual, accessible space documentary",
        sources=[],
        warnings=["NASA media metadata is a visual source, not scientific claim evidence."],
    )
    script_result = GeminiProvider().generate(packet)
    script = script_result.script
    (root / "script.txt").write_text(script, encoding="utf-8")

    raw_parts = _split_for_visuals(script)
    audio_path = PiperTTS().synthesize(script, root / "narration.wav")
    audio_duration = _probe_duration(audio_path)

    # Create one timeline unit per 1–2 sentences and distribute the measured
    # narration duration across those units. The audio is the source of truth.
    base_scenes = plan_scenes("\n".join(raw_parts), seconds_per_sentence=max(4.0, audio_duration / max(1, len(raw_parts))))
    if not base_scenes:
        raise RuntimeError("No narration scenes were generated")
    scale = audio_duration / sum(max(0.01, s.end - s.start) for s in base_scenes)
    durations = [max(2.5, (scene.end - scene.start) * scale) for scene in base_scenes]
    # Correct rounding/flooring drift on the last scene.
    durations[-1] = max(1.0, audio_duration - sum(durations[:-1]))
    scenes: list[Scene] = retime_scenes(base_scenes, durations)

    # Search per scene and de-duplicate. This yields many more relevant visual
    # changes than a single 12-image slideshow.
    nasa = NASAImageVideoProvider()
    local_assets = []
    seen_ids: set[str] = set()
    for scene in scenes:
        query = scene.visual_query or topic
        candidates = nasa.search_assets(query, page_size=2)
        for asset in candidates:
            if asset.id in seen_ids:
                continue
            try:
                downloaded = download_asset(asset, media_dir)
                local_assets.append(downloaded)
                seen_ids.add(asset.id)
            except Exception:
                continue
        if len(local_assets) >= min(120, max(24, len(scenes))):
            break
    # If scene-specific searches were sparse, fill with broad topic results.
    if len(local_assets) < min(24, len(scenes)):
        for asset in nasa.search_assets(topic, page_size=36):
            if asset.id in seen_ids:
                continue
            try:
                local_assets.append(download_asset(asset, media_dir))
                seen_ids.add(asset.id)
            except Exception:
                continue
            if len(local_assets) >= min(36, max(24, len(scenes))):
                break

    write_media_manifest(local_assets, root)
    if not local_assets:
        raise RuntimeError("No NASA visual assets were downloaded; rendering is blocked.")

    sources = [{
        "id": asset.id,
        "title": asset.title,
        "url": str(asset.url),
        "publisher": "NASA Image and Video Library",
        "accessed_at": "runtime",
        "license_note": asset.license_note,
    } for asset in local_assets]

    image_paths = [Path(asset.local_path) for asset in local_assets if asset.local_path]
    visual_video = build_slideshow(image_paths, audio_duration, root / "visuals.mp4")
    final_video = mux_audio(visual_video, audio_path, root / "documentary.mp4")
    _validate_media(final_video, minimum_seconds=audio_duration * 0.98)

    # Captions are generated from the same scene timeline as the video/audio.
    write_srt(scenes, root / "captions.srt")

    shorts = make_shorts(scenes, count=6, target_seconds=45)
    short_paths: list[str] = []
    for index, short in enumerate(shorts, 1):
        path = root / "shorts" / f"short-{index:02d}.mp4"
        render_short(final_video, short.start, short.end, path)
        _validate_media(path)
        short_paths.append(str(path))

    final_duration = _probe_duration(final_video)
    if abs(final_duration - audio_duration) > 1.0:
        raise RuntimeError(f"Audio/video duration mismatch: audio={audio_duration:.3f}s video={final_duration:.3f}s")

    (root / "production.json").write_text(json.dumps({
        "topic": topic,
        "documentary": str(final_video),
        "narration": str(audio_path),
        "captions": str(root / "captions.srt"),
        "shorts": short_paths,
        "source_assets": sources,
        "scene_count": len(scenes),
        "visual_asset_count": len(local_assets),
        "audio_duration_seconds": round(audio_duration, 3),
        "video_duration_seconds": round(final_duration, 3),
        "publishable": False,
        "reason": "Human QA required before publication.",
    }, indent=2), encoding="utf-8")
    return final_video
