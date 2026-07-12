import re

from Agents.base_agent import BaseAgent
from Models.review import Review
from Core.citation_validator import CitationValidator


class Reviewer(BaseAgent):

    PROMPT_NAME = "reviewer"
    MODEL_NAME = "REVIEWER_MODEL"
    def _parse_score(self, text):

        match = re.search(r"\d+(\.\d+)?", text)

        if match:

            return float(match.group())

        return 0.0

    def execute(self, task):

        task.citation_errors = CitationValidator.validate(
            task.literature_review,
            task
        )

        prompt = f"""
Обзор литературы

{task.literature_review}

Ошибки проверки ссылок

{task.citation_errors}
"""

        answer = self.ask_llm(prompt)

        review = Review()

        current = None

        for line in answer.splitlines():

            line = line.strip()

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

        task.review = review

        task.memory.set(
            "review",
            review
        )

        return review