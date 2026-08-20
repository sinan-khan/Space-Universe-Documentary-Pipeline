from __future__ import annotations

from dataclasses import dataclass

from .research.models import ResearchPacket


@dataclass(frozen=True)
class ScriptPlan:
    title: str
    chapters: tuple[str, ...]
    prompt: str


DEFAULT_CHAPTERS = (
    "Hook",
    "Premise",
    "Context",
    "Escalation",
    "Discovery",
    "Implications",
    "Conclusion",
)


def build_script_plan(packet: ResearchPacket, chapters: tuple[str, ...] = DEFAULT_CHAPTERS) -> ScriptPlan:
    """Create a deterministic, citation-aware writing brief.

    This layer does not invent facts. A future LLM adapter receives only this
    research packet and must return narration whose factual assertions map back
    to the supplied claim IDs.
    """
    claim_lines = []
    for claim in packet.claims:
        sources = ", ".join(claim.source_ids) or "UNSUPPORTED"
        claim_lines.append(f"- [{claim.id}] {claim.text} (sources: {sources})")
    evidence = "\n".join(claim_lines) or "- No verified claims available."
    prompt = f"""Write a cinematic but factual space documentary about: {packet.topic}\n\n"
        f"Angle: {packet.angle}\n\n"
        "Use only the supplied evidence for factual assertions. Never invent numbers, discoveries, quotations, dates, or scientific conclusions. "
        "Preserve claim IDs in a machine-readable citation marker such as [claim:c1]. "
        "Use these chapters in order: " + " → ".join(chapters) + "\n\n"
        "Verified evidence:\n" + evidence
    return ScriptPlan(title=packet.topic.strip(), chapters=chapters, prompt=prompt)
