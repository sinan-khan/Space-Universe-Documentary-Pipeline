from __future__ import annotations

from pathlib import Path
import json

from .models import Documentary


def write_project_manifest(doc: Documentary, output_dir: str | Path) -> Path:
    """Persist a render-ready manifest; an FFmpeg/MoviePy adapter can consume it."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "documentary.json"
    target.write_text(doc.model_dump_json(indent=2), encoding="utf-8")
    return target


def write_edit_decision_list(doc: Documentary, output_dir: str | Path) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "edit_decision_list.json"
    payload = [{
        "scene_id": scene.id,
        "start": scene.start,
        "end": scene.end,
        "narration": scene.narration,
        "visual_query": scene.visual_query,
    } for scene in doc.scenes]
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target
