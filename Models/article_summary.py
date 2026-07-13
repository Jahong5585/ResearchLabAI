from dataclasses import dataclass


@dataclass
class ArticleSummary:

    title: str

    authors: str

    year: int | None

    journal: str

    doi: str

    abstract: str

    problem: str

    methodology: str

    findings: str

    limitations: str

    conclusion: str

    keywords: list[str]

    research_objective: str

    research_questions: str

    study_type: str

    educational_level: str

    country: str

    discipline: str

    participants: str

    dataset: str

    sample_size: str

    study_period: str

    ai_field: str

    ai_models: str

    algorithms: str

    tools: str

    frameworks: str

    evaluation_metrics: str

    results: str

    strengths: str

    weaknesses: str

    practical_implications: str

    future_research: str

    verified_facts: list[str]