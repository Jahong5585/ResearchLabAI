from Tools.register_tools import register_tools

from Core.tool_manager import get


def main():

    register_tools()

    tool = get("CrossrefAbstract")

    abstract = tool.execute(
        "10.1016/j.caeai.2022.100049"
    )

    print(abstract)


if __name__ == "__main__":
    main()