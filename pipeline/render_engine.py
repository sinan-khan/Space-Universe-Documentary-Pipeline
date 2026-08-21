from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import Scene


@dataclass(frozen=True)
class RenderSegment:
    scene_id: str
    start: float
    end: float
    narration_audio: Path | None
    visual_path: Path | None


@dataclass(frozen=True)
class RenderPlan:
    aspect_ratio: str
    width: int
    height: int
    segments: tuple[RenderSegment, ...]


def build_render_plan(scenes: list[Scene], aspect_ratio: str = "16:9") -> RenderPlan:
    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    elif aspect_ratio == "16:9":
        width, height = 1920, 1080
    else:
        raise ValueError(f"unsupported aspect ratio: {aspect_ratio}")
    return RenderPlan(
        aspect_ratio=aspect_ratio,
        width=width,
        height=height,
        segments=tuple(
            RenderSegment(scene.id, scene.start, scene.end, None, None)
            for scene in scenes
        ),
    )
