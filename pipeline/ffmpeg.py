from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class FFmpegError(RuntimeError):
    pass


def render_with_ffmpeg(input_video: str | Path, narration_audio: str | Path, output_video: str | Path) -> Path:
    """Mux video and narration with FFmpeg; fails closed if FFmpeg is unavailable."""
    binary = shutil.which("ffmpeg")
    if not binary:
        raise FFmpegError("ffmpeg executable not found")
    output = Path(output_video)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [binary, "-y", "-i", str(input_video), "-i", str(narration_audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise FFmpegError(result.stderr[-4000:])
    return output
