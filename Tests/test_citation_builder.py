from Tools.register_tools import register_tools

from Core.research_service import ResearchService
from Core.citation_builder import CitationBuilder


def main():

    register_tools()

    service = ResearchService()

    papers = service.search(
        "Artificial Intelligence in Education",
        rows=5
    )

    citations = CitationBuilder.build(papers)

    for citation in citations:

        print(citation.format())


if __name__ == "__main__":
    main()