from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request, urlopen

from .models import MediaAsset


def download_asset(asset: MediaAsset, output_dir: str | Path) -> MediaAsset:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    suffix = Path(str(asset.url).split("?")[0]).suffix or ".bin"
    target = directory / f"{asset.id}{suffix}"
    request = Request(str(asset.url), headers={"User-Agent": "Space-Universe-Documentary-Pipeline/1.0"})
    with urlopen(request, timeout=60) as response, target.open("wb") as handle:
        handle.write(response.read())
    return asset.model_copy(update={"local_path": str(target)})


def write_media_manifest(assets: list[MediaAsset], output_dir: str | Path) -> Path:
    target = Path(output_dir) / "media-manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps([a.model_dump(mode="json") for a in assets], indent=2), encoding="utf-8")
    return target
