from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class Source(BaseModel):
    id: str
    title: str
    url: HttpUrl
    publisher: str
    accessed_at: str
    license_note: str | None = None


class Claim(BaseModel):
    id: str
    text: str
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = False


class ResearchPacket(BaseModel):
    topic: str
    angle: str
    claims: list[Claim] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
