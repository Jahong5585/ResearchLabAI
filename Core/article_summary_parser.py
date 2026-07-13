from __future__ import annotations

from typing import Any

from Core.json_parser import parse_json
from Models.article_summary import ArticleSummary


class ArticleSummaryParser:
    """Parse structured LLM output into ArticleSummary.

    JSON is the primary format. A legacy section parser is retained so older
    model responses do not break the workflow during migration.
    """

    FIELD_MAP = {
        "Problem": "problem",
        "Methodology": "methodology",
        "Findings": "findings",
        "Limitations": "limitations",
        "Conclusion": "conclusion",
        "Keywords": "keywords",
        "ResearchObjective": "research_objective",
        "ResearchQuestions": "research_questions",
        "StudyType": "study_type",
        "EducationalLevel": "educational_level",
        "Country": "country",
        "Discipline": "discipline",
        "Participants": "participants",
        "Dataset": "dataset",
        "SampleSize": "sample_size",
        "StudyPeriod": "study_period",
        "AIField": "ai_field",
        "AIModels": "ai_models",
        "Algorithms": "algorithms",
        "Tools": "tools",
        "Frameworks": "frameworks",
        "EvaluationMetrics": "evaluation_metrics",
        "Results": "results",
        "Strengths": "strengths",
        "Weaknesses": "weaknesses",
        "PracticalImplications": "practical_implications",
        "FutureResearch": "future_research",
        "VerifiedFacts": "verified_facts",
    }

    @classmethod
    def parse(cls, answer: str, paper) -> ArticleSummary:
        data = cls._parse_json(answer)

        if data is None:
            data = cls._parse_legacy_sections(answer)

        kwargs: dict[str, Any] = {
            "title": paper.title,
            "authors": ", ".join(paper.authors),
            "year": paper.year,
            "journal": paper.journal,
            "doi": paper.doi,
            "abstract": paper.abstract,
        }

        for external_name, internal_name in cls.FIELD_MAP.items():
            value = data.get(external_name, "Not specified")

            if internal_name == "keywords":
                kwargs[internal_name] = cls._as_list(value)
            elif internal_name == "verified_facts":
                kwargs[internal_name] = cls._as_fact_list(value)
            else:
                kwargs[internal_name] = cls._as_text(value)

        return ArticleSummary(**kwargs)

    @staticmethod
    def _parse_json(answer: str) -> dict[str, Any] | None:
        try:
            parsed = parse_json(answer)
        except (ValueError, TypeError):
            return None

        return parsed if isinstance(parsed, dict) else None

    @staticmethod
    def _parse_legacy_sections(answer: str) -> dict[str, Any]:
        sections: dict[str, str] = {}
        current: str | None = None

        for raw_line in answer.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            if line.endswith(":"):
                current = line[:-1].strip()
                sections[current] = ""
                continue

            if current:
                separator = "\n" if current == "VerifiedFacts" else " "
                sections[current] += separator + line

        return sections

    @staticmethod
    def _as_text(value: Any) -> str:
        if value is None:
            return "Not specified"

        if isinstance(value, list):
            text = "; ".join(str(item).strip() for item in value if str(item).strip())
        elif isinstance(value, dict):
            text = "; ".join(f"{key}: {item}" for key, item in value.items())
        else:
            text = str(value).strip()

        return text or "Not specified"

    @staticmethod
    def _as_list(value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            items = value
        else:
            items = str(value).replace(";", ",").split(",")

        return [
            str(item).strip(" -\t\n")
            for item in items
            if str(item).strip(" -\t\n")
            and str(item).strip().lower() != "not specified"
        ]

    @classmethod
    def _as_fact_list(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, list):
            items = value
        else:
            items = str(value).splitlines()

        facts = []

        for item in items:
            fact = str(item).strip(" -•\t\n")

            if not fact or fact.lower() == "not specified":
                continue

            facts.append(fact)

        return facts
