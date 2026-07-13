from Models.plan import Plan
from Models.plan_step import PlanStep


class WorkflowBuilder:
    @staticmethod
    def build(user_request, plan):
        if plan is None:
            plan = Plan()

        request = user_request.lower()

        if (
            "литератур" in request
            or "обзор" in request
            or "исследован" in request
            or "article" in request
            or "paper" in request
        ):
            new_plan = Plan()

            required = [
                ("Researcher", "Search papers"),
                ("Ranking", "Rank papers"),
                ("Summarizer", "Extract structured data from each paper"),
                ("Cluster", "Group related papers"),
                ("Outline", "Build analytical outline"),
                ("Synthesis", "Compare studies and build evidence claims"),
                ("Writer", "Write literature review from synthesis claims"),
                ("Reviewer", "Review literature and citations"),
            ]

            for agent, goal in required:
                new_plan.add(PlanStep(agent, goal))

            return new_plan

        return plan
