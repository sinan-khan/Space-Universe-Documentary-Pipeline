from __future__ import annotations

import json
import re
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


def _split_for_visuals(script: str, max_scenes: int = 24) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if len(sentences) <= max_scenes:
        return sentences
    size = max(1, (len(sentences) + max_scenes - 1) // max_scenes)
    return [" ".join(sentences[i:i + size]) for i in range(0, len(sentences), size)][:max_scenes]


def build_documentary(topic: str, output_dir: str | Path = "artifacts") -> Path:
    root = Path(output_dir) / _slug(topic)
    media_dir = root / "media"
    root.mkdir(parents=True, exist_ok=True)

    nasa = NASAImageVideoProvider()
    assets = nasa.search_assets(topic, page_size=12)
    local_assets = []
    for asset in assets:
        try:
            local_assets.append(download_asset(asset, media_dir))
        except Exception:
            continue
    write_media_manifest(local_assets, root)

    sources = [
        {
            "id": asset.id,
            "title": asset.title,
            "url": str(asset.url),
            "publisher": "NASA Image and Video Library",
            "accessed_at": "runtime",
            "license_note": asset.license_note,
        }
        for asset in local_assets
    ]
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
    from .tts import wav_duration
    audio_duration = wav_duration(audio_path)
    base_scenes = plan_scenes("\n".join(raw_parts), seconds_per_sentence=max(4.0, audio_duration / max(1, len(raw_parts))))
    durations = [max(4.0, scene.end - scene.start) for scene in base_scenes]
    scenes: list[Scene] = retime_scenes(base_scenes, durations)

    if not local_assets:
        raise RuntimeError("No NASA visual assets were downloaded; rendering is blocked.")
    image_paths = [Path(asset.local_path) for asset in local_assets if asset.local_path]
    visual_video = build_slideshow(image_paths, audio_duration, root / "visuals.mp4")
    final_video = mux_audio(visual_video, audio_path, root / "documentary.mp4")
    write_srt(scenes, root / "captions.srt")

    shorts = make_shorts(scenes, count=6, target_seconds=45)
    short_paths = []
    for index, short in enumerate(shorts, 1):
        path = root / "shorts" / f"short-{index:02d}.mp4"
        try:
            render_short(final_video, short.start, short.end, path)
            short_paths.append(str(path))
        except Exception:
            continue

    (root / "production.json").write_text(json.dumps({
        "topic": topic,
        "documentary": str(final_video),
        "narration": str(audio_path),
        "captions": str(root / "captions.srt"),
        "shorts": short_paths,
        "source_assets": sources,
        "publishable": False,
        "reason": "Human QA required before publication.",
    }, indent=2), encoding="utf-8")
    return final_video
