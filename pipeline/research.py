from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import Source


class ResearchProvider(Protocol):
    def search(self, query: str, limit: int = 10) -> list[Source]: ...


@dataclass
class ResearchResult:
    topic: str
    sources: list[Source]


def collect_research(topic: str, providers: list[ResearchProvider], limit: int = 10) -> ResearchResult:
    """Combine provider results while preserving order and removing duplicate URLs."""
    seen: set[str] = set()
    sources: list[Source] = []
    for provider in providers:
        for source in provider.search(topic, limit=limit):
            url = str(source.url)
            if url not in seen:
                seen.add(url)
                sources.append(source)
    return ResearchResult(topic=topic, sources=sources)
