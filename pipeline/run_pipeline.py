from __future__ import annotations

import argparse
from pathlib import Path

from .production import build_documentary


def run(topic: str, output_dir: str = "artifacts", dry_run: bool = True) -> Path:
    if dry_run:
        root = Path(output_dir) / topic.lower().replace(" ", "-")
        root.mkdir(parents=True, exist_ok=True)
        (root / "DRY_RUN.txt").write_text(
            "Dry run only. Use --live after configuring Gemini, Piper and FFmpeg.\n",
            encoding="utf-8",
        )
        return root
    return build_documentary(topic, output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Space documentary production runner")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output", default="artifacts")
    parser.add_argument("--live", action="store_true", help="Run the full local production pipeline")
    args = parser.parse_args()
    result = run(args.topic, args.output, dry_run=not args.live)
    print(result)


if __name__ == "__main__":
    main()
