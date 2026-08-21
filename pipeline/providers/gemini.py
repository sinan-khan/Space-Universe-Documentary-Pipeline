from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.request import Request, urlopen

from ..research.models import ResearchPacket
from ..script_engine import build_script_plan


@dataclass(frozen=True)
class GeneratedScript:
    title: str
    script: str


class GeminiProvider:
    """Google Gemini REST adapter with retry/backoff and no committed credentials."""

    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 180):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.timeout = timeout
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "4"))

    def generate(self, packet: ResearchPacket) -> GeneratedScript:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Gemini script generation")
        plan = build_script_plan(packet)
        prompt = plan.prompt + "\n\nReturn only documentary narration. Preserve [claim:cN] markers. Target 3,600–5,600 words."
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                request = Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
                with urlopen(request, timeout=self.timeout) as response:
                    payload = json.load(response)
                parts = payload.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts).strip()
                if not text:
                    raise RuntimeError("Gemini returned empty text")
                return GeneratedScript(title=plan.title, script=text)
            except Exception as exc:
                last_error = exc
                if attempt + 1 < self.max_retries:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"Gemini generation failed after retries: {last_error}") from last_error
