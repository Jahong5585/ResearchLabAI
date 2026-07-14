from __future__ import annotations

from collections import Counter
from typing import Any

from Models.synthesis_claim import SynthesisClaim
from Models.synthesis_report import SynthesisReport


class SynthesisEngine:
    """
    Deterministic helpers and validation for cross-paper synthesis.

    Evidence profiles are derived from the Comparison Matrix without
    additional LLM calls.

    All quality-related indicators describe only the usability of
    metadata and available abstracts. They are not full risk-of-bias
    assessments and not final evaluations of complete articles.
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

    ALLOWED_CLAIM_TYPES = {
        "CONSENSUS",
        "MAJORITY_PATTERN",
        "MINORITY_PATTERN",
        "CONTRADICTION",
        "METHODOLOGICAL_DIFFERENCE",
        "TEMPORAL_TREND",
        "GEOGRAPHICAL_DIFFERENCE",
        "POPULATION_DIFFERENCE",
        "EVIDENCE_GAP",
        "LIMITATION_PATTERN",
        "REPLICATION_PATTERN",
    }

    ABSTRACT_EVIDENCE_MULTIPLIERS = {
        "higher abstract-level evidence usability": 1.20,
        "moderate abstract-level evidence usability": 1.00,
        "limited abstract-level evidence usability": 0.70,
    }

    REVIEW_MARKERS = (
        "meta-analysis",
        "meta analysis",
        "мета-анализ",
        "systematic review",
        "систематический обзор",
        "scoping review",
        "rapid review",
        "literature review",
        "обзор литературы",
        "review study",
    )

    OBJECTIVE_DESIGN_MARKERS = (
        "experimental study",
        "controlled study",
        "quasi-experimental study",
        "mixed-methods study",
        "longitudinal study",
        "experiment",
        "experimental",
        "intervention",
        "controlled",
        "quasi-experimental",
        "pre-test",
        "post-test",
        "pretest",
        "posttest",
        "эксперимент",
        "интервенцион",
        "контрольн",
        "предтест",
        "посттест",
    )

    OBJECTIVE_MEASURE_MARKERS = (
        "writing score",
        "writing performance",
        "academic writing performance",
        "writing quality",
        "test score",
        "assessment score",
        "pre-test",
        "post-test",
        "pretest",
        "posttest",
        "effect size",
        "regression",
        "t-test",
        "anova",
        "statistical significance",
        "grammar accuracy",
        "coherence score",
        "vocabulary score",
        "оценка письма",
        "качество письма",
        "результаты теста",
        "статистическ",
        "грамматическ точност",
        "связност",
    )

    PERCEPTION_DESIGN_MARKERS = (
        "qualitative study",
        "survey study",
        "mixed-methods study",
        "qualitative",
        "survey",
        "questionnaire",
        "interview",
        "focus group",
        "thematic analysis",
        "self-report",
        "качествен",
        "опрос",
        "анкет",
        "интервью",
        "фокус-груп",
        "самоотч",
    )

    PERCEPTION_CONTENT_MARKERS = (
        "perception",
        "perceptions",
        "attitude",
        "attitudes",
        "experience",
        "experiences",
        "motivation",
        "self-efficacy",
        "acceptance",
        "satisfaction",
        "dependency",
        "confidence",
        "student views",
        "student opinion",
        "восприят",
        "отношение",
        "опыт студент",
        "мотивац",
        "самоэффектив",
        "удовлетвор",
        "зависимост",
        "мнение студент",
    )

    @classmethod
    def build_statistics(
        cls,
        summaries,
    ) -> dict[str, Any]:
        return {
            "total_articles": len(summaries),
            "publication_years": cls._count_values(
                str(summary.year) if summary.year else ""
                for summary in summaries
            ),
            "study_types": cls._count_values(
                summary.study_type
                for summary in summaries
            ),
            "methodologies": cls._count_values(
                summary.methodology
                for summary in summaries
            ),
            "countries": cls._count_values(
                summary.country
                for summary in summaries
            ),
            "educational_levels": cls._count_values(
                summary.educational_level
                for summary in summaries
            ),
            "disciplines": cls._count_values(
                summary.discipline
                for summary in summaries
            ),
            "ai_fields": cls._count_values(
                summary.ai_field
                for summary in summaries
            ),
            "ai_models": cls._count_values(
                summary.ai_models
                for summary in summaries
            ),
        }

    @classmethod
    def from_llm_data(
        cls,
        data: dict[str, Any],
        summaries,
        comparison_matrix=None,
    ) -> SynthesisReport:
        """
        Convert the LLM JSON response into a validated SynthesisReport.

        comparison_matrix is optional for backward compatibility.
        """

        report = SynthesisReport(
            overview=cls._text(
                data.get("overview")
            ),
            methodology_patterns=cls._string_list(
                data.get("methodology_patterns")
            ),
            trends=cls._string_list(
                data.get("trends")
            ),
            contradictions=cls._string_list(
                data.get("contradictions")
            ),
            gaps=cls._string_list(
                data.get("gaps")
            ),
            recurring_limitations=cls._string_list(
                data.get("recurring_limitations")
            ),
            aggregate_statistics=cls.build_statistics(
                summaries
            ),
        )

        raw_claims = data.get(
            "claims",
            [],
        )

        if not isinstance(
            raw_claims,
            list,
        ):
            raw_claims = []

        for raw_claim in raw_claims:
            if not isinstance(
                raw_claim,
                dict,
            ):
                continue

            claim_type = cls._text(
                raw_claim.get("claim_type")
            ).upper()

            if claim_type not in cls.ALLOWED_CLAIM_TYPES:
                claim_type = "MAJORITY_PATTERN"

            claim = SynthesisClaim(
                claim_type=claim_type,
                statement=cls._text(
                    raw_claim.get("statement")
                ),
                supporting_articles=cls._article_numbers(
                    raw_claim.get("supporting_articles")
                ),
                contradicting_articles=cls._article_numbers(
                    raw_claim.get("contradicting_articles")
                ),
                confidence=cls._normalize_confidence(
                    raw_claim.get("confidence")
                ),
                rationale=cls._text(
                    raw_claim.get("rationale")
                ),
                caveats=cls._string_list(
                    raw_claim.get("caveats")
                ),
            )

            if claim.statement:
                report.claims.append(
                    claim
                )

        if comparison_matrix:
            cls.attach_evidence_profiles(
                report,
                comparison_matrix,
            )

        report.validation_errors = cls.validate(
            report,
            len(summaries),
        )

        return report

    @classmethod
    def attach_evidence_profiles(
        cls,
        report: SynthesisReport,
        comparison_matrix,
    ) -> SynthesisReport:
        """
        Attach deterministic evidence profiles to all synthesis claims.
        """

        matrix_index = cls._index_comparison_matrix(
            comparison_matrix
        )

        for claim in report.claims:
            cls._populate_claim_evidence_profile(
                claim,
                matrix_index,
            )

        return report

    @classmethod
    def _index_comparison_matrix(
        cls,
        comparison_matrix,
    ) -> dict[int, dict[str, Any]]:
        matrix_index = {}

        for row in comparison_matrix or []:
            if not isinstance(
                row,
                dict,
            ):
                continue

            article_number = cls._to_int(
                row.get("article_number")
            )

            if article_number <= 0:
                continue

            matrix_index[article_number] = row

        return matrix_index

    @classmethod
    def _populate_claim_evidence_profile(
        cls,
        claim: SynthesisClaim,
        matrix_index: dict[int, dict[str, Any]],
    ) -> None:
        supporting_designs = []
        objective_articles = []
        perception_articles = []
        review_articles = []
        evidence_levels = Counter()

        weighted_support = 0.0

        for article_number in claim.supporting_articles:
            row = matrix_index.get(
                article_number
            )

            if row is None:
                continue

            design = cls._text(
                row.get("normalized_design")
            )

            if (
                not cls._is_missing(design)
                and design not in supporting_designs
            ):
                supporting_designs.append(
                    design
                )

            evidence_level = cls._text(
                row.get("abstract_evidence_level")
            )

            if not cls._is_missing(
                evidence_level
            ):
                evidence_levels[
                    evidence_level
                ] += 1

            design_weight = cls._to_float(
                row.get("design_weight"),
                default=1.0,
            )

            evidence_multiplier = (
                cls.ABSTRACT_EVIDENCE_MULTIPLIERS.get(
                    evidence_level.casefold(),
                    1.0,
                )
            )

            weighted_support += (
                max(
                    design_weight,
                    0.0,
                )
                * evidence_multiplier
            )

            if cls._is_review_evidence(
                row
            ):
                review_articles.append(
                    article_number
                )

            if cls._is_objective_evidence(
                row
            ):
                objective_articles.append(
                    article_number
                )

            if cls._is_perception_evidence(
                row
            ):
                perception_articles.append(
                    article_number
                )

        claim.supporting_designs = (
            cls._unique_strings(
                supporting_designs
            )
        )

        claim.objective_evidence_articles = (
            cls._unique_numbers(
                objective_articles
            )
        )

        claim.perception_evidence_articles = (
            cls._unique_numbers(
                perception_articles
            )
        )

        claim.review_evidence_articles = (
            cls._unique_numbers(
                review_articles
            )
        )

        claim.abstract_evidence_levels = dict(
            evidence_levels
        )

        claim.quality_weighted_support = round(
            weighted_support,
            2,
        )

        claim.evidence_profile_note = (
            cls._build_evidence_profile_note(
                claim
            )
        )

    @classmethod
    def _is_review_evidence(
        cls,
        row: dict[str, Any],
    ) -> bool:
        text = cls._row_text(
            row,
            (
                "normalized_design",
                "study_type",
                "methodology",
                "title",
                "findings",
            ),
        )

        return any(
            marker in text
            for marker in cls.REVIEW_MARKERS
        )

    @classmethod
    def _is_objective_evidence(
        cls,
        row: dict[str, Any],
    ) -> bool:
        design_text = cls._row_text(
            row,
            (
                "normalized_design",
                "study_type",
                "methodology",
            ),
        )

        measure_text = cls._row_text(
            row,
            (
                "evaluation_metrics",
                "results",
                "findings",
                "methodology",
            ),
        )

        has_objective_design = any(
            marker in design_text
            for marker in cls.OBJECTIVE_DESIGN_MARKERS
        )

        has_objective_measure = any(
            marker in measure_text
            for marker in cls.OBJECTIVE_MEASURE_MARKERS
        )

        return (
            has_objective_design
            and has_objective_measure
        )

    @classmethod
    def _is_perception_evidence(
        cls,
        row: dict[str, Any],
    ) -> bool:
        design_text = cls._row_text(
            row,
            (
                "normalized_design",
                "study_type",
                "methodology",
            ),
        )

        content_text = cls._row_text(
            row,
            (
                "participants",
                "evaluation_metrics",
                "results",
                "findings",
                "methodology",
            ),
        )

        has_perception_design = any(
            marker in design_text
            for marker in cls.PERCEPTION_DESIGN_MARKERS
        )

        has_perception_content = any(
            marker in content_text
            for marker in cls.PERCEPTION_CONTENT_MARKERS
        )

        return (
            has_perception_design
            or has_perception_content
        )

    @classmethod
    def _build_evidence_profile_note(
        cls,
        claim: SynthesisClaim,
    ) -> str:
        parts = [
            (
                f"Supported by {claim.evidence_count} "
                f"unique article(s)."
            )
        ]

        if claim.supporting_designs:
            parts.append(
                "Supporting designs: "
                + ", ".join(
                    claim.supporting_designs
                )
                + "."
            )

        parts.append(
            (
                "Objective evidence records: "
                f"{claim.objective_evidence_count}; "
                "perception or self-report records: "
                f"{claim.perception_evidence_count}; "
                "review or synthesis records: "
                f"{claim.review_evidence_count}."
            )
        )

        if claim.abstract_evidence_levels:
            level_text = ", ".join(
                f"{level}: {count}"
                for level, count
                in claim.abstract_evidence_levels.items()
            )

            parts.append(
                "Abstract-level evidence usability: "
                + level_text
                + "."
            )

        parts.append(
            (
                "Weighted support score: "
                f"{claim.quality_weighted_support}. "
                "This score is based on study design and abstract-level "
                "information usability; it is not a full risk-of-bias "
                "or scientific-quality assessment."
            )
        )

        return " ".join(
            parts
        )

    @classmethod
    def _row_text(
        cls,
        row: dict[str, Any],
        field_names,
    ) -> str:
        values = []

        for field_name in field_names:
            value = row.get(
                field_name
            )

            if cls._is_missing(
                value
            ):
                continue

            values.append(
                cls._text(
                    value
                )
            )

        return " ".join(
            values
        ).casefold()

    @classmethod
    def fallback(
        cls,
        summaries,
        comparison_matrix=None,
    ) -> SynthesisReport:
        statistics = cls.build_statistics(
            summaries
        )

        report = SynthesisReport(
            overview=(
                f"The corpus contains {len(summaries)} articles. "
                "Cross-paper LLM synthesis was unavailable, so only "
                "deterministic aggregate patterns are reported."
            ),
            aggregate_statistics=statistics,
        )

        study_types = statistics.get(
            "study_types",
            {},
        )

        methodologies = statistics.get(
            "methodologies",
            {},
        )

        if study_types:
            value, count = next(
                iter(
                    study_types.items()
                )
            )

            report.methodology_patterns.append(
                f"The most frequently recorded study type is "
                f"'{value}' ({count} articles)."
            )

        if methodologies:
            value, count = next(
                iter(
                    methodologies.items()
                )
            )

            report.methodology_patterns.append(
                f"The most frequently recorded methodology is "
                f"'{value}' ({count} articles)."
            )

        limitations = cls._count_values(
            summary.limitations
            for summary in summaries
        )

        for limitation, count in list(
            limitations.items()
        )[:5]:
            if count >= 2:
                report.recurring_limitations.append(
                    f"Recorded in {count} articles: "
                    f"{limitation}"
                )

        return report

    @classmethod
    def validate(
        cls,
        report: SynthesisReport,
        article_count: int,
    ) -> list[str]:
        errors = []

        for index, claim in enumerate(
            report.claims,
            start=1,
        ):
            if not claim.supporting_articles:
                errors.append(
                    f"Claim {index} has no supporting articles."
                )

            for article_number in (
                claim.supporting_articles
                + claim.contradicting_articles
            ):
                if (
                    article_number < 1
                    or article_number > article_count
                ):
                    errors.append(
                        f"Claim {index} references missing "
                        f"ARTICLE {article_number}."
                    )

            overlap = (
                set(
                    claim.supporting_articles
                )
                & set(
                    claim.contradicting_articles
                )
            )

            if overlap:
                errors.append(
                    f"Claim {index} uses the same articles "
                    f"as support and contradiction: "
                    f"{sorted(overlap)}."
                )

            profile_article_numbers = (
                claim.objective_evidence_articles
                + claim.perception_evidence_articles
                + claim.review_evidence_articles
            )

            unsupported_profile_numbers = (
                set(
                    profile_article_numbers
                )
                - set(
                    claim.supporting_articles
                )
            )

            if unsupported_profile_numbers:
                errors.append(
                    f"Claim {index} evidence profile references "
                    f"articles outside supporting_articles: "
                    f"{sorted(unsupported_profile_numbers)}."
                )

            if claim.quality_weighted_support < 0:
                errors.append(
                    f"Claim {index} has a negative weighted-support score."
                )

        return errors

    @classmethod
    def remove_invalid_claims(
        cls,
        report: SynthesisReport,
        article_count: int,
    ) -> SynthesisReport:
        valid_claims = []

        for claim in report.claims:
            all_numbers = (
                claim.supporting_articles
                + claim.contradicting_articles
            )

            if not claim.supporting_articles:
                continue

            if any(
                number < 1
                or number > article_count
                for number in all_numbers
            ):
                continue

            if (
                set(
                    claim.supporting_articles
                )
                & set(
                    claim.contradicting_articles
                )
            ):
                continue

            valid_claims.append(
                claim
            )

        report.claims = valid_claims

        return report

    @classmethod
    def _count_values(
        cls,
        values,
    ) -> dict[str, int]:
        counter = Counter()

        for value in values:
            normalized = cls._text(
                value
            )

            if normalized.casefold() in cls.MISSING_VALUES:
                continue

            counter[normalized] += 1

        return dict(
            counter.most_common()
        )

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

        text = cls._text(
            value
        ).casefold()

        return text in cls.MISSING_VALUES

    @staticmethod
    def _text(
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

    @classmethod
    def _string_list(
        cls,
        value: Any,
    ) -> list[str]:
        if value is None:
            return []

        if isinstance(
            value,
            list,
        ):
            items = value
        else:
            items = [value]

        result = []

        for item in items:
            text = cls._text(
                item
            )

            if not text:
                continue

            if text.casefold() in cls.MISSING_VALUES:
                continue

            result.append(
                text
            )

        return result

    @staticmethod
    def _article_numbers(
        value: Any,
    ) -> list[int]:
        if value is None:
            return []

        if not isinstance(
            value,
            list,
        ):
            value = [value]

        numbers = []

        for item in value:
            try:
                number = int(
                    item
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if number not in numbers:
                numbers.append(
                    number
                )

        return numbers

    @staticmethod
    def _normalize_confidence(
        value: Any,
    ) -> str:
        text = str(
            value or "Low"
        ).strip().lower()

        if text == "high":
            return "High"

        if text == "medium":
            return "Medium"

        return "Low"

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
    def _to_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return default

    @staticmethod
    def _unique_numbers(
        values,
    ) -> list[int]:
        result = []

        for value in values:
            if value not in result:
                result.append(
                    value
                )

        return result

    @staticmethod
    def _unique_strings(
        values,
    ) -> list[str]:
        result = []

        for value in values:
            if value and value not in result:
                result.append(
                    value
                )

        return result