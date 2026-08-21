from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ResearchPacket


class ResearchProvider(ABC):
    """Provider boundary for research APIs; implementations stay outside core logic."""

    @abstractmethod
    def research(self, topic: str) -> ResearchPacket:
        raise NotImplementedError


class EmptyResearchProvider(ResearchProvider):
    def research(self, topic: str) -> ResearchPacket:
        return ResearchPacket(
            topic=topic,
            angle="Research provider not configured",
            warnings=["No external research provider configured; publication must be blocked."],
        )
