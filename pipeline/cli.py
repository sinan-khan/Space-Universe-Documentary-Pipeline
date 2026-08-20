from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .metadata import build_metadata
from .planner import plan_scenes
from .shorts import make_shorts
from .render import write_edit_decision_list


def run(topic: str, config_path: str, dry_run: bool) -> dict:
    config = load_config(config_path)
    # Provider adapters will populate the researched script in the next stage.
    # The dry-run foundation deliberately creates a deterministic planning artifact.
    script = (
        f"This is a planning run for {topic}. "
        "Research, narration and source verification are required before publication."
    )
    scenes = plan_scenes(script)
    shorts = make_shorts(scenes, config["channel"]["shorts"]["per_long_form"])
    output = Path(config["runtime"]["output_dir"])
    output.mkdir(parents=True, exist_ok=True)
    payload = {
        "topic": topic,
        "dry_run": dry_run,
        "metadata": build_metadata(topic, config["channel"]["name"]),
        "scenes": [s.model_dump(mode="json") for s in scenes],
        "shorts": [s.model_dump(mode="json") for s in shorts],
    }
    (output / "run-plan.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Space documentary automation engine")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--topic", required=True)
    run_parser.add_argument("--config", default="./config/channel.yaml")
    run_parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.command == "run":
        result = run(args.topic, args.config, args.dry_run)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
