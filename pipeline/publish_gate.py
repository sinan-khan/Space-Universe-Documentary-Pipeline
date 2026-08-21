from __future__ import annotations

from pathlib import Path

from .models import Documentary
from .quality import assert_publishable


def assert_ready_for_publish(doc: Documentary, config: dict, required_files: list[str | Path]) -> None:
    """Fail closed unless content quality and required production artifacts exist."""
    assert_publishable(doc, config)
    missing = [str(path) for path in required_files if not Path(path).exists()]
    if missing:
        raise RuntimeError("Missing production artifacts: " + ", ".join(missing))
