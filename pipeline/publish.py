from __future__ import annotations

from dataclasses import dataclass

from .quality_gate import QualityResult


@dataclass(frozen=True)
class PublishDecision:
    allowed: bool
    reasons: tuple[str, ...]


def can_publish(*gates: QualityResult) -> PublishDecision:
    failures = tuple(error for gate in gates if not gate.passed for error in gate.errors)
    return PublishDecision(not failures, failures)
