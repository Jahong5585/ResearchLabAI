import re
from typing import Any


class ComparisonMatrixBuilder:
    """
    Builds a deterministic comparison matrix from ArticleSummary objects.

    The matrix may be based on:

    - bibliographic metadata and an available abstract;
    - metadata, abstract and selected full-text sections.

    It does not evaluate the complete publication unless the relevant
    full-text sections were actually supplied.

    No LLM or paid API is used.
    """

    MISSING_VALUES = {
        "",
        "not specified",
        "not reported in the available abstract",
        "not reported in the abstract",
        "not reported in the supplied source text",
        "none",
        "n/a",
        "unknown",
    }

    CORE_COMPARISON_FIELDS = (
        "research_objective",
        "research_questions",
        "study_type",
        "educational_level",
        "country",
        "discipline",
        "participants",
        "dataset",
        "sample_size",
        "study_period",
        "methodology",
        "evaluation_metrics",
        "results",
        "findings",
        "limitations",
    )

    DESIGN_WEIGHTS = (
        (
            (
                "meta-analysis",
                "meta analysis",
                "meta-analytic",
                "meta analytic",
                "мета-анализ",
                "метааналитический",
                "метааналитическое",
                "метааналитическое исследование",
            ),
            5.0,
            "Meta-analysis",
        ),
        (
            (
                "systematic review",
                "систематический обзор",
            ),
            4.5,
            "Systematic review",
        ),
        (
            (
                "randomized controlled trial",
                "randomised controlled trial",
                "controlled trial",
                "рандомизирован",
            ),
            4.5,
            "Controlled study",
        ),
        (
            (
                "mixed methods",
                "mixed-methods",
                "смешанные методы",
                "смешанный метод",
            ),
            4.0,
            "Mixed-methods study",
        ),
        (
            (
                "experimental study",
                "experiment",
                "pre-test",
                "post-test",
                "pretest",
                "posttest",
                "эксперимент",
            ),
            4.0,
            "Experimental study",
        ),
        (
            (
                "longitudinal",
                "лонгитюд",
            ),
            3.5,
            "Longitudinal study",
        ),
        (
            (
                "quasi-experimental",
                "quasi experimental",
                "квазиэксперимент",
            ),
            3.5,
            "Quasi-experimental study",
        ),
        (
            (
                "survey",
                "questionnaire",
                "опрос",
                "анкет",
            ),
            3.0,
            "Survey study",
        ),
        (
            (
                "qualitative",
                "interview",
                "focus group",
                "thematic analysis",
                "качественное",
                "интервью",
                "фокус-групп",
            ),
            3.0,
            "Qualitative study",
        ),
        (
            (
                "bibliometric",
                "библиометр",
            ),
            2.5,
            "Bibliometric study",
        ),
        (
            (
                "scoping review",
                "rapid review",
                "literature review",
                "обзор литературы",
            ),
            2.5,
            "Review study",
        ),
        (
            (
                "case study",
                "case method",
                "кейс",
            ),
            2.0,
            "Case study",
        ),
        (
            (
                "conceptual",
                "theoretical",
                "теоретичес",
                "концептуаль",
            ),
            1.5,
            "Conceptual study",
        ),
    )

    PREPRINT_MARKERS = {
        "ssrn",
        "osf",
        "arxiv",
        "preprint",
        "medrxiv",
        "biorxiv",
        "research square",
    }

    CONFERENCE_MARKERS = {
        "conference",
        "proceedings",
        "symposium",
        "annual meeting",
        "workshop",
        "конференц",
    }

    @classmethod
    def build(
        cls,
        summaries,
    ) -> list[dict[str, Any]]:
        """
        Build one comparison row for every ArticleSummary.
        """

        matrix = []

        for article_number, summary in enumerate(
            summaries,
            start=1,
        ):
            matrix.append(
                cls._build_row(
                    article_number,
                    summary,
                )
            )

        return matrix

    @classmethod
    def _build_row(
        cls,
        article_number: int,
        summary,
    ) -> dict[str, Any]:
        study_type = cls._value(
            getattr(
                summary,
                "study_type",
                "",
            )
        )

        methodology = cls._value(
            getattr(
                summary,
                "methodology",
                "",
            )
        )

        abstract = cls._value(
            getattr(
                summary,
                "abstract",
                "",
            )
        )

        title = cls._value(
            getattr(
                summary,
                "title",
                "",
            )
        )

        journal = cls._value(
            getattr(
                summary,
                "journal",
                "",
            )
        )

        source_scope = cls._value(
            getattr(
                summary,
                "source_scope",
                "ABSTRACT_ONLY",
            )
        )

        if not source_scope:
            source_scope = "ABSTRACT_ONLY"

        source_sections = cls._list_value(
            getattr(
                summary,
                "source_sections",
                [],
            )
        )

        source_text_characters = cls._to_int(
            getattr(
                summary,
                "source_text_characters",
                0,
            )
        )

        full_text_url = cls._value(
            getattr(
                summary,
                "full_text_url",
                "",
            )
        )

        full_text_source = cls._value(
            getattr(
                summary,
                "full_text_source",
                "",
            )
        )

        uses_full_text = (
            source_scope == "FULL_TEXT_SECTIONS"
            and bool(source_sections)
        )

        design_label, design_weight = cls._detect_design(
            study_type=study_type,
            methodology=methodology,
            title=title,
            abstract=abstract,
        )

        completeness = cls._calculate_completeness(
            summary
        )

        source_type = cls._detect_source_type(
            title=title,
            journal=journal,
            abstract=abstract,
        )

        evidence_level = cls._calculate_abstract_evidence_level(
            design_weight=design_weight,
            completeness_score=completeness["score"],
            source_type=source_type,
        )

        return {
            "article_number": article_number,
            "title": title,
            "authors": cls._value(
                getattr(
                    summary,
                    "authors",
                    "",
                )
            ),
            "year": getattr(
                summary,
                "year",
                None,
            ),
            "journal": journal,
            "doi": cls._value(
                getattr(
                    summary,
                    "doi",
                    "",
                )
            ),

            # Extraction provenance.
            "source_scope": source_scope,
            "uses_full_text": uses_full_text,
            "source_sections": source_sections,
            "source_text_characters": source_text_characters,
            "full_text_url": full_text_url,
            "full_text_source": full_text_source,

            # Study characteristics.
            "research_objective": cls._value(
                getattr(
                    summary,
                    "research_objective",
                    "",
                )
            ),
            "research_questions": cls._value(
                getattr(
                    summary,
                    "research_questions",
                    "",
                )
            ),
            "study_type": study_type,
            "normalized_design": design_label,
            "design_weight": design_weight,
            "educational_level": cls._value(
                getattr(
                    summary,
                    "educational_level",
                    "",
                )
            ),
            "country": cls._value(
                getattr(
                    summary,
                    "country",
                    "",
                )
            ),
            "discipline": cls._value(
                getattr(
                    summary,
                    "discipline",
                    "",
                )
            ),
            "participants": cls._value(
                getattr(
                    summary,
                    "participants",
                    "",
                )
            ),
            "sample_size": cls._value(
                getattr(
                    summary,
                    "sample_size",
                    "",
                )
            ),
            "dataset": cls._value(
                getattr(
                    summary,
                    "dataset",
                    "",
                )
            ),
            "study_period": cls._value(
                getattr(
                    summary,
                    "study_period",
                    "",
                )
            ),
            "ai_field": cls._value(
                getattr(
                    summary,
                    "ai_field",
                    "",
                )
            ),
            "ai_models": cls._value(
                getattr(
                    summary,
                    "ai_models",
                    "",
                )
            ),
            "algorithms": cls._value(
                getattr(
                    summary,
                    "algorithms",
                    "",
                )
            ),
            "tools": cls._value(
                getattr(
                    summary,
                    "tools",
                    "",
                )
            ),
            "frameworks": cls._value(
                getattr(
                    summary,
                    "frameworks",
                    "",
                )
            ),
            "methodology": methodology,
            "evaluation_metrics": cls._value(
                getattr(
                    summary,
                    "evaluation_metrics",
                    "",
                )
            ),
            "results": cls._value(
                getattr(
                    summary,
                    "results",
                    "",
                )
            ),
            "findings": cls._value(
                getattr(
                    summary,
                    "findings",
                    "",
                )
            ),
            "strengths": cls._value(
                getattr(
                    summary,
                    "strengths",
                    "",
                )
            ),
            "weaknesses": cls._value(
                getattr(
                    summary,
                    "weaknesses",
                    "",
                )
            ),
            "limitations": cls._value(
                getattr(
                    summary,
                    "limitations",
                    "",
                )
            ),
            "practical_implications": cls._value(
                getattr(
                    summary,
                    "practical_implications",
                    "",
                )
            ),
            "future_research": cls._value(
                getattr(
                    summary,
                    "future_research",
                    "",
                )
            ),

            # Deterministic comparison indicators.
            "source_type": source_type,
            "abstract_completeness_score": (
                completeness["score"]
            ),
            "reported_core_fields": (
                completeness["reported_fields"]
            ),
            "missing_core_fields": (
                completeness["missing_fields"]
            ),
            "abstract_evidence_level": evidence_level,
        }

    @classmethod
    def _calculate_completeness(
        cls,
        summary,
    ) -> dict[str, Any]:
        reported_fields = []
        missing_fields = []

        for field_name in cls.CORE_COMPARISON_FIELDS:
            value = getattr(
                summary,
                field_name,
                "",
            )

            if cls._is_missing(value):
                missing_fields.append(
                    field_name
                )
            else:
                reported_fields.append(
                    field_name
                )

        total_fields = len(
            cls.CORE_COMPARISON_FIELDS
        )

        score = (
            len(reported_fields)
            / total_fields
            * 100
            if total_fields
            else 0.0
        )

        return {
            "score": round(
                score,
                1,
            ),
            "reported_fields": reported_fields,
            "missing_fields": missing_fields,
        }

    @classmethod
    def _detect_design(
        cls,
        study_type: str,
        methodology: str,
        title: str,
        abstract: str,
    ) -> tuple[str, float]:
        text = " ".join(
            (
                study_type,
                methodology,
                title,
                abstract,
            )
        ).casefold()

        for markers, weight, label in cls.DESIGN_WEIGHTS:
            if any(
                marker in text
                for marker in markers
            ):
                return label, weight

        if (
            cls._is_missing(study_type)
            and cls._is_missing(methodology)
        ):
            return (
                "Not identifiable from supplied source text",
                0.5,
            )

        return (
            "Other reported design",
            1.0,
        )

    @classmethod
    def _detect_source_type(
        cls,
        title: str,
        journal: str,
        abstract: str,
    ) -> str:
        text = " ".join(
            (
                title,
                journal,
                abstract,
            )
        ).casefold()

        if any(
            marker in text
            for marker in cls.PREPRINT_MARKERS
        ):
            return "Preprint or repository record"

        if any(
            marker in text
            for marker in cls.CONFERENCE_MARKERS
        ):
            return "Conference material"

        if journal:
            return "Journal publication"

        return "Source type not identifiable"

    @classmethod
    def _calculate_abstract_evidence_level(
        cls,
        design_weight: float,
        completeness_score: float,
        source_type: str,
    ) -> str:
        """
        Estimate evidence usability from supplied source information.

        The field name remains abstract_evidence_level for backward
        compatibility with existing project components.

        This is not a full risk-of-bias or article-quality assessment.
        """

        score = design_weight

        if completeness_score >= 75:
            score += 2.0
        elif completeness_score >= 50:
            score += 1.0
        elif completeness_score < 25:
            score -= 0.5

        if source_type == "Journal publication":
            score += 0.5
        elif source_type == "Conference material":
            score -= 0.5
        elif source_type == "Preprint or repository record":
            score -= 1.0

        if score >= 6.0:
            return "Higher abstract-level evidence usability"

        if score >= 3.5:
            return "Moderate abstract-level evidence usability"

        return "Limited abstract-level evidence usability"

    @classmethod
    def _is_missing(
        cls,
        value: Any,
    ) -> bool:
        if value is None:
            return True

        if isinstance(
            value,
            list,
        ):
            return len(value) == 0

        text = cls._value(
            value
        ).casefold()

        return text in cls.MISSING_VALUES

    @staticmethod
    def _list_value(
        value: Any,
    ) -> list[str]:
        if value is None:
            return []

        if isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):
            result = []

            for item in value:
                text = str(item).strip()

                if (
                    text
                    and text not in result
                ):
                    result.append(text)

            return result

        text = str(value).strip()

        if not text:
            return []

        return [text]

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int:
        try:
            return int(
                value or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _value(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        if isinstance(
            value,
            list,
        ):
            return "; ".join(
                str(item).strip()
                for item in value
                if str(item).strip()
            )

        return str(
            value
        ).strip()