from Tools.register_tools import register_tools

from Core.research_service import ResearchService


def main():

    register_tools()

    service = ResearchService()

    papers = service.search(
        "Artificial Intelligence in Education",
        rows=5
    )

    for paper in papers:

        print("=" * 80)

        print(paper.title)

        print(paper.year)

        print(paper.citations)

        print(paper.doi)


if __name__ == "__main__":
    main()