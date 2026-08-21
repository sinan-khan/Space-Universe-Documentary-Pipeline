from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class UploadRequest:
    video_path: str
    title: str
    description: str
    privacy_status: str = "private"
    publish_at: str | None = None


class YouTubePublisher:
    """Publishing boundary. OAuth/client implementation is intentionally isolated."""

    def __init__(self):
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        self.refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    def validate_credentials(self) -> None:
        missing = [name for name, value in (("YOUTUBE_CLIENT_ID", self.client_id), ("YOUTUBE_CLIENT_SECRET", self.client_secret), ("YOUTUBE_REFRESH_TOKEN", self.refresh_token)) if not value]
        if missing:
            raise RuntimeError("Missing YouTube credentials: " + ", ".join(missing))

    def upload(self, request: UploadRequest) -> None:
        self.validate_credentials()
        raise NotImplementedError("Connect the YouTube OAuth client before enabling uploads")
