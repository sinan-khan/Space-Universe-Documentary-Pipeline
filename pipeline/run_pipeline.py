from __future__ import annotations

import argparse
import json
from pathlib import Path

from .piper_tts import PiperTTS
from .providers.gemini import GeminiProvider
from .research_engine import ResearchEngine, ResearchQuery
from .providers.nasa_images import NASAImageVideoProvider


def run(topic: str, output_dir: str = "artifacts", dry_run: bool = True) -> Path:
    root = Path(output_dir) / topic.lower().replace(" ", "-")
    root.mkdir(parents=True, exist_ok=True)
    nasa = NASAImageVideoProvider()
    engine = ResearchEngine([nasa])
    sources, claims = engine.run(ResearchQuery(topic=topic, max_sources=8))
    packet = {
        "topic": topic,
        "sources": [s.__dict__ for s in sources],
        "claims": [c.__dict__ for c in claims],
        "dry_run": dry_run,
    }
    (root / "research.json").write_text(json.dumps(packet, indent=2, default=str), encoding="utf-8")
    if dry_run:
        return root
    from .research.models import ResearchPacket
    research_packet = ResearchPacket(topic=topic, angle="Automated space documentary", sources=sources)
    script = GeminiProvider().generate(research_packet)
    (root / "script.txt").write_text(script.script, encoding="utf-8")
    PiperTTS().synthesize(script.script, root / "narration.wav")
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description="Space documentary production runner")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", default="artifacts")
    parser.add_argument("--live", action="store_true", help="Generate script and TTS instead of dry-run")
    args = parser.parse_args()
    result = run(args.topic, args.output, dry_run=not args.live)
    print(result)


if __name__ == "__main__":
    main()
