from dataclasses import dataclass, field


@dataclass
class ArticleSummary:
    """
    Structured scientific information extracted from one publication.

    The source-provenance fields show whether the extraction was based
    only on metadata and an abstract or also on selected full-text sections.

    All fields have safe defaults for backward compatibility.
    """

    # Bibliographic metadata.
    title: str = ""
    authors: str = ""
    year: int | None = None
    journal: str = ""
    doi: str = ""
    abstract: str = ""

    # Extraction provenance.
    #
    # Allowed values:
    # ABSTRACT_ONLY
    # FULL_TEXT_SECTIONS
    source_scope: str = "ABSTRACT_ONLY"

    # Names of full-text sections supplied to Summarizer.
    #
    # Example:
    # [
    #     "methodology",
    #     "results",
    #     "limitations",
    #     "conclusion"
    # ]
    source_sections: list[str] = field(
        default_factory=list
    )

    # Number of source-text characters supplied to Summarizer.
    source_text_characters: int = 0

    # Open full-text location and provider, when available.
    full_text_url: str = ""
    full_text_source: str = ""

    # Primary structured extraction.
    problem: str = "Not specified"
    methodology: str = "Not specified"
    findings: str = "Not specified"
    limitations: str = "Not specified"
    conclusion: str = "Not specified"

    keywords: list[str] = field(
        default_factory=list
    )

    # Detailed study characteristics.
    research_objective: str = "Not specified"
    research_questions: str = "Not specified"
    study_type: str = "Not specified"
    educational_level: str = "Not specified"
    country: str = "Not specified"
    discipline: str = "Not specified"
    participants: str = "Not specified"
    dataset: str = "Not specified"
    sample_size: str = "Not specified"
    study_period: str = "Not specified"

    # Artificial-intelligence characteristics.
    ai_field: str = "Not specified"
    ai_models: str = "Not specified"
    algorithms: str = "Not specified"
    tools: str = "Not specified"
    frameworks: str = "Not specified"

    # Methods and findings.
    evaluation_metrics: str = "Not specified"
    results: str = "Not specified"
    strengths: str = "Not specified"
    weaknesses: str = "Not specified"
    practical_implications: str = "Not specified"
    future_research: str = "Not specified"

    # Facts directly supported by the supplied source text.
    verified_facts: list[str] = field(
        default_factory=list
    )

    @property
    def uses_full_text(self) -> bool:
        """
        Whether selected full-text sections were used for extraction.
        """

        return (
            self.source_scope == "FULL_TEXT_SECTIONS"
            and bool(self.source_sections)
        )

    @property
    def source_description(self) -> str:
        """
        Human-readable extraction-source description.
        """

        if self.uses_full_text:
            sections = ", ".join(
                self.source_sections
            )

            return (
                "Metadata, abstract and selected full-text sections: "
                f"{sections}"
            )

        return "Bibliographic metadata and available abstract"