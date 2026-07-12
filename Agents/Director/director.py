from Core.event_logger import log
from Core.planner_executor import create_plan
from Core.orchestrator import Orchestrator


class Director:

    def __init__(self):

        log("Director", "Запущен.")

        self.orchestrator = Orchestrator()

    def execute(self, user_request):

        log("Director", "Получена новая задача.")

        plan = create_plan(user_request)

        log("Director", "План построен.")

        task = self.orchestrator.execute(
            user_request,
            plan
        )

        if task.review is not None:

            if task.review.decision == "approve":

                return task.literature_review

            return f"""
================ REVIEW ================

Score: {task.review.score}

Strengths:

{chr(10).join(task.review.strengths)}

Weaknesses:

{chr(10).join(task.review.weaknesses)}

Missing:

{chr(10).join(task.review.missing_topics)}

Recommendations:

{chr(10).join(task.review.recommendations)}

Decision:

{task.review.decision}

================ LITERATURE REVIEW ================

{task.literature_review}
"""

        return task.literature_review