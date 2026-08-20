from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import Claim, Source


@dataclass(frozen=True)
class ResearchQuery:
    topic: str
    max_sources: int = 8


class ResearchProvider(Protocol):
    name: str

    def search(self, query: ResearchQuery) -> list[Source]: ...

    def extract_claims(self, sources: list[Source]) -> list[Claim]: ...


class ResearchEngine:
    """Provider-agnostic research orchestration with deterministic ordering."""

    def __init__(self, providers: list[ResearchProvider]):
        self.providers = providers

    def run(self, query: ResearchQuery) -> tuple[list[Source], list[Claim]]:
        sources: list[Source] = []
        claims: list[Claim] = []
        seen_urls: set[str] = set()

        for provider in self.providers:
            for source in provider.search(query):
                if source.url and source.url not in seen_urls:
                    sources.append(source)
                    seen_urls.add(source.url)
                if len(sources) >= query.max_sources:
                    break
            if len(sources) >= query.max_sources:
                break

        for provider in self.providers:
            claims.extend(provider.extract_claims(sources))

        return sources, claims
