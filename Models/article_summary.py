from dataclasses import dataclass, field


@dataclass
class ArticleSummary:
    """Structured extraction produced for one scientific publication.

    All fields have safe defaults so the model remains backward compatible
    with older tests and partially populated records.
    """

    title: str = ""
    authors: str = ""
    year: int | None = None
    journal: str = ""
    doi: str = ""
    abstract: str = ""

    problem: str = "Not specified"
    methodology: str = "Not specified"
    findings: str = "Not specified"
    limitations: str = "Not specified"
    conclusion: str = "Not specified"
    keywords: list[str] = field(default_factory=list)

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
    ai_field: str = "Not specified"
    ai_models: str = "Not specified"
    algorithms: str = "Not specified"
    tools: str = "Not specified"
    frameworks: str = "Not specified"
    evaluation_metrics: str = "Not specified"
    results: str = "Not specified"
    strengths: str = "Not specified"
    weaknesses: str = "Not specified"
    practical_implications: str = "Not specified"
    future_research: str = "Not specified"
    verified_facts: list[str] = field(default_factory=list)
