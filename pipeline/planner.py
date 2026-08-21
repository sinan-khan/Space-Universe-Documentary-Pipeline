from __future__ import annotations

import re
from .models import Scene


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def plan_scenes(script: str, seconds_per_sentence: float = 6.0) -> list[Scene]:
    """Create a deterministic first-pass timeline; audio duration can refine it later."""
    scenes: list[Scene] = []
    cursor = 0.0
    for index, sentence in enumerate(split_sentences(script), start=1):
        end = cursor + max(4.0, seconds_per_sentence)
        scenes.append(Scene(
            id=f"scene-{index:04d}",
            narration=sentence,
            start=cursor,
            end=end,
            visual_query=sentence,
        ))
        cursor = end
    return scenes


def retime_scenes(scenes: list[Scene], durations: list[float]) -> list[Scene]:
    """Align scenes to measured narration durations without changing scene order."""
    if len(scenes) != len(durations):
        raise ValueError("scene and duration counts must match")
    cursor = 0.0
    result: list[Scene] = []
    for scene, duration in zip(scenes, durations):
        if duration <= 0:
            raise ValueError("scene durations must be positive")
        result.append(scene.model_copy(update={"start": cursor, "end": cursor + duration}))
        cursor += duration
    return result
