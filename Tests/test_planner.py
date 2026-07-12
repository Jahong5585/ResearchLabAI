from Tools.register_tools import register_tools

from Core.agent_registry import get


def main():

    register_tools()

    planner = get("Planner")

    plan = planner.execute(

        "Сделай обзор литературы по искусственному интеллекту"

    )

    print(plan)


if __name__ == "__main__":
    main()