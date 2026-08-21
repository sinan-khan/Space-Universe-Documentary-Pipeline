from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from ..models import MediaAsset, Source
from ..research_engine import ResearchQuery

BASE_URL = "https://images-api.nasa.gov"


class NASAImageVideoProvider:
    """Dependency-free adapter for NASA's public Image and Video Library API.

    Search is deliberately resilient: a natural-language documentary title can be
    too specific for NASA's index, so we progressively try simpler search terms.
    """

    name = "nasa-image-video-library"

    def _get(self, path: str) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                request = Request(
                    f"{BASE_URL}{path}",
                    headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"},
                )
                with urlopen(request, timeout=30) as response:
                    return json.loads(response.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"NASA Image API request failed: {last_error}") from last_error

    @staticmethod
    def _queries(query: str) -> list[str]:
        cleaned = " ".join(query.split()).strip()
        words = [w.strip(".,!?;:\"'()[]") for w in cleaned.split()]
        # Keep queries broad enough to match NASA's metadata index.
        candidates = [cleaned]
        if len(words) > 5:
            candidates.append(" ".join(words[:5]))
        if "star" in {w.lower() for w in words}:
            candidates += ["stars", "stellar", "supernova"]
        if "black" in {w.lower() for w in words} and "hole" in {w.lower() for w in words}:
            candidates += ["black hole", "black holes"]
        if "planet" in {w.lower() for w in words}:
            candidates += ["planet", "planets", "solar system"]
        if "galaxy" in {w.lower() for w in words}:
            candidates += ["galaxy", "galaxies"]
        # Preserve order while removing duplicates.
        return list(dict.fromkeys(candidates))

    def search_assets(self, query: str, media_type: str | None = "image", page_size: int = 25) -> list[MediaAsset]:
        seen: set[str] = set()
        assets: list[MediaAsset] = []
        for search_query in self._queries(query):
            params = f"q={quote(search_query)}&page_size={max(1, min(page_size, 100))}"
            if media_type:
                params += f"&media_type={quote(media_type)}"
            try:
                payload = self._get(f"/search?{params}")
            except Exception:
                continue
            for item in payload.get("collection", {}).get("items", []):
                data = (item.get("data") or [{}])[0]
                nasa_id = str(data.get("nasa_id", ""))
                links = item.get("links") or []
                preview = next((x.get("href") for x in links if x.get("rel") == "preview"), None)
                if not nasa_id or not preview or nasa_id in seen:
                    continue
                seen.add(nasa_id)
                assets.append(MediaAsset(
                    id=nasa_id,
                    url=preview,
                    provider=self.name,
                    title=data.get("title") or nasa_id,
                    attribution=data.get("photographer") or data.get("secondary_creator") or "NASA",
                    license_note="Check the specific NASA media item and current NASA Media Usage Guidelines before publication.",
                ))
                if len(assets) >= page_size:
                    return assets
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
        return []
