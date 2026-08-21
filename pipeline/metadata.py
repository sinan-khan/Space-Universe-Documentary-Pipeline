from __future__ import annotations


def build_metadata(topic: str, channel: str = "Space & Universe") -> dict:
    title = topic.strip()
    return {
        "title": title,
        "description": (
            f"A cinematic {channel} documentary exploring {topic}. "
            "Sources and media attribution are recorded by the production pipeline."
        ),
        "tags": ["space", "universe", "astronomy", "science", "documentary", "NASA"],
        "hashtags": ["#Space", "#Astronomy", "#Science"],
    }
