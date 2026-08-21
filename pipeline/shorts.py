from __future__ import annotations

from .models import Scene, Short


def make_shorts(scenes: list[Scene], count: int = 6, target_seconds: float = 45.0) -> list[Short]:
    """Pick evenly distributed, self-contained 35–60s windows from the master timeline."""
    if not scenes:
        return []
    total_end = scenes[-1].end
    if total_end <= 1:
        return []
    count = max(1, min(count, len(scenes)))
    target = max(35.0, min(60.0, target_seconds))
    starts = [0.0 if count == 1 else (total_end - target) * i / (count - 1) for i in range(count)]
    shorts: list[Short] = []
    for i, start in enumerate(starts):
        start = max(0.0, min(start, max(0.0, total_end - 1.0)))
        end = min(total_end, start + target)
        # Snap to scene boundaries so captions/narration aren't cut mid-scene.
        start_scene = next((s for s in scenes if s.start >= start), scenes[0])
        end_scene = next((s for s in reversed(scenes) if s.end <= end), scenes[-1])
        actual_start = start_scene.start
        actual_end = max(actual_start + 1.0, min(total_end, end_scene.end))
        if actual_end - actual_start < 30.0:
            actual_end = min(total_end, actual_start + target)
        hook_scene = start_scene
        shorts.append(Short(
            title=hook_scene.narration[:70].rstrip(".!?") or f"Space fact #{i + 1}",
            start=actual_start,
            end=actual_end,
            hook=hook_scene.narration,
            source_scene_ids=[s.id for s in scenes if s.start < actual_end and s.end > actual_start],
        ))
    return shorts
