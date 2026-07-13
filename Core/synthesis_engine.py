from __future__ import annotations

from collections import Counter
from typing import Any

from Models.synthesis_claim import SynthesisClaim
from Models.synthesis_report import SynthesisReport


class SynthesisEngine:
    """
    Deterministic helpers and validation for cross-paper synthesis.
    """

    MISSING_VALUES = {
        "",
        "not specified",
        "not reported in the available abstract",
        "not reported in the abstract",
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

    @classmethod
    def build_statistics(cls, summaries) -> dict[str, Any]:
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
    ) -> SynthesisReport:
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

        report.validation_errors = cls.validate(
            report,
            len(summaries),
        )

        return report

    @classmethod
    def fallback(
        cls,
        summaries,
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

    @staticmethod
    def _text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

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