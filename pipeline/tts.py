from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import wave


@dataclass(frozen=True)
class AudioResult:
    path: Path
    duration_seconds: float


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_path: str | Path) -> AudioResult:
        raise NotImplementedError


def wav_duration(path: str | Path) -> float:
    with wave.open(str(path), "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        return frames / rate if rate else 0.0


class LocalWavProvider(TTSProvider):
    """Test adapter: validates an existing WAV instead of calling a paid TTS API."""

    def synthesize(self, text: str, output_path: str | Path) -> AudioResult:
        path = Path(output_path)
        if not path.exists():
            raise FileNotFoundError(path)
        return AudioResult(path=path, duration_seconds=wav_duration(path))
