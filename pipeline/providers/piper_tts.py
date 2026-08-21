from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class PiperTTSProvider:
    """Local Piper executable adapter. No cloud key or subscription required."""

    name = "piper"

    def __init__(self, executable: str | None = None, model: str | None = None):
        self.executable = executable or os.getenv("PIPER_EXECUTABLE", "piper")
        self.model = model or os.getenv("PIPER_MODEL", "")

    def available(self) -> bool:
        return shutil.which(self.executable) is not None

    def synthesize(self, text: str, output_path: str | Path) -> Path:
        if not self.available():
            raise RuntimeError("Piper executable not found. Install Piper and set PIPER_EXECUTABLE if needed.")
        if not self.model:
            raise RuntimeError("PIPER_MODEL must point to a downloaded Piper voice model.")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [self.executable, "--model", self.model, "--output_file", str(output)],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "Piper TTS failed")
        return output
