from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..models import MediaAsset, Source
from ..research_engine import ResearchQuery

BASE_URL = "https://images-api.nasa.gov"


class NASAImageVideoProvider:
    """Resilient NASA Image and Video Library client.

    Search results expose thumbnails, so the provider resolves each selected
    NASA ID through /asset/{id} and returns the best original/full-resolution
    image URL rather than a ~thumb.jpg preview.
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
        lower = {w.lower() for w in words}
        candidates = [cleaned]
        if len(words) > 5:
            candidates.append(" ".join(words[:5]))
        if "star" in lower or "stars" in lower:
            candidates += ["stars", "stellar", "supernova", "neutron star"]
        if "black" in lower and "hole" in lower:
            candidates += ["black hole", "black holes"]
        if "planet" in lower or "planets" in lower:
            candidates += ["planet", "planets", "solar system"]
        if "galaxy" in lower or "galaxies" in lower:
            candidates += ["galaxy", "galaxies"]
        if "nebula" in lower:
            candidates += ["nebula", "nebulae"]
        return list(dict.fromkeys(candidates))

    def _original_url(self, nasa_id: str, media_type: str = "image") -> str | None:
        try:
            payload = self._get(f"/asset/{quote(nasa_id, safe='')}")
        except Exception:
            return None
        links = payload.get("collection", {}).get("items", [])
        candidates: list[str] = []
        for item in links:
            href = str(item.get("href", ""))
            if not href:
                continue
            lower = href.lower()
            if media_type == "image":
                if lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
                    candidates.append(href)
            elif media_type == "video" and lower.endswith((".mp4", ".mov", ".webm")):
                candidates.append(href)
        # Prefer the largest-looking original asset. NASA's asset endpoint
        # commonly returns original before derived thumbnails, but sort away
        # obvious thumbnails as a second line of defense.
        candidates.sort(key=lambda x: ("thumb" in x.lower(), "small" in x.lower(), len(x)))
        return candidates[0] if candidates else None

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
                if not nasa_id or nasa_id in seen:
                    continue
                resolved = self._original_url(nasa_id, media_type or "image")
                if not resolved:
                    continue
                seen.add(nasa_id)
                assets.append(MediaAsset(
                    id=nasa_id,
                    url=resolved,
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
