from pydantic import HttpUrl

from pipeline.models import Claim, Documentary, Scene, Source
from pipeline.planner import plan_scenes, retime_scenes
from pipeline.quality import validate_documentary
from pipeline.shorts import make_shorts


def test_scene_planning_is_deterministic():
    scenes = plan_scenes("One sentence. Another sentence!")
    assert len(scenes) == 2
    assert scenes[0].start == 0
    assert scenes[1].start == scenes[0].end


def test_retiming_uses_measured_audio_durations():
    scenes = plan_scenes("A. B.")
    retimed = retime_scenes(scenes, [2.5, 4.0])
    assert retimed[0].end == 2.5
    assert retimed[1].start == 2.5
    assert retimed[1].end == 6.5


def test_shorts_are_generated():
    scenes = plan_scenes("A. B. C. D. E. F.")
    assert len(make_shorts(scenes, count=3)) == 3


def test_quality_requires_sources_for_claims():
    claim = Claim(text="A factual claim")
    doc = Documentary(
        topic="test", title="test", script="one two three",
        claims=[claim], scenes=plan_scenes("A sentence."),
    )
    errors = validate_documentary(doc, {"quality": {"minimum_script_words": 0, "require_source_for_factual_claim": True}})
    assert any("no source" in error for error in errors)
