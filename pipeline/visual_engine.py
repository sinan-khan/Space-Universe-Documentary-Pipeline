from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import MediaAsset, Scene


@dataclass(frozen=True)
class VisualCandidate:
    scene_id: str
    query: str
    assets: tuple[MediaAsset, ...]
    generated_fallback: bool = False


class VisualProvider(Protocol):
    name: str

    def search(self, query: str, limit: int = 8) -> list[MediaAsset]: ...


def plan_visuals(scenes: list[Scene], provider: VisualProvider, fallback_generated: bool = True) -> list[VisualCandidate]:
    plans: list[VisualCandidate] = []
    for scene in scenes:
        assets = tuple(provider.search(scene.visual_query, limit=8))
        plans.append(VisualCandidate(
            scene_id=scene.id,
            query=scene.visual_query,
            assets=assets,
            generated_fallback=not assets and fallback_generated,
        ))
    return plans
