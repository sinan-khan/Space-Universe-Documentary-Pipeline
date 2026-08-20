from __future__ import annotations

from .models import Scene, Short


def make_shorts(scenes: list[Scene], count: int = 6, target_seconds: float = 45.0) -> list[Short]:
    if not scenes:
        return []
    # Prefer scenes with strong narration length and spread selections across the documentary.
    step = max(1, len(scenes) // count)
    shorts: list[Short] = []
    for i in range(min(count, len(scenes))):
        scene = scenes[min(i * step, len(scenes) - 1)]
        end = min(scene.end + target_seconds, scenes[-1].end)
        if end <= scene.start:
            continue
        shorts.append(Short(
            title=scene.narration[:70].rstrip(".!?") or f"Space fact #{i + 1}",
            start=scene.start,
            end=end,
            hook=scene.narration,
            source_scene_ids=[scene.id],
        ))
    return shorts
