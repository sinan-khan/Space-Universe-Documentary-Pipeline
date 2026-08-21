from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class NarrationSegment:
    id: str
    text: str
    audio_path: Path | None = None
    duration_seconds: float | None = None


class NarrationProvider(Protocol):
    name: str

    def synthesize(self, segments: list[NarrationSegment], output_dir: Path) -> list[NarrationSegment]: ...


def validate_audio_segments(segments: list[NarrationSegment]) -> list[str]:
    errors: list[str] = []
    for segment in segments:
        if not segment.audio_path:
            errors.append(f"missing audio: {segment.id}")
        elif not segment.audio_path.exists():
            errors.append(f"audio file does not exist: {segment.id}")
        if segment.duration_seconds is not None and segment.duration_seconds <= 0:
            errors.append(f"invalid audio duration: {segment.id}")
    return errors
