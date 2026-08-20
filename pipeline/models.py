from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class Source(BaseModel):
    title: str
    url: HttpUrl
    provider: str
    license_note: str = ""
    attribution: str = ""


class Claim(BaseModel):
    text: str
    sources: list[Source] = Field(default_factory=list)


class Scene(BaseModel):
    id: str
    narration: str
    start: float
    end: float
    visual_query: str
    source_urls: list[HttpUrl] = Field(default_factory=list)
    generated_visual: bool = False


class Documentary(BaseModel):
    topic: str
    title: str
    script: str
    claims: list[Claim] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)

    @property
    def duration(self) -> float:
        return max((scene.end for scene in self.scenes), default=0.0)


class Short(BaseModel):
    title: str
    start: float
    end: float
    hook: str
    source_scene_ids: list[str]


class MediaAsset(BaseModel):
    id: str
    url: HttpUrl
    provider: str
    title: str
    attribution: str = ""
    license_note: str = ""
    local_path: str | None = None
