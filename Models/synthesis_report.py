from dataclasses import dataclass, field

from Models.synthesis_claim import SynthesisClaim


@dataclass
class SynthesisReport:
    """Validated cross-paper analysis consumed by the Writer agent."""

    overview: str = ""
    claims: list[SynthesisClaim] = field(default_factory=list)
    methodology_patterns: list[str] = field(default_factory=list)
    trends: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recurring_limitations: list[str] = field(default_factory=list)
    aggregate_statistics: dict = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)
