from Core.agent_registry import get


def create_plan(task):

    planner = get("Planner")

    if planner is None:
        return None

    return planner.execute(task)