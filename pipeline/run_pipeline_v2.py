from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path

from .piper_tts import PiperTTS
from .providers.gemini import GeminiProvider
from .providers.nasa_images import NASAImageVideoProvider
from .research_engine import ResearchEngine, ResearchQuery
from .video_builder import build_slideshow, mux_audio, render_short


def slug(value: str) -> str:
    return "-".join(value.lower().split())


def download(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as handle:
        handle.write(response.read())
    return destination


def run(topic: str, output_dir: str = "artifacts", live: bool = False) -> Path:
    root = Path(output_dir) / slug(topic)
    root.mkdir(parents=True, exist_ok=True)

    nasa = NASAImageVideoProvider()
    engine = ResearchEngine([nasa])
    sources, claims = engine.run(ResearchQuery(topic=topic, max_sources=8))
    (root / "research.json").write_text(json.dumps({
        "topic": topic,
        "sources": [s.__dict__ for s in sources],
        "claims": [c.__dict__ for c in claims],
    }, indent=2, default=str), encoding="utf-8")

    if not live:
        (root / "RUN_STATUS.txt").write_text("DRY RUN PASSED: research stage completed. No paid generation, audio, rendering, or upload was performed.\n", encoding="utf-8")
        return root

    from .research.models import ResearchPacket
    packet = ResearchPacket(topic=topic, angle="Automated space documentary", sources=sources)
    generated = GeminiProvider().generate(packet)
    (root / "script.txt").write_text(generated.script, encoding="utf-8")

    narration = PiperTTS().synthesize(generated.script, root / "narration.wav")
    assets = nasa.search_assets(topic, page_size=12)
    image_paths: list[Path] = []
    manifest: list[dict] = []
    for index, asset in enumerate(assets):
        try:
            path = download(asset.url, root / "media" / f"{index:03d}.jpg")
            image_paths.append(path)
            manifest.append({"id": asset.id, "title": asset.title, "url": asset.url, "attribution": asset.attribution, "license_note": asset.license_note})
        except Exception as exc:
            manifest.append({"id": asset.id, "title": asset.title, "url": asset.url, "error": str(exc)})
    (root / "media-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if not image_paths:
        raise RuntimeError("No downloadable NASA preview assets were available; refusing to render a fake documentary.")

    # Baseline renderer: visual duration follows the measured narration duration.
    import wave
    with wave.open(str(narration), "rb") as wav:
        duration = wav.getnframes() / float(wav.getframerate())
    visuals = build_slideshow(image_paths, duration, root / "visuals.mp4")
    documentary = mux_audio(visuals, narration, root / "documentary.mp4")

    # Safe baseline Shorts: evenly distributed excerpts until the scene-aware cutter is enabled.
    short_dir = root / "shorts"
    short_dir.mkdir(exist_ok=True)
    segment = min(60.0, max(30.0, duration / 6.0))
    for index in range(6):
        start = min(max(0.0, duration - segment), index * max(1.0, (duration - segment) / 5.0))
        render_short(documentary, start, start + segment, short_dir / f"short-{index + 1:02d}.mp4")

    (root / "RUN_STATUS.txt").write_text("LIVE RENDER PASSED. Upload remains disabled by design. Inspect documentary.mp4 and shorts/ before publishing.\n", encoding="utf-8")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Space documentary pipeline")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", default="artifacts")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    print(run(args.topic, args.output, args.live))


if __name__ == "__main__":
    main()
