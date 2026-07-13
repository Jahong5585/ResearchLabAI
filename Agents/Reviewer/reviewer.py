import json
import re

from Agents.base_agent import BaseAgent
from Core.citation_validator import CitationValidator
from Models.review import Review


class Reviewer(BaseAgent):
    PROMPT_NAME = "reviewer"
    MODEL_NAME = "REVIEWER_MODEL"

    @staticmethod
    def _parse_score(text):
        match = re.search(r"\d+(\.\d+)?", text)
        return float(match.group()) if match else 0.0

    def execute(self, task):
        task.citation_errors = CitationValidator.validate(
            task.literature_review,
            task,
        )

        synthesis = task.synthesis_report
        synthesis_data = {
            "overview": synthesis.overview if synthesis else "",
            "claims": [
                {
                    "claim_type": claim.claim_type,
                    "statement": claim.statement,
                    "supporting_articles": claim.supporting_articles,
                    "contradicting_articles": claim.contradicting_articles,
                    "confidence": claim.confidence,
                    "caveats": claim.caveats,
                }
                for claim in (synthesis.claims if synthesis else [])
            ],
            "validation_errors": (
                synthesis.validation_errors if synthesis else []
            ),
        }

        prompt = f"""
LITERATURE REVIEW

{task.literature_review}

SYNTHESIS REPORT

{json.dumps(synthesis_data, ensure_ascii=False, indent=2)}

CITATION VALIDATION ERRORS

{json.dumps(task.citation_errors, ensure_ascii=False, indent=2)}
"""

        answer = self.ask_llm(prompt)
        review = Review()
        current = None

        for raw_line in answer.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            if line.endswith(":"):
                current = line[:-1]
                continue

            if current == "Score":
                review.score = self._parse_score(line)
            elif current == "Strengths":
                review.strengths.append(line)
            elif current == "Weaknesses":
                review.weaknesses.append(line)
            elif current == "Missing":
                review.missing_topics.append(line)
            elif current == "Recommendations":
                review.recommendations.append(line)
            elif current == "Decision":
                review.decision = line.lower()

        if task.citation_errors:
            review.decision = "revise"
            review.weaknesses.extend(task.citation_errors)

        task.review = review
        task.memory.set("review", review)
        return review
