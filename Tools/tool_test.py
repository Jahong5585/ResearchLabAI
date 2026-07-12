from Tools.register_tools import register_tools
from Core.tool_manager import get

from Tools.paper_sorter import PaperSorter


def test_tools():

    register_tools()

    tool = get("Crossref")

    papers = tool.execute(
        "Artificial Intelligence in Education",
        rows=10
    )

    papers = PaperSorter.sort_by_citations(papers)

    for index, paper in enumerate(papers, start=1):

        print("=" * 80)

        print(f"#{index}")

        print("Title:", paper.title)

        print("Citations:", paper.citations)

        print("Year:", paper.year)

        print("Journal:", paper.journal)

        print("DOI:", paper.doi)


if __name__ == "__main__":
    test_tools()