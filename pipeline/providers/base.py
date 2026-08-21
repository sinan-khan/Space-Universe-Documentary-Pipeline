from __future__ import annotations

from abc import ABC, abstractmethod

from ..research.models import ResearchPacket


class ResearchProvider(ABC):
    name = "provider"

    @abstractmethod
    def research(self, topic: str) -> ResearchPacket:
        raise NotImplementedError
