import requests

from Models.paper import Paper
from Tools.base_tool import BaseTool


class OpenAlexTool(BaseTool):

    NAME = "OpenAlex"

    URL = "https://api.openalex.org/works"

    def execute(self, query: str, rows: int = 10):

        try:

            response = requests.get(
                self.URL,
                params={
                    "search": query,
                    "per-page": rows
                },
                headers={
                    "User-Agent": "ResearchLabAI/1.0"
                },
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            papers = []

            for item in data.get("results", []):

                authors = []

                for author in item.get("authorships", []):

                    author_data = author.get("author")

                    if author_data:
                        authors.append(
                            author_data.get("display_name", "")
                        )

                primary_location = item.get("primary_location") or {}
                source = primary_location.get("source") or {}

                abstract = ""

                inverted = item.get("abstract_inverted_index")

                if inverted:

                    words = {}

                    for word, positions in inverted.items():

                        for pos in positions:
                            words[pos] = word

                    abstract = " ".join(
                        words[index]
                        for index in sorted(words.keys())
                    )

                papers.append(
                    Paper(
                        title=item.get("display_name", ""),
                        authors=authors,
                        journal=source.get("display_name", ""),
                        publisher="",
                        year=item.get("publication_year"),
                        paper_type=item.get("type", ""),
                        citations=item.get("cited_by_count", 0),
                        doi=(item.get("doi") or "").replace("https://doi.org/", ""),
                        url=item.get("id", ""),
                        abstract=abstract
                    )
                )

            return papers

        except Exception as e:

            print(f"OpenAlex error: {e}")

            return []