from Core.event_logger import log
from Core.planner_executor import create_plan
from Core.orchestrator import Orchestrator


class Director:
    """
    Coordinates the complete ResearchLab AI workflow.

    During the testing stage, the Reviewer report is always displayed,
    including when the review is approved.
    """

    def __init__(self):
        log(
            "Director",
            "Запущен.",
        )

        self.orchestrator = Orchestrator()

    def execute(self, user_request):
        log(
            "Director",
            "Получена новая задача.",
        )

        plan = create_plan(user_request)

        log(
            "Director",
            "План построен.",
        )

        task = self.orchestrator.execute(
            user_request,
            plan,
        )

        if task.review is not None:
            return self._build_review_output(task)

        return task.literature_review

    @staticmethod
    def _build_review_output(task):
        review = task.review

        strengths = (
            "\n".join(review.strengths)
            if review.strengths
            else "Не указаны."
        )

        weaknesses = (
            "\n".join(review.weaknesses)
            if review.weaknesses
            else "Не обнаружены."
        )

        missing_topics = (
            "\n".join(review.missing_topics)
            if review.missing_topics
            else "Не обнаружены."
        )

        recommendations = (
            "\n".join(review.recommendations)
            if review.recommendations
            else "Дополнительные рекомендации отсутствуют."
        )

        decision = review.decision or "not specified"

        return f"""
================ REVIEW ================

Score: {review.score}

Strengths:

{strengths}

Weaknesses:

{weaknesses}

Missing:

{missing_topics}

Recommendations:

{recommendations}

Decision:

{decision}

================ LITERATURE REVIEW ================

{task.literature_review}
"""