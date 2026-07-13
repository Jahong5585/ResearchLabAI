from dataclasses import dataclass, field


@dataclass
class Evidence:

    # Основная тема
    topic: str

    # Статьи
    supporting_articles: list = field(default_factory=list)

    # Общие сведения
    common_findings: list[str] = field(default_factory=list)
    common_limitations: list[str] = field(default_factory=list)

    # Новые агрегированные данные
    research_objectives: list[str] = field(default_factory=list)

    methodologies: list[str] = field(default_factory=list)

    study_types: list[str] = field(default_factory=list)

    educational_levels: list[str] = field(default_factory=list)

    countries: list[str] = field(default_factory=list)

    disciplines: list[str] = field(default_factory=list)

    participants: list[str] = field(default_factory=list)

    datasets: list[str] = field(default_factory=list)

    sample_sizes: list[str] = field(default_factory=list)

    study_periods: list[str] = field(default_factory=list)

    ai_fields: list[str] = field(default_factory=list)

    ai_models: list[str] = field(default_factory=list)

    algorithms: list[str] = field(default_factory=list)

    tools: list[str] = field(default_factory=list)

    frameworks: list[str] = field(default_factory=list)

    evaluation_metrics: list[str] = field(default_factory=list)

    results: list[str] = field(default_factory=list)

    strengths: list[str] = field(default_factory=list)

    weaknesses: list[str] = field(default_factory=list)

    practical_implications: list[str] = field(default_factory=list)

    future_research: list[str] = field(default_factory=list)

    verified_facts: list[str] = field(default_factory=list)

    confidence: str = "Low"