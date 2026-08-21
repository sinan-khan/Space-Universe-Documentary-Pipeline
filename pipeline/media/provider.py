from __future__ import annotations

from abc import ABC, abstractmethod

from .models import MediaManifest


class MediaProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> MediaManifest:
        raise NotImplementedError


class EmptyMediaProvider(MediaProvider):
    def search(self, query: str) -> MediaManifest:
        return MediaManifest()
