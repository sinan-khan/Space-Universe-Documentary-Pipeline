from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request, urlopen

from ..models import MediaAsset


class MediaManifest:
    def __init__(self, assets: list[MediaAsset] | None = None):
        self.assets = assets or []


def download_asset(asset: MediaAsset, output_dir: str | Path) -> MediaAsset:
    """Download a remote media preview into the documentary artifact directory."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    suffix = Path(str(asset.url).split("?")[0]).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov"}:
        suffix = ".jpg"
    destination = directory / f"{asset.id}{suffix}"
    request = Request(
        str(asset.url),
        headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"},
    )
    with urlopen(request, timeout=60) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"Empty media response for {asset.id}")
    destination.write_bytes(data)
    return asset.model_copy(update={"local_path": str(destination)})


def write_media_manifest(assets: list[MediaAsset], root: str | Path) -> Path:
    """Write a JSON manifest describing downloaded media assets."""
    path = Path(root) / "media_manifest.json"
    path.write_text(
        json.dumps({"assets": [asset.model_dump(mode="json") for asset in assets]}, indent=2),
        encoding="utf-8",
    )
    return path


__all__ = ["MediaAsset", "MediaManifest", "download_asset", "write_media_manifest"]
