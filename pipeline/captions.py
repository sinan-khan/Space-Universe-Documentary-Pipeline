from __future__ import annotations

from pathlib import Path

from .models import Scene


def _timestamp(seconds: float) -> str:
    total_ms = max(0, round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def write_srt(scenes: list[Scene], output_path: str | Path) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for index, scene in enumerate(scenes, 1):
        blocks.append(f"{index}\n{_timestamp(scene.start)} --> {_timestamp(scene.end)}\n{scene.narration.strip()}\n")
    target.write_text("\n".join(blocks), encoding="utf-8")
    return target
