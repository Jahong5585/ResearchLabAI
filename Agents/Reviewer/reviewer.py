import json
import re

from Agents.base_agent import BaseAgent
from Core.citation_validator import CitationValidator
from Core.event_logger import log
from Models.review import Review


class Reviewer(BaseAgent):
    """
    Validates the final literature review against the synthesis report.

    The parser supports both formats:

        Score:
        9.0

    and:

        Score: 9.0
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

    def execute(self, task):
        task.citation_errors = CitationValidator.validate(
            task.literature_review,
            task,
        )

        synthesis = task.synthesis_report

        synthesis_data = {
            "overview": (
                synthesis.overview
                if synthesis
                else ""
            ),
            "claims": [
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
                }
                for claim in (
                    synthesis.claims
                    if synthesis
                    else []
                )
            ],
            "methodology_patterns": (
                synthesis.methodology_patterns
                if synthesis
                else []
            ),
            "trends": (
                synthesis.trends
                if synthesis
                else []
            ),
            "contradictions": (
                synthesis.contradictions
                if synthesis
                else []
            ),
            "gaps": (
                synthesis.gaps
                if synthesis
                else []
            ),
            "recurring_limitations": (
                synthesis.recurring_limitations
                if synthesis
                else []
            ),
            "validation_errors": (
                synthesis.validation_errors
                if synthesis
                else []
            ),
        }

        prompt = f"""
LITERATURE REVIEW

{task.literature_review}

SYNTHESIS REPORT

{json.dumps(
    synthesis_data,
    ensure_ascii=False,
    indent=2,
)}

CITATION VALIDATION ERRORS

{json.dumps(
    task.citation_errors,
    ensure_ascii=False,
    indent=2,
)}
"""

        answer = self.ask_llm(prompt)

        task.memory.set(
            "reviewer_raw_answer",
            answer,
        )

        review = self._parse_review(answer)

        self._apply_deterministic_rules(
            review,
            task.citation_errors,
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
                f"{len(task.citation_errors)}"
            ),
        )

        return review

    @classmethod
    def _parse_review(cls, answer: str) -> Review:
        review = Review()

        if not isinstance(answer, str):
            review.decision = "revise"
            review.weaknesses.append(
                "Reviewer returned a non-text response."
            )
            return review

        sections = cls._extract_sections(answer)

        score_text = " ".join(
            sections.get("Score", [])
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
                    heading_match.group(1).lower()
                )

                current_section = (
                    cls.SECTION_NAMES[raw_heading]
                )

                inline_value = (
                    heading_match.group(2).strip()
                )

                if inline_value:
                    sections[current_section].append(
                        inline_value
                    )

                continue

            if current_section is not None:
                sections[current_section].append(
                    line
                )

        return sections

    @staticmethod
    def _parse_score(text: str) -> float:
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
            text = str(item).strip()

            text = re.sub(
                r"^[\-\*\u2022]+\s*",
                "",
                text,
            )

            if not text:
                continue

            if text.lower().rstrip(".") in {
                "none",
                "not found",
                "не обнаружены",
                "не указаны",
                "отсутствуют",
            }:
                continue

            cleaned.append(text)

        return cleaned

    @staticmethod
    def _apply_deterministic_rules(
        review: Review,
        citation_errors: list[str],
    ) -> None:
        if citation_errors:
            review.decision = "revise"

            for error in citation_errors:
                if error not in review.weaknesses:
                    review.weaknesses.append(
                        error
                    )

        if review.score < 0:
            review.score = 0.0

        if review.score > 10:
            review.score = 10.0

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