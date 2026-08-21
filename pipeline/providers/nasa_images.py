from __future__ import annotations

from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen
import json

from ..models import MediaAsset, Source
from ..research_engine import ResearchQuery

BASE_URL = "https://images-api.nasa.gov"


class NASAImageVideoProvider:
    """Small dependency-free adapter for NASA's public Image and Video Library API."""

    name = "nasa-image-video-library"

    def _get(self, path: str) -> dict[str, Any]:
        request = Request(f"{BASE_URL}{path}", headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"})
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def search_assets(self, query: str, media_type: str | None = None, page_size: int = 25) -> list[MediaAsset]:
        params = f"q={quote(query)}&page_size={max(1, min(page_size, 100))}"
        if media_type:
            params += f"&media_type={quote(media_type)}"
        payload = self._get(f"/search?{params}")
        assets: list[MediaAsset] = []
        for item in payload.get("collection", {}).get("items", []):
            data = (item.get("data") or [{}])[0]
            nasa_id = str(data.get("nasa_id", ""))
            links = item.get("links") or []
            preview = next((x.get("href") for x in links if x.get("rel") == "preview"), None)
            href = item.get("href")
            if not nasa_id or not preview:
                continue
            assets.append(MediaAsset(
                id=nasa_id,
                url=preview,
                provider=self.name,
                title=data.get("title") or nasa_id,
                attribution=data.get("photographer") or data.get("secondary_creator") or "NASA",
                license_note="Check the specific NASA media item and current NASA Media Usage Guidelines before publication.",
            ))
        return assets

    def search(self, query: ResearchQuery) -> list[Source]:
        assets = self.search_assets(query.topic, page_size=query.max_sources)
        return [Source(
            title=asset.title,
            url=asset.url,
            provider=self.name,
            license_note=asset.license_note,
            attribution=asset.attribution,
        ) for asset in assets]

    def extract_claims(self, sources: list[Source]):
        # Media metadata is not treated as scientific evidence.
        return []
