from Core.tool_manager import get


class ResearchService:

    def __init__(self):

        self.crossref = get("Crossref")
        self.openalex = get("OpenAlex")

    def search(self, query: str, rows: int = 10):

        papers = []

        if self.crossref:

            result = self.crossref.execute(
                query=query,
                rows=rows
            )

            if isinstance(result, list):

                papers.extend(result)

        if self.openalex:

            result = self.openalex.execute(
                query=query,
                rows=rows
            )

            if isinstance(result, list):

                papers.extend(result)

        unique = {}

        for paper in papers:

            key = ""

            if getattr(paper, "doi", ""):

                key = paper.doi.lower().strip()

            else:

                key = paper.title.lower().strip()

            unique[key] = paper

        papers = list(unique.values())

        papers.sort(

            key=lambda x: getattr(
                x,
                "citations",
                0
            ),

            reverse=True

        )

        return papers