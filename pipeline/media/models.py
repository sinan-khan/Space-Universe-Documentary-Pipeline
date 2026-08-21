from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class MediaAsset(BaseModel):
    id: str
    source_url: HttpUrl
    local_path: str | None = None
    media_type: str
    provider: str
    license_note: str | None = None
    attribution: str | None = None
    duration_seconds: float | None = Field(default=None, ge=0)


class MediaManifest(BaseModel):
    assets: list[MediaAsset] = Field(default_factory=list)
