from pprint import pprint

from Tools.register_tools import register_tools
from Core.tool_manager import get


def main():

    register_tools()

    tool = get("OpenAlex")

    result = tool.execute(
        "Artificial Intelligence in Education",
        per_page=3
    )

    pprint(result)


if __name__ == "__main__":
    main()