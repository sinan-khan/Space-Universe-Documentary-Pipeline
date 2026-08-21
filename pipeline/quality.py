from __future__ import annotations

from .models import Documentary


class QualityError(ValueError):
    pass


def validate_documentary(doc: Documentary, config: dict) -> list[str]:
    errors: list[str] = []
    quality = config.get("quality", {})
    words = len(doc.script.split())
    if words < quality.get("minimum_script_words", 0):
        errors.append(f"script too short: {words} words")
    if words > quality.get("maximum_script_words", 10**9):
        errors.append(f"script too long: {words} words")
    if not doc.scenes:
        errors.append("timeline has no scenes")
    for scene in doc.scenes:
        if scene.end <= scene.start:
            errors.append(f"invalid timing in {scene.id}")
    if quality.get("require_source_for_factual_claim", False):
        for index, claim in enumerate(doc.claims, start=1):
            if not claim.sources:
                errors.append(f"claim {index} has no source")
    return errors


def assert_publishable(doc: Documentary, config: dict) -> None:
    errors = validate_documentary(doc, config)
    if errors:
        raise QualityError("; ".join(errors))
