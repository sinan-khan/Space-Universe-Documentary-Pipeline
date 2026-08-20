from __future__ import annotations

import os
import subprocess
from pathlib import Path


class PiperTTS:
    """Local Piper command adapter. No cloud API is required."""

    def __init__(self, executable: str | None = None, model: str | None = None):
        self.executable = executable or os.getenv("PIPER_EXECUTABLE", "piper")
        self.model = model or os.getenv("PIPER_MODEL", "")

    def synthesize(self, text: str, output: str | Path) -> Path:
        if not self.model:
            raise RuntimeError("PIPER_MODEL is required")
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [self.executable, "--model", self.model, "--output_file", str(target)]
        try:
            subprocess.run(command, input=text.encode("utf-8"), check=True)
        except FileNotFoundError as exc:
            raise RuntimeError("Piper executable was not found. Install Piper and set PIPER_EXECUTABLE.") from exc
        return target
