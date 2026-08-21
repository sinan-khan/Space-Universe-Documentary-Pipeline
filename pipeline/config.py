from __future__ import annotations

from pathlib import Path
import os
import yaml
from dotenv import load_dotenv


def load_config(path: str | Path) -> dict:
    load_dotenv()
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    data["runtime"] = {
        "output_dir": os.getenv("OUTPUT_DIR", "./output"),
        "environment": os.getenv("APP_ENV", "development"),
    }
    return data
