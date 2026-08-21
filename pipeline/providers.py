from __future__ import annotations

from .models import MediaAsset, Source


class NasaProvider:
    """Interface placeholder for NASA API/media integration.

    Network access and API credentials are intentionally kept outside core logic.
    Implement search/download here using NASA's official endpoints and persist
    the returned attribution/license metadata with every asset.
    """

    name = "nasa"

    def search(self, query: str, limit: int = 10) -> list[Source]:
        return []


class GeneratedVisualProvider:
    name = "generated"

    def plan(self, query: str) -> dict:
        return {"provider": self.name, "prompt": query, "status": "planned"}


def media_manifest(assets: list[MediaAsset]) -> list[dict]:
    return [asset.model_dump(mode="json") for asset in assets]
