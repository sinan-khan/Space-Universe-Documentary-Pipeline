from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class VideoBuildError(RuntimeError):
    pass


def _ffmpeg() -> str:
    binary = shutil.which("ffmpeg")
    if not binary:
        raise VideoBuildError("ffmpeg executable not found")
    return binary


def build_slideshow(images: list[Path], duration: float, output: str | Path, width: int = 1920, height: int = 1080) -> Path:
    """Build a slideshow that is guaranteed to cover the requested narration duration."""
    if not images:
        raise VideoBuildError("no visual assets available")
    if duration <= 0:
        raise VideoBuildError("duration must be positive")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Give the visual timeline a small safety margin. FFmpeg's frame/timebase
    # rounding can otherwise make the concatenated video a few seconds shorter
    # than the measured narration, which then causes -shortest to truncate audio.
    visual_duration = duration + 2.0
    per_image = visual_duration / len(images)
    inputs: list[str] = []
    filters: list[str] = []
    for i, image in enumerate(images):
        inputs += ["-loop", "1", "-t", f"{per_image:.3f}", "-i", str(image)]
        filters.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1,setdar={width}/{height},"
            f"zoompan=z='min(zoom+0.0005,1.08)':d=1:s={width}x{height}:fps=30,"
            f"setsar=1,setpts=PTS-STARTPTS[v{i}]"
        )
    joined = "".join(f"[v{i}]" for i in range(len(images)))
    filters.append(
        f"{joined}concat=n={len(images)}:v=1:a=0,"
        f"tpad=stop_mode=clone:stop_duration=2,"
        f"trim=duration={duration:.3f},setpts=PTS-STARTPTS,"
        f"setsar=1,format=yuv420p[v]"
    )
    command = [
        _ffmpeg(), "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[v]", "-r", "30",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-movflags", "+faststart", str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise VideoBuildError(result.stderr[-5000:])
    return output


def mux_audio(video: str | Path, audio: str | Path, output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        _ffmpeg(), "-y", "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise VideoBuildError(result.stderr[-5000:])
    return output


def render_short(source_video: str | Path, start: float, end: float, output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = max(1.0, min(60.0, end - start))
    filter_graph = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=18:2,setsar=1[bg];"
        "[0:v]scale=1080:608:force_original_aspect_ratio=decrease,setsar=1[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]"
    )
    command = [_ffmpeg(), "-y", "-ss", f"{start:.3f}", "-i", str(source_video), "-t", f"{duration:.3f}", "-filter_complex", filter_graph, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise VideoBuildError(result.stderr[-5000:])
    return output
