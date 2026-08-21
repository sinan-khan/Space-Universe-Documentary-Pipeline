from __future__ import annotations

from pathlib import Path

from .thumbnail_engine import build_thumbnail_brief


def write_thumbnail_brief(topic: str, output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    brief = build_thumbnail_brief(topic)
    target = directory / "thumbnail-brief.json"
    target.write_text(
        '{\n'
        f'  "title_text": {brief.title_text!r},\n'
        f'  "visual_prompt": {brief.visual_prompt!r},\n'
        f'  "aspect_ratio": {brief.aspect_ratio!r}\n'
        '}\n', encoding="utf-8"
    )
    return target
