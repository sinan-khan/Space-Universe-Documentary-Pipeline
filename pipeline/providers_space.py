from __future__ import annotations

from .models import Claim, Source
from .research_engine import ResearchQuery


class StaticResearchProvider:
    """Offline provider used for tests and dry runs; no network access."""

    name = "static"

    def __init__(self, sources: list[Source] | None = None, claims: list[Claim] | None = None):
        self._sources = sources or []
        self._claims = claims or []

    def search(self, query: ResearchQuery) -> list[Source]:
        return self._sources[: query.max_sources]

    def extract_claims(self, sources: list[Source]) -> list[Claim]:
        return self._claims


class NasaProvider:
    """Interface boundary for the NASA API/media implementation."""

    name = "nasa"

    def search(self, query: ResearchQuery) -> list[Source]:
        raise NotImplementedError("NASA adapter is the next integration stage")

    def extract_claims(self, sources: list[Source]) -> list[Claim]:
        raise NotImplementedError("NASA claim extraction is the next integration stage")
