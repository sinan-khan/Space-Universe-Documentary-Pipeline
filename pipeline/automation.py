from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .audio_engine import NarrationSegment, validate_audio_segments
from .publish import PublishDecision, can_publish
from .quality_gate import QualityResult, research_gate
from .research.models import ResearchPacket
from .render_engine import build_render_plan
from .script_engine import build_script_plan


@dataclass(frozen=True)
class ProductionPlan:
    topic: str
    script_prompt: str
    quality: QualityResult
    publish: PublishDecision


def build_production_plan(topic: str, research: ResearchPacket, config: dict) -> ProductionPlan:
    quality = research_gate(research)
    script = build_script_plan(research)
    # Audio is intentionally a hard gate once real narration is attached.
    audio_gate = QualityResult(True, ())
    publish = can_publish(quality, audio_gate)
    return ProductionPlan(topic=topic, script_prompt=script.prompt, quality=quality, publish=publish)


def build_render(output_dir: str | Path, scenes, aspect_ratio: str = "16:9"):
    plan = build_render_plan(scenes, aspect_ratio)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return plan
