from dataclasses import dataclass, field


@dataclass
class SynthesisClaim:
    """One analytical statement derived from multiple article summaries."""

    claim_type: str
    statement: str
    supporting_articles: list[int] = field(default_factory=list)
    contradicting_articles: list[int] = field(default_factory=list)
    confidence: str = "Low"
    rationale: str = ""
    caveats: list[str] = field(default_factory=list)

    @property
    def evidence_count(self) -> int:
        return len(set(self.supporting_articles))
