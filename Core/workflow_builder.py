from Models.plan import Plan
from Models.plan_step import PlanStep


class WorkflowBuilder:
    """
    Builds a deterministic workflow for literature-review requests.

    The Planner may suggest a plan, but literature reviews always use
    the required scientific pipeline defined below.
    """

    LITERATURE_KEYWORDS = (
        # Russian
        "литератур",
        "обзор",
        "исследован",
        "научная статья",
        "научные статьи",
        "статьи",
        "публикаци",
        "систематический обзор",
        "анализ литературы",

        # English
        "literature",
        "literature review",
        "systematic review",
        "research",
        "article",
        "articles",
        "paper",
        "papers",
        "publication",
        "publications",
    )

    @staticmethod
    def build(user_request: str, plan: Plan | None) -> Plan:
        """
        Create a workflow for the user's request.

        For literature-review requests, a fixed scientific workflow is used.
        For other requests, the plan created by Planner is returned unchanged.
        """

        if plan is None:
            plan = Plan()

        request = (user_request or "").casefold().strip()

        is_literature_request = any(
            keyword in request
            for keyword in WorkflowBuilder.LITERATURE_KEYWORDS
        )

        if not is_literature_request:
            return plan

        literature_plan = Plan()

        required_steps = [
            ("Researcher", "Search for relevant scientific papers"),
            ("Ranking", "Rank papers by relevance and quality"),
            (
                "Summarizer",
                "Extract structured scientific data from every paper",
            ),
            ("Cluster", "Group papers into related research themes"),
            ("Outline", "Build an analytical literature-review outline"),
            (
                "Synthesis",
                "Compare studies and create evidence-based synthesis claims",
            ),
            (
                "Writer",
                "Write the literature review using synthesis claims",
            ),
            (
                "Reviewer",
                "Check completeness, evidence, citations and academic style",
            ),
        ]

        for agent_name, goal in required_steps:
            literature_plan.add(
                PlanStep(
                    agent_name,
                    goal,
                )
            )

        return literature_plan