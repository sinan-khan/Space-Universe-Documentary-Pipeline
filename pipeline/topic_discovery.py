from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    title: str
    angle: str
    evergreen: bool = True


DEFAULT_TOPICS = (
    Topic("What Happens When a Star Dies?", "Follow stellar death from red giant to remnant."),
    Topic("Inside a Black Hole", "Explain horizons, tides and what physics can actually say."),
    Topic("The Search for a Habitable World", "Explain how astronomers identify potentially habitable exoplanets."),
    Topic("How the Universe Began", "Build an accessible timeline from the early universe to galaxies."),
    Topic("The Strange Worlds of Our Solar System", "Compare the most unusual planets and moons."),
    Topic("What Happens to the Sun Next?", "Trace the Sun's future using established stellar evolution."),
)


def discover(limit: int = 6) -> list[Topic]:
    """Return deterministic starter topics until a trend/research scorer is connected."""
    if limit < 1:
        return []
    return list(DEFAULT_TOPICS[:limit])
