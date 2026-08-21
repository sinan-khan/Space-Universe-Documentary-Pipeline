from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..research.models import Claim, ResearchPacket, Source
from .base import ResearchProvider


class JPLSSDSolarSystemProvider(ResearchProvider):
    """Read-only adapter for JPL SSD/CNEOS machine-readable solar-system data."""

    name = "jpl-ssd"
    base_url = "https://ssd-api.jpl.nasa.gov"

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, str]) -> dict:
        url = f"{self.base_url}{path}?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            return json.load(response)

    def research(self, topic: str) -> ResearchPacket:
        # Keep this provider conservative: it currently records the authoritative
        # JPL endpoint as a source and leaves claim extraction to the verifier.
        source = Source(
            id="jpl-ssd-service",
            title=f"JPL SSD/CNEOS data service — {topic}",
            url="https://ssd-api.jpl.nasa.gov/",
            publisher="NASA/JPL",
            accessed_at="runtime",
            license_note="Check the JPL SSD/CNEOS fair-use policy and endpoint-specific terms before automated high-volume use.",
        )
        return ResearchPacket(
            topic=topic,
            angle="Solar-system data source available for verification",
            sources=[source],
            warnings=["No claim is generated from the endpoint until an endpoint-specific query and verifier are configured."],
        )
