from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThumbnailBrief:
    title_text: str
    visual_prompt: str
    aspect_ratio: str = "16:9"


def build_thumbnail_brief(topic: str) -> ThumbnailBrief:
    clean = " ".join(topic.split()).strip()
    words = clean.split()
    # Short, readable text is intentional; the image provider can render it later.
    title_text = " ".join(words[:4]).upper() if words else "SPACE"
    return ThumbnailBrief(
        title_text=title_text,
        visual_prompt=(
            f"Ultra-high-quality cinematic space documentary thumbnail about {clean}; "
            "one dominant cosmic subject, dramatic lighting, strong depth, clean composition, "
            "minimal background clutter, room for large readable text."
        ),
    )
