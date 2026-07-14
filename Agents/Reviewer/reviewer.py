import json
import re
from collections import Counter
from typing import Any

from Agents.base_agent import BaseAgent
from Core.citation_validator import CitationValidator
from Core.event_logger import log
from Models.review import Review


class Reviewer(BaseAgent):
    """
    Validates the final literature review against:

    - the Synthesis Report;
    - claim-level evidence profiles;
    - the Comparison Matrix;
    - citation-validation results.

    Evidence profiles are based on metadata and available abstracts.
    They are not full risk-of-bias assessments.
    """

    PROMPT_NAME = "reviewer"
    MODEL_NAME = "REVIEWER_MODEL"

    SECTION_NAMES = {
        "score": "Score",
        "strengths": "Strengths",
        "weaknesses": "Weaknesses",
        "missing": "Missing",
        "recommendations": "Recommendations",
        "decision": "Decision",
    }

    MISSING_VALUES = {
        "",
        "not specified",
        "not reported in the available abstract",
        "not reported in the abstract",
        "none",
        "n/a",
        "unknown",
    }

    COMPARISON_FIELDS = (
        "article_number",
        "normalized_design",
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

    def execute(self, task):
        task.citation_errors = CitationValidator.validate(
            task.literature_review,
            task,
        )

        synthesis = task.synthesis_report

        synthesis_data = self._build_synthesis_data(
            synthesis
        )

        comparison_data = self._build_comparison_data(
            task.comparison_matrix
        )

        comparison_audit = self._build_comparison_audit(
            comparison_data
        )

        evidence_profile_audit = (
            self._build_evidence_profile_audit(
                synthesis
            )
        )

        comparison_errors = (
            self._deterministic_comparison_checks(
                literature_review=task.literature_review,
                comparison_audit=comparison_audit,
            )
        )

        evidence_profile_errors = (
            self._deterministic_evidence_profile_checks(
                literature_review=task.literature_review,
                evidence_profile_audit=evidence_profile_audit,
            )
        )

        deterministic_errors = (
            comparison_errors
            + evidence_profile_errors
        )

        deterministic_errors = self._remove_duplicates(
            deterministic_errors
        )

        prompt = f"""
Evaluate the literature review against the supplied synthesis,
evidence profiles and comparison data.

Do not use external knowledge.

LITERATURE REVIEW

{task.literature_review}

SYNTHESIS REPORT AND CLAIM EVIDENCE PROFILES

{json.dumps(
    synthesis_data,
    ensure_ascii=False,
    indent=2,
)}

COMPARISON MATRIX

{json.dumps(
    comparison_data,
    ensure_ascii=False,
    indent=2,
)}

COMPARISON AUDIT

{json.dumps(
    comparison_audit,
    ensure_ascii=False,
    indent=2,
)}

EVIDENCE PROFILE AUDIT

{json.dumps(
    evidence_profile_audit,
    ensure_ascii=False,
    indent=2,
)}

CITATION VALIDATION ERRORS

{json.dumps(
    task.citation_errors,
    ensure_ascii=False,
    indent=2,
)}

DETERMINISTIC VALIDATION ERRORS

{json.dumps(
    deterministic_errors,
    ensure_ascii=False,
    indent=2,
)}

REVIEW REQUIREMENTS

Check whether the literature review:

1. Accurately represents every important validated synthesis claim.

2. Uses only supporting article numbers supplied for the relevant claim.

3. Correctly distinguishes:

   - objectively measured outcomes;
   - participant perceptions and self-reports;
   - review or meta-analytic evidence;
   - conceptual discussion.

4. Does not describe perception evidence as an objectively measured effect.

5. Does not describe review evidence as a new primary empirical result.

6. Clearly identifies findings supported by only one publication.

7. Does not present a single-study result as a general consensus.

8. Correctly explains when the same claim is supported by multiple
   evidence types.

9. Does not claim methodological convergence unless the evidence profile
   contains multiple evidence types or compatible study designs.

10. Does not print or interpret the raw quality_weighted_support value
    as a scientific-quality score.

11. Does not describe a larger weighted-support score as proof that a
    claim is scientifically true.

12. Does not treat abstract_evidence_level as:

    - a full risk-of-bias assessment;
    - journal quality;
    - complete article quality;
    - proof of publication reliability.

13. Compares methodologies rather than merely listing them.

14. Distinguishes experiments, mixed-methods studies, qualitative
    studies, surveys, reviews and meta-analyses when the available
    records permit this comparison.

15. Distinguishes objectively measured writing results from student
    attitudes, experiences, motivation and self-efficacy.

16. Does not treat differences in participants, methods, outcomes or
    educational levels as direct contradictions.

17. Preserves the boundary that the system analyzed metadata and
    available abstracts rather than necessarily complete article texts.

18. Does not claim that information is absent from the complete article
    merely because it is unavailable in the abstract.

19. Correctly preserves numbers, percentages, sample sizes, years,
    models, tools, authors and DOI values.

20. Uses the required citation format:

    [ARTICLE 1; ARTICLE 2]

21. Contains no unsupported causal explanations or external knowledge.

DECISION RULES

Return revise if any of the following is present:

- a citation-validation error;
- a deterministic validation error;
- perception evidence presented as objective proof;
- review evidence presented as a primary experiment;
- a single-study finding generalized to the entire corpus;
- absence of direct methodological comparison when comparison is possible;
- raw weighted-support values presented as scientific-quality scores;
- abstract completeness presented as complete article quality;
- missing abstract data presented as missing from the complete article;
- an important synthesis claim or caveat omitted;
- a weakness that requires rewriting.

Return approve only when no meaningful revision is required.

OUTPUT RULES

Return exactly:

Score:
<number from 0 to 10>

Strengths:
<one complete item per line, or None.>

Weaknesses:
<one complete item per line, or None.>

Missing:
<one complete item per line, or None.>

Recommendations:
<one complete item per line, or None.>

Decision:
approve
or
revise

Complete every sentence.
Do not add text before Score or after Decision.
"""

        answer = self.ask_llm(prompt)

        task.memory.set(
            "reviewer_raw_answer",
            answer,
        )

        task.memory.set(
            "comparison_audit",
            comparison_audit,
        )

        task.memory.set(
            "evidence_profile_audit",
            evidence_profile_audit,
        )

        review = self._parse_review(
            answer
        )

        self._apply_deterministic_rules(
            review=review,
            citation_errors=task.citation_errors,
            deterministic_errors=deterministic_errors,
        )

        task.review = review

        task.memory.set(
            "review",
            review,
        )

        log(
            "Reviewer",
            (
                f"Оценка: {review.score}; "
                f"решение: {review.decision}; "
                f"ошибок ссылок: "
                f"{len(task.citation_errors)}; "
                f"ошибок проверки: "
                f"{len(deterministic_errors)}; "
                f"профилированных claims: "
                f"{evidence_profile_audit['profiled_claims']}"
            ),
        )

        return review

    @classmethod
    def _build_synthesis_data(
        cls,
        synthesis,
    ) -> dict[str, Any]:
        if synthesis is None:
            return {
                "overview": "",
                "claims": [],
                "methodology_patterns": [],
                "trends": [],
                "contradictions": [],
                "gaps": [],
                "recurring_limitations": [],
                "validation_errors": [],
            }

        claims = []

        for claim in synthesis.claims:
            claims.append(
                {
                    "claim_type": claim.claim_type,
                    "statement": claim.statement,
                    "supporting_articles": (
                        claim.supporting_articles
                    ),
                    "contradicting_articles": (
                        claim.contradicting_articles
                    ),
                    "confidence": claim.confidence,
                    "rationale": claim.rationale,
                    "caveats": claim.caveats,
                    "evidence_count": (
                        claim.evidence_count
                    ),
                    "supporting_designs": (
                        claim.supporting_designs
                    ),
                    "objective_evidence_articles": (
                        claim.objective_evidence_articles
                    ),
                    "objective_evidence_count": (
                        claim.objective_evidence_count
                    ),
                    "perception_evidence_articles": (
                        claim.perception_evidence_articles
                    ),
                    "perception_evidence_count": (
                        claim.perception_evidence_count
                    ),
                    "review_evidence_articles": (
                        claim.review_evidence_articles
                    ),
                    "review_evidence_count": (
                        claim.review_evidence_count
                    ),
                    "has_multiple_evidence_types": (
                        claim.has_multiple_evidence_types
                    ),
                    "abstract_evidence_levels": (
                        claim.abstract_evidence_levels
                    ),
                    "quality_weighted_support": (
                        claim.quality_weighted_support
                    ),
                    "evidence_profile_note": (
                        claim.evidence_profile_note
                    ),
                }
            )

        return {
            "overview": synthesis.overview,
            "claims": claims,
            "methodology_patterns": (
                synthesis.methodology_patterns
            ),
            "trends": synthesis.trends,
            "contradictions": (
                synthesis.contradictions
            ),
            "gaps": synthesis.gaps,
            "recurring_limitations": (
                synthesis.recurring_limitations
            ),
            "validation_errors": (
                synthesis.validation_errors
            ),
        }

    @classmethod
    def _build_comparison_data(
        cls,
        comparison_matrix,
    ) -> list[dict[str, Any]]:
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

    @classmethod
    def _build_comparison_audit(
        cls,
        comparison_data,
    ) -> dict[str, Any]:
        design_counter = Counter()
        evidence_counter = Counter()
        source_counter = Counter()

        available_field_counts = {
            "educational_level": 0,
            "country": 0,
            "participants": 0,
            "sample_size": 0,
            "methodology": 0,
            "evaluation_metrics": 0,
            "results": 0,
            "findings": 0,
            "limitations": 0,
        }

        for row in comparison_data:
            design = cls._text(
                row.get(
                    "normalized_design",
                    "",
                )
            )

            evidence_level = cls._text(
                row.get(
                    "abstract_evidence_level",
                    "",
                )
            )

            source_type = cls._text(
                row.get(
                    "source_type",
                    "",
                )
            )

            if not cls._is_missing(
                design
            ):
                design_counter[design] += 1

            if not cls._is_missing(
                evidence_level
            ):
                evidence_counter[
                    evidence_level
                ] += 1

            if not cls._is_missing(
                source_type
            ):
                source_counter[
                    source_type
                ] += 1

            for field_name in available_field_counts:
                if not cls._is_missing(
                    row.get(
                        field_name,
                        "",
                    )
                ):
                    available_field_counts[
                        field_name
                    ] += 1

        return {
            "article_count": len(
                comparison_data
            ),
            "design_counts": dict(
                design_counter
            ),
            "distinct_design_count": len(
                design_counter
            ),
            "abstract_evidence_level_counts": dict(
                evidence_counter
            ),
            "source_type_counts": dict(
                source_counter
            ),
            "available_field_counts": (
                available_field_counts
            ),
            "direct_methodological_comparison_expected": (
                len(design_counter) >= 2
            ),
            "source_boundary": (
                "The matrix evaluates abstract-level evidence usability, "
                "not full-text scientific quality or risk of bias."
            ),
        }

    @classmethod
    def _build_evidence_profile_audit(
        cls,
        synthesis,
    ) -> dict[str, Any]:
        if synthesis is None:
            return {
                "total_claims": 0,
                "profiled_claims": 0,
                "objective_supported_claims": 0,
                "perception_supported_claims": 0,
                "review_supported_claims": 0,
                "mixed_evidence_claims": 0,
                "single_study_claims": 0,
                "weighted_support_average": 0.0,
                "weighted_support_minimum": 0.0,
                "weighted_support_maximum": 0.0,
            }

        claims = synthesis.claims or []

        weighted_scores = [
            claim.quality_weighted_support
            for claim in claims
            if claim.evidence_profile_note
        ]

        profiled_claims = sum(
            1
            for claim in claims
            if claim.evidence_profile_note
        )

        objective_supported_claims = sum(
            1
            for claim in claims
            if claim.objective_evidence_articles
        )

        perception_supported_claims = sum(
            1
            for claim in claims
            if claim.perception_evidence_articles
        )

        review_supported_claims = sum(
            1
            for claim in claims
            if claim.review_evidence_articles
        )

        mixed_evidence_claims = sum(
            1
            for claim in claims
            if claim.has_multiple_evidence_types
        )

        single_study_claims = sum(
            1
            for claim in claims
            if claim.evidence_count == 1
        )

        if weighted_scores:
            weighted_average = (
                sum(weighted_scores)
                / len(weighted_scores)
            )

            weighted_minimum = min(
                weighted_scores
            )

            weighted_maximum = max(
                weighted_scores
            )
        else:
            weighted_average = 0.0
            weighted_minimum = 0.0
            weighted_maximum = 0.0

        return {
            "total_claims": len(claims),
            "profiled_claims": profiled_claims,
            "objective_supported_claims": (
                objective_supported_claims
            ),
            "perception_supported_claims": (
                perception_supported_claims
            ),
            "review_supported_claims": (
                review_supported_claims
            ),
            "mixed_evidence_claims": (
                mixed_evidence_claims
            ),
            "single_study_claims": (
                single_study_claims
            ),
            "weighted_support_average": round(
                weighted_average,
                2,
            ),
            "weighted_support_minimum": round(
                weighted_minimum,
                2,
            ),
            "weighted_support_maximum": round(
                weighted_maximum,
                2,
            ),
            "quality_boundary": (
                "Weighted support is a deterministic abstract-level "
                "indicator, not a full scientific-quality assessment."
            ),
        }

    @classmethod
    def _deterministic_comparison_checks(
        cls,
        literature_review: str,
        comparison_audit: dict[str, Any],
    ) -> list[str]:
        errors = []

        text = cls._text(
            literature_review
        ).casefold()

        if not text:
            return [
                "Текст обзора отсутствует."
            ]

        comparison_expected = comparison_audit.get(
            "direct_methodological_comparison_expected",
            False,
        )

        comparison_action_markers = (
            "сравнен",
            "сопостав",
            "по сравнению",
            "в отличие",
            "тогда как",
            "в то время как",
            "различаются",
            "различие между",
            "разница между",
            "напротив",
            "с одной стороны",
            "с другой стороны",
            "compare",
            "comparison",
            "compared with",
            "compared to",
            "in contrast",
            "whereas",
            "while",
            "unlike",
            "differences between",
            "versus",
        )

        methodology_markers = (
            "метод",
            "методолог",
            "дизайн исследован",
            "эксперимент",
            "интервенцион",
            "смешанн",
            "качествен",
            "количествен",
            "опрос",
            "анкет",
            "интервью",
            "фокус-груп",
            "метаанализ",
            "мета-анализ",
            "систематическ обзор",
            "обзор литературы",
            "эмпирическ",
            "восприятие студент",
            "самоотчёт",
            "объективн измер",
            "предтест",
            "посттест",
            "method",
            "methodolog",
            "study design",
            "experimental",
            "intervention",
            "mixed-method",
            "qualitative",
            "quantitative",
            "survey",
            "questionnaire",
            "interview",
            "focus group",
            "meta-analysis",
            "systematic review",
            "literature review",
            "empirical",
            "student perception",
            "self-report",
            "objective measure",
            "pre-test",
            "post-test",
        )

        has_comparison_action = any(
            marker in text
            for marker in comparison_action_markers
        )

        has_methodological_content = any(
            marker in text
            for marker in methodology_markers
        )

        if (
            comparison_expected
            and not (
                has_comparison_action
                and has_methodological_content
            )
        ):
            errors.append(
                "Comparison Matrix содержит несколько типов исследований, "
                "но итоговый обзор не демонстрирует прямого "
                "сопоставления методологий или типов доказательств."
            )

        forbidden_source_boundary_phrases = (
            "статьи не содержат",
            "исследования не содержат",
            "авторы не указали",
            "авторы не предоставили",
            "в статьях отсутствуют",
            "в исследованиях отсутствуют",
            "the articles do not contain",
            "the studies failed to report",
            "the authors did not provide",
            "the articles lack",
        )

        for phrase in forbidden_source_boundary_phrases:
            if phrase in text:
                errors.append(
                    "Обнаружена формулировка, которая переносит отсутствие "
                    "данных в аннотации на полный текст статьи: "
                    f"«{phrase}»."
                )

        unsupported_quality_phrases = (
            "самая качественная статья",
            "наиболее качественная статья",
            "самое надежное исследование",
            "наиболее надежное исследование",
            "самая сильная статья",
            "лучшая статья",
            "scientifically superior",
            "highest quality article",
            "most reliable study",
            "best article",
        )

        for phrase in unsupported_quality_phrases:
            if phrase in text:
                errors.append(
                    "Abstract-level evidence usability ошибочно "
                    "представлена как окончательная оценка научного "
                    f"качества: «{phrase}»."
                )

        return cls._remove_duplicates(
            errors
        )

    @classmethod
    def _deterministic_evidence_profile_checks(
        cls,
        literature_review: str,
        evidence_profile_audit: dict[str, Any],
    ) -> list[str]:
        errors = []

        text = cls._text(
            literature_review
        ).casefold()

        if not text:
            return [
                "Текст обзора отсутствует."
            ]

        raw_score_markers = (
            "quality_weighted_support",
            "weighted support score",
            "взвешенная поддержка:",
            "оценка взвешенной поддержки:",
        )

        for marker in raw_score_markers:
            if marker in text:
                errors.append(
                    "В итоговом обзоре выведено внутреннее техническое "
                    "значение quality_weighted_support."
                )

        objective_claim_count = evidence_profile_audit.get(
            "objective_supported_claims",
            0,
        )

        perception_claim_count = evidence_profile_audit.get(
            "perception_supported_claims",
            0,
        )

        review_claim_count = evidence_profile_audit.get(
            "review_supported_claims",
            0,
        )

        objective_language_markers = (
            "объективно доказано",
            "объективно подтверждено",
            "экспериментально доказано",
            "objectively proven",
            "objectively demonstrated",
            "experimentally proven",
        )

        if (
            objective_claim_count == 0
            and any(
                marker in text
                for marker in objective_language_markers
            )
        ):
            errors.append(
                "Обзор использует язык объективного доказательства, "
                "хотя доказательные профили не содержат claims с "
                "объективно измеренными результатами."
            )

        perception_language_markers = (
            "восприятие студентов",
            "мнение студентов",
            "самоотчёт",
            "самоотчеты",
            "student perceptions",
            "student attitudes",
            "self-reported",
            "self-report",
        )

        if (
            perception_claim_count == 0
            and any(
                marker in text
                for marker in perception_language_markers
            )
        ):
            errors.append(
                "Обзор ссылается на восприятие или самоотчёты, "
                "хотя доказательные профили не содержат соответствующих "
                "источников поддержки."
            )

        review_language_markers = (
            "метаанализ",
            "мета-анализ",
            "систематический обзор",
            "обзор литературы",
            "meta-analysis",
            "systematic review",
            "literature review",
        )

        if (
            review_claim_count == 0
            and any(
                marker in text
                for marker in review_language_markers
            )
        ):
            errors.append(
                "Обзор описывает обзорные или метааналитические "
                "доказательства, хотя профили claims не содержат "
                "review-evidence статей."
            )

        return cls._remove_duplicates(
            errors
        )

    @classmethod
    def _parse_review(
        cls,
        answer: str,
    ) -> Review:
        review = Review()

        if not isinstance(
            answer,
            str,
        ):
            review.decision = "revise"

            review.weaknesses.append(
                "Reviewer returned a non-text response."
            )

            return review

        sections = cls._extract_sections(
            answer
        )

        score_text = " ".join(
            sections.get(
                "Score",
                [],
            )
        )

        review.score = cls._parse_score(
            score_text
        )

        review.strengths = cls._clean_items(
            sections.get(
                "Strengths",
                [],
            )
        )

        review.weaknesses = cls._clean_items(
            sections.get(
                "Weaknesses",
                [],
            )
        )

        review.missing_topics = cls._clean_items(
            sections.get(
                "Missing",
                [],
            )
        )

        review.recommendations = cls._clean_items(
            sections.get(
                "Recommendations",
                [],
            )
        )

        decision_text = " ".join(
            sections.get(
                "Decision",
                [],
            )
        ).strip().lower()

        if "revise" in decision_text:
            review.decision = "revise"
        elif "approve" in decision_text:
            review.decision = "approve"
        else:
            review.decision = "revise"

            review.weaknesses.append(
                "Reviewer did not return a valid decision."
            )

        return review

    @classmethod
    def _extract_sections(
        cls,
        answer: str,
    ) -> dict[str, list[str]]:
        sections = {
            section_name: []
            for section_name in cls.SECTION_NAMES.values()
        }

        current_section = None

        heading_pattern = re.compile(
            r"^\s*"
            r"(Score|Strengths|Weaknesses|Missing|"
            r"Recommendations|Decision)"
            r"\s*:\s*(.*)$",
            re.IGNORECASE,
        )

        for raw_line in answer.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            heading_match = heading_pattern.match(
                line
            )

            if heading_match:
                raw_heading = (
                    heading_match.group(
                        1
                    ).lower()
                )

                current_section = (
                    cls.SECTION_NAMES[
                        raw_heading
                    ]
                )

                inline_value = (
                    heading_match.group(
                        2
                    ).strip()
                )

                if inline_value:
                    sections[
                        current_section
                    ].append(
                        inline_value
                    )

                continue

            if current_section is not None:
                sections[
                    current_section
                ].append(
                    line
                )

        return sections

    @staticmethod
    def _parse_score(
        text: str,
    ) -> float:
        match = re.search(
            r"\b(10(?:\.0+)?|[0-9](?:\.\d+)?)\b",
            text or "",
        )

        if match is None:
            return 0.0

        score = float(
            match.group(1)
        )

        return max(
            0.0,
            min(
                score,
                10.0,
            ),
        )

    @staticmethod
    def _clean_items(
        items: list[str],
    ) -> list[str]:
        cleaned = []

        for item in items:
            text = str(
                item
            ).strip()

            text = re.sub(
                r"^[\-\*\u2022]+\s*",
                "",
                text,
            )

            if not text:
                continue

            if text.lower().rstrip(
                "."
            ) in {
                "none",
                "not found",
                "не обнаружены",
                "не указаны",
                "отсутствуют",
            }:
                continue

            cleaned.append(
                text
            )

        return cleaned

    @staticmethod
    def _apply_deterministic_rules(
        review: Review,
        citation_errors: list[str],
        deterministic_errors: list[str],
    ) -> None:
        all_errors = (
            list(
                citation_errors
            )
            + list(
                deterministic_errors
            )
        )

        if all_errors:
            review.decision = "revise"

            for error in all_errors:
                if error not in review.weaknesses:
                    review.weaknesses.append(
                        error
                    )

        review.score = max(
            0.0,
            min(
                review.score,
                10.0,
            ),
        )

        has_revision_recommendation = bool(
            review.recommendations
        )

        has_substantive_weakness = bool(
            review.weaknesses
        )

        if (
            review.decision == "approve"
            and has_substantive_weakness
            and has_revision_recommendation
        ):
            review.decision = "revise"

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
            return len(
                value
            ) == 0

        return (
            cls._text(
                value
            ).casefold()
            in cls.MISSING_VALUES
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

    @staticmethod
    def _remove_duplicates(
        items: list[str],
    ) -> list[str]:
        unique_items = []

        for item in items:
            if item not in unique_items:
                unique_items.append(
                    item
                )

        return unique_items