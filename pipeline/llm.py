from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.request import Request, urlopen

from .research.models import ResearchPacket
from .script_engine import build_script_plan


@dataclass(frozen=True)
class GeneratedScript:
    title: str
    script: str


class OpenAIResponsesProvider:
    """Minimal dependency-free OpenAI Responses API adapter.

    The API key is read only from OPENAI_API_KEY. No credential is stored in the repo.
    """

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 180):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        self.timeout = timeout

    def generate(self, packet: ResearchPacket) -> GeneratedScript:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for script generation")
        plan = build_script_plan(packet)
        body = {
            "model": self.model,
            "input": (
                plan.prompt
                + "\n\nReturn only the documentary narration. Keep claim markers such as [claim:c1] "
                "next to the factual sentences they support. Target 3,600–5,600 words."
            ),
        }
        request = Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Space-Universe-Documentary-Pipeline/1.0",
            },
            method="POST",
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        text = payload.get("output_text", "").strip()
        if not text:
            raise RuntimeError("OpenAI returned no output_text")
        return GeneratedScript(title=plan.title, script=text)
