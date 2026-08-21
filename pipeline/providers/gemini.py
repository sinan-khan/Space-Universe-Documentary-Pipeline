from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ..research.models import ResearchPacket
from ..script_engine import build_script_plan


@dataclass(frozen=True)
class GeneratedScript:
    title: str
    script: str


class GeminiProvider:
    """Google Gemini REST adapter with configurable API version/model and retries."""

    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 180):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.api_version = os.getenv("GEMINI_API_VERSION", "v1beta")
        self.timeout = timeout
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "4"))

    def generate(self, packet: ResearchPacket) -> GeneratedScript:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Gemini script generation")

        plan = build_script_plan(packet)
        prompt = plan.prompt + "\n\nReturn only documentary narration. Preserve [claim:cN] markers. Target 3,600–5,600 words."
        url = (
            f"https://generativelanguage.googleapis.com/{self.api_version}/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                request = Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "Space-Universe-Documentary-Pipeline/1.0"},
                    method="POST",
                )
                with urlopen(request, timeout=self.timeout) as response:
                    payload = json.load(response)

                candidates = payload.get("candidates") or []
                if not candidates:
                    raise RuntimeError(f"Gemini returned no candidates: {payload}")
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
                if not text:
                    raise RuntimeError(f"Gemini returned empty text: {payload}")
                return GeneratedScript(title=plan.title, script=text)

            except HTTPError as exc:
                # A 404 usually means the configured model is unavailable on the
                # selected API version. Include the response body so failures are
                # actionable, without ever logging the API key.
                try:
                    detail = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    detail = str(exc)
                last_error = RuntimeError(f"Gemini HTTP {exc.code}: {detail[:1000]}")
            except Exception as exc:
                last_error = exc

            if attempt + 1 < self.max_retries:
                time.sleep(2 ** attempt)

        raise RuntimeError(f"Gemini generation failed after retries: {last_error}") from last_error
