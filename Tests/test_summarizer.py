from Tools.register_tools import register_tools

from Core.research_service import ResearchService
from Agents.Summarizer.summarizer import Summarizer


def main():

    register_tools()

    service = ResearchService()

    papers = service.search(

        "Artificial Intelligence in Education",

        rows=1

    )

    summarizer = Summarizer()

    summary = summarizer.execute(

        papers[0]

    )

    print(summary)


if __name__ == "__main__":
    main()