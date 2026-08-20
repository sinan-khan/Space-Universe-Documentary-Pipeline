from __future__ import annotations

import json
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from ..models import Claim, Source
from ..research_engine import ResearchQuery


class NASAImageLibraryProvider:
    """Read-only adapter for NASA's public Image and Video Library API."""

    name = "nasa-image-library"
    endpoint = "https://images-api.nasa.gov/search"

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def _get(self, params: dict[str, str]) -> dict:
        url = f"{self.endpoint}?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            return json.load(response)

    def search(self, query: ResearchQuery) -> list[Source]:
        data = self._get({"q": query.topic, "media_type": "image,video", "page_size": str(query.max_sources)})
        items = data.get("collection", {}).get("items", [])
        results: list[Source] = []
        for item in items:
            meta = (item.get("data") or [{}])[0]
            href = item.get("href") or ""
            if not href:
                continue
            results.append(
                Source(
                    title=meta.get("title") or query.topic,
                    url=href,
                    provider=self.name,
                    license_note="NASA media; verify item-level third-party restrictions before publication.",
                    attribution="NASA",
                )
            )
        return results

    def extract_claims(self, sources: list[Source]) -> list[Claim]:
        # The media API is a discovery source, not a scientific fact database.
        # Claims are intentionally left to a science-text provider in the next stage.
        return []
