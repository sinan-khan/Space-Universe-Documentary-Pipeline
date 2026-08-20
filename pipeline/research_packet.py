from __future__ import annotations

import json
from pathlib import Path

from .models import Claim, Source


def write_research_packet(topic: str, sources: list[Source], claims: list[Claim], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "topic": topic,
        "sources": [source.model_dump(mode="json") for source in sources],
        "claims": [claim.model_dump(mode="json") for claim in claims],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
