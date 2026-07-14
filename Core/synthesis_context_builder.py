from __future__ import annotations

import json
from typing import Any


class SynthesisContextBuilder:
    """
    Creates structured, numbered input for cross-paper synthesis.

    The context contains:

    - structured article summaries;
    - analytical outline;
    - deterministic comparison matrix.

    Comparison Matrix is produced without an additional LLM call.
    """

    COMPARISON_FIELDS = (
        "article_number",
        "normalized_design",
        "design_weight",
        "source_type",
        "abstract_completeness_score",
        "abstract_evidence_level",
        "educational_level",
        "country",
        "discipline",
        "participants",
        "sample_size",
        "study_period",
        "methodology",
        "evaluation_metrics",
        "results",
        "findings",
        "limitations",
        "reported_core_fields",
        "missing_core_fields",
    )

    @classmethod
    def build(
        cls,
        article_summaries,
        outline=None,
        comparison_matrix=None,
    ) -> str:
        """
        Build JSON context for Synthesis Agent.

        comparison_matrix is optional to preserve compatibility
        with older calls and tests.
        """

        articles = cls._build_articles(
            article_summaries
        )

        outline_data = cls._build_outline(
            outline
        )

        comparison_data = cls._build_comparison_matrix(
            comparison_matrix
        )

        context = {
            "source_boundary": (
                "The records are based on bibliographic metadata "
                "and available abstracts, not necessarily on full texts."
            ),
            "outline": outline_data,
            "articles": articles,
            "comparison_matrix": comparison_data,
            "comparison_instructions": {
                "purpose": (
                    "Use the matrix for direct comparison of study "
                    "designs, populations, methods, reported results "
                    "and abstract-level evidence usability."
                ),
                "quality_boundary": (
                    "abstract_evidence_level is not a full article-quality "
                    "or risk-of-bias assessment."
                ),
                "missing_data_boundary": (
                    "Missing fields mean only that information was not "
                    "reported in the available metadata or abstract."
                ),
            },
        }

        return json.dumps(
            context,
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def _build_articles(
        article_summaries,
    ) -> list[dict[str, Any]]:
        articles = []

        for number, summary in enumerate(
            article_summaries,
            start=1,
        ):
            articles.append(
                {
                    "article_number": number,
                    "title": summary.title,
                    "authors": summary.authors,
                    "year": summary.year,
                    "journal": summary.journal,
                    "doi": summary.doi,
                    "keywords": summary.keywords,
                    "research_objective": (
                        summary.research_objective
                    ),
                    "research_questions": (
                        summary.research_questions
                    ),
                    "study_type": summary.study_type,
                    "educational_level": (
                        summary.educational_level
                    ),
                    "country": summary.country,
                    "discipline": summary.discipline,
                    "participants": summary.participants,
                    "dataset": summary.dataset,
                    "sample_size": summary.sample_size,
                    "study_period": summary.study_period,
                    "ai_field": summary.ai_field,
                    "ai_models": summary.ai_models,
                    "algorithms": summary.algorithms,
                    "tools": summary.tools,
                    "frameworks": summary.frameworks,
                    "methodology": summary.methodology,
                    "evaluation_metrics": (
                        summary.evaluation_metrics
                    ),
                    "results": summary.results,
                    "findings": summary.findings,
                    "strengths": summary.strengths,
                    "weaknesses": summary.weaknesses,
                    "limitations": summary.limitations,
                    "practical_implications": (
                        summary.practical_implications
                    ),
                    "future_research": (
                        summary.future_research
                    ),
                    "conclusion": summary.conclusion,
                    "verified_facts": (
                        summary.verified_facts
                    ),
                }
            )

        return articles

    @staticmethod
    def _build_outline(
        outline,
    ) -> list[dict[str, str]]:
        outline_data = []

        for section in outline or []:
            outline_data.append(
                {
                    "title": section.title,
                    "description": section.description,
                }
            )

        return outline_data

    @classmethod
    def _build_comparison_matrix(
        cls,
        comparison_matrix,
    ) -> list[dict[str, Any]]:
        """
        Keep only fields useful for cross-paper comparison.

        This avoids repeating the complete ArticleSummary objects
        and reduces context size and model cost.
        """

        comparison_data = []

        for raw_row in comparison_matrix or []:
            if not isinstance(
                raw_row,
                dict,
            ):
                continue

            row = {}

            for field_name in cls.COMPARISON_FIELDS:
                if field_name in raw_row:
                    row[field_name] = raw_row[
                        field_name
                    ]

            comparison_data.append(
                row
            )

        return comparison_data