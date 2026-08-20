from __future__ import annotations

from dataclasses import dataclass

from .research.models import ResearchPacket


@dataclass(frozen=True)
class QualityResult:
    passed: bool
    errors: tuple[str, ...]


def research_gate(packet: ResearchPacket) -> QualityResult:
    errors: list[str] = []
    if not packet.claims:
        errors.append("No verified claims were produced.")
    if not packet.sources:
        errors.append("No sources were recorded.")
    if any(claim.needs_review for claim in packet.claims):
        errors.append("At least one claim requires review.")
    return QualityResult(not errors, tuple(errors))
