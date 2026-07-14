from __future__ import annotations

import json
from collections import Counter
from typing import Any


class SynthesisContextBuilder:
    """
    Creates structured input for cross-paper synthesis.

    The context contains:

    - structured article summaries;
    - extraction provenance;
    - analytical outline;
    - deterministic comparison matrix.

    The provenance fields distinguish summaries based only on an
    abstract from summaries that also used selected full-text sections.
    """

    COMPARISON_FIELDS = (
        "article_number",

        # Extraction provenance.
        "source_scope",
        "uses_full_text",
        "source_sections",
        "source_text_characters",
        "full_text_source",

        # Study design and evidence characteristics.
        "normalized_design",
        "design_weight",
        "source_type",
        "abstract_completeness_score",
        "abstract_evidence_level",

        # Study characteristics.
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

        # Reporting completeness.
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

        comparison_matrix remains optional for backward compatibility.
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

        provenance_summary = cls._build_provenance_summary(
            comparison_data
        )

        context = {
            "source_boundary": (
                "The records may be based either on bibliographic metadata "
                "and an available abstract or on metadata, abstract and "
                "selected openly accessible full-text sections. Selected "
                "sections do not necessarily represent every page or every "
                "section of the complete publication."
            ),
            "provenance_summary": provenance_summary,
            "outline": outline_data,
            "articles": articles,
            "comparison_matrix": comparison_data,
            "comparison_instructions": {
                "purpose": (
                    "Use the matrix for direct comparison of study designs, "
                    "participants, methods, evaluation metrics, reported "
                    "results and source provenance."
                ),
                "full_text_boundary": (
                    "FULL_TEXT_SECTIONS means that selected extracted "
                    "sections were supplied to Summarizer. It does not mean "
                    "that every part of the complete article was analyzed."
                ),
                "quality_boundary": (
                    "The use of full-text sections does not automatically "
                    "prove that a publication is scientifically stronger "
                    "than an abstract-only record."
                ),
                "missing_data_boundary": (
                    "Missing fields mean only that the information was not "
                    "reported in the source text supplied to the system."
                ),
                "comparison_rule": (
                    "When the same conclusion is supported by both "
                    "FULL_TEXT_SECTIONS and ABSTRACT_ONLY records, this may "
                    "be described as support across different source scopes, "
                    "but only when the supplied evidence genuinely supports "
                    "the same claim."
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

                    # Bibliographic metadata.
                    "title": summary.title,
                    "authors": summary.authors,
                    "year": summary.year,
                    "journal": summary.journal,
                    "doi": summary.doi,

                    # Extraction provenance.
                    "source_scope": getattr(
                        summary,
                        "source_scope",
                        "ABSTRACT_ONLY",
                    ),
                    "source_sections": getattr(
                        summary,
                        "source_sections",
                        [],
                    ),
                    "source_text_characters": getattr(
                        summary,
                        "source_text_characters",
                        0,
                    ),
                    "full_text_source": getattr(
                        summary,
                        "full_text_source",
                        "",
                    ),

                    # Extracted scientific information.
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
                    "problem": summary.problem,
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
        Keep only fields needed for scientific comparison.

        Duplicate bibliographic metadata are excluded to reduce
        context size and model cost.
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

    @staticmethod
    def _build_provenance_summary(
        comparison_data,
    ) -> dict[str, Any]:
        """
        Build corpus-level extraction-provenance statistics.
        """

        scope_counter = Counter()
        section_counter = Counter()
        full_text_source_counter = Counter()

        full_text_article_numbers = []
        abstract_only_article_numbers = []

        for row in comparison_data:
            article_number = row.get(
                "article_number"
            )

            source_scope = str(
                row.get(
                    "source_scope",
                    "ABSTRACT_ONLY",
                )
                or "ABSTRACT_ONLY"
            ).strip()

            scope_counter[source_scope] += 1

            if source_scope == "FULL_TEXT_SECTIONS":
                full_text_article_numbers.append(
                    article_number
                )
            else:
                abstract_only_article_numbers.append(
                    article_number
                )

            source_sections = row.get(
                "source_sections",
                [],
            )

            if isinstance(
                source_sections,
                list,
            ):
                for section_name in source_sections:
                    section_text = str(
                        section_name
                    ).strip()

                    if section_text:
                        section_counter[
                            section_text
                        ] += 1

            full_text_source = str(
                row.get(
                    "full_text_source",
                    "",
                )
                or ""
            ).strip()

            if full_text_source:
                full_text_source_counter[
                    full_text_source
                ] += 1

        return {
            "total_articles": len(
                comparison_data
            ),
            "source_scope_counts": dict(
                scope_counter
            ),
            "full_text_article_numbers": (
                full_text_article_numbers
            ),
            "abstract_only_article_numbers": (
                abstract_only_article_numbers
            ),
            "full_text_section_counts": dict(
                section_counter
            ),
            "full_text_source_counts": dict(
                full_text_source_counter
            ),
            "interpretation_boundary": (
                "These counts describe source availability and extraction "
                "scope. They do not represent final scientific quality."
            ),
        }