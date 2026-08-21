from pipeline.media.models import MediaAsset, MediaManifest
from pipeline.publish import can_publish
from pipeline.quality_gate import research_gate
from pipeline.research.models import Claim, ResearchPacket, Source


def test_empty_research_blocks_publication():
    result = research_gate(ResearchPacket(topic="x", angle="y"))
    assert not result.passed
    assert not can_publish(result).allowed


def test_research_with_sources_and_claims_passes():
    packet = ResearchPacket(
        topic="x",
        angle="y",
        sources=[Source(id="s1", title="Source", url="https://example.com", publisher="Example", accessed_at="2026-08-20")],
        claims=[Claim(id="c1", text="Fact", source_ids=["s1"], confidence=0.95)],
    )
    assert research_gate(packet).passed


def test_media_manifest_tracks_rights_metadata():
    asset = MediaAsset(id="a1", source_url="https://example.com/video.mp4", media_type="video", provider="test", license_note="review")
    assert MediaManifest(assets=[asset]).assets[0].license_note == "review"
