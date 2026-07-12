from Tools.register_tools import register_tools

from Core.research_service import ResearchService
from Core.paper_context_builder import PaperContextBuilder


def main():

    register_tools()

    service = ResearchService()

    papers = service.search(
        "Artificial Intelligence in Education",
        rows=3
    )

    context = PaperContextBuilder.build(papers)

    print(context)


if __name__ == "__main__":
    main()