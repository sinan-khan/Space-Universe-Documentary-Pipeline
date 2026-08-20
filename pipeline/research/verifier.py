from __future__ import annotations

from dataclasses import dataclass

from .models import Claim, ResearchPacket


@dataclass(frozen=True)
class VerificationResult:
    packet: ResearchPacket
    errors: tuple[str, ...]


def verify_packet(packet: ResearchPacket, min_confidence: float = 0.85) -> VerificationResult:
    """Validate research structure without pretending source presence proves truth."""
    errors: list[str] = []
    source_ids = {source.id for source in packet.sources}
    verified: list[Claim] = []

    for claim in packet.claims:
        missing = [sid for sid in claim.source_ids if sid not in source_ids]
        if missing:
            errors.append(f"claim {claim.id} references missing sources: {', '.join(missing)}")
        if claim.confidence < min_confidence:
            errors.append(f"claim {claim.id} confidence below threshold")
        if claim.needs_review:
            errors.append(f"claim {claim.id} requires review")
        if not claim.source_ids:
            errors.append(f"claim {claim.id} has no supporting source")
        if not missing and claim.confidence >= min_confidence and not claim.needs_review:
            verified.append(claim)

    if packet.claims and not verified:
        errors.append("no claims passed the verification gate")

    return VerificationResult(packet=packet, errors=tuple(errors))
