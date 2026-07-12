from Models.plan import Plan
from Models.plan_step import PlanStep


def main():

    plan = Plan()

    plan.add(
        PlanStep(
            "Researcher",
            "Find scientific papers"
        )
    )

    plan.add(
        PlanStep(
            "Ranking",
            "Rank papers"
        )
    )

    plan.add(
        PlanStep(
            "Writer",
            "Write literature review"
        )
    )

    print(plan)


if __name__ == "__main__":
    main()