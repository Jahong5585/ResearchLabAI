from dataclasses import dataclass, field


@dataclass
class SynthesisClaim:
    """
    One validated analytical statement derived from multiple
    article summaries.

    The evidence-profile fields describe the methodological composition
    of the supporting records. They are based on metadata and available
    abstracts, not necessarily on complete article texts.
    """

    claim_type: str
    statement: str

    # Article-level support.
    supporting_articles: list[int] = field(
        default_factory=list
    )

    contradicting_articles: list[int] = field(
        default_factory=list
    )

    # General assessment returned by Synthesis Agent.
    confidence: str = "Low"
    rationale: str = ""
    caveats: list[str] = field(
        default_factory=list
    )

    # Methodological composition of supporting evidence.
    supporting_designs: list[str] = field(
        default_factory=list
    )

    # Articles reporting objectively measured outcomes,
    # for example writing scores or pre-test/post-test results.
    objective_evidence_articles: list[int] = field(
        default_factory=list
    )

    # Articles mainly reporting perceptions, attitudes,
    # experiences or self-reported outcomes.
    perception_evidence_articles: list[int] = field(
        default_factory=list
    )

    # Articles synthesizing prior research, such as literature
    # reviews, systematic reviews and meta-analyses.
    review_evidence_articles: list[int] = field(
        default_factory=list
    )

    # Distribution of abstract-level evidence usability.
    #
    # Example:
    # {
    #     "Higher abstract-level evidence usability": 2,
    #     "Moderate abstract-level evidence usability": 3
    # }
    abstract_evidence_levels: dict[str, int] = field(
        default_factory=dict
    )

    # Deterministic weighted-support score.
    #
    # This is not a full risk-of-bias assessment and not a final
    # evaluation of scientific quality.
    quality_weighted_support: float = 0.0

    # Human-readable explanation of the evidence profile.
    evidence_profile_note: str = ""

    @property
    def evidence_count(self) -> int:
        """
        Number of unique supporting articles.
        """

        return len(
            set(
                self.supporting_articles
            )
        )

    @property
    def contradiction_count(self) -> int:
        """
        Number of unique contradicting articles.
        """

        return len(
            set(
                self.contradicting_articles
            )
        )

    @property
    def objective_evidence_count(self) -> int:
        """
        Number of supporting articles with objectively measured outcomes.
        """

        return len(
            set(
                self.objective_evidence_articles
            )
        )

    @property
    def perception_evidence_count(self) -> int:
        """
        Number of supporting articles based mainly on perceptions
        or self-reported experience.
        """

        return len(
            set(
                self.perception_evidence_articles
            )
        )

    @property
    def review_evidence_count(self) -> int:
        """
        Number of supporting review or evidence-synthesis publications.
        """

        return len(
            set(
                self.review_evidence_articles
            )
        )

    @property
    def has_multiple_evidence_types(self) -> bool:
        """
        Whether the claim is supported by more than one evidence type.
        """

        evidence_types = 0

        if self.objective_evidence_articles:
            evidence_types += 1

        if self.perception_evidence_articles:
            evidence_types += 1

        if self.review_evidence_articles:
            evidence_types += 1

        return evidence_types >= 2