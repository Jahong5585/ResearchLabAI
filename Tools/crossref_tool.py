import re
import requests

from Models.paper import Paper
from Tools.base_tool import BaseTool


class CrossrefTool(BaseTool):

    NAME = "Crossref"

    URL = "https://api.crossref.org/works"

    def execute(self, query: str, rows: int = 5):

        try:

            response = requests.get(
                self.URL,
                params={
                    "query": query,
                    "rows": rows
                },
                headers={
                    "User-Agent": "ResearchLabAI/1.0 (research)"
                },
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            papers = []

            for item in data["message"]["items"]:

                title = item.get("title", [""])[0]

                authors = []

                for author in item.get("author", []):

                    given = author.get("given", "")
                    family = author.get("family", "")

                    authors.append(f"{given} {family}".strip())

                year = None

                if "published-print" in item:
                    year = item["published-print"]["date-parts"][0][0]

                elif "published-online" in item:
                    year = item["published-online"]["date-parts"][0][0]

                journal = ""

                if item.get("container-title"):
                    journal = item["container-title"][0]

                abstract = item.get("abstract", "")

                if abstract:
                    abstract = re.sub(r"<[^>]+>", "", abstract)
                    abstract = abstract.replace("\n", " ").strip()

                papers.append(
                    Paper(
                        title=title,
                        authors=authors,
                        journal=journal,
                        publisher=item.get("publisher", ""),
                        year=year,
                        paper_type=item.get("type", ""),
                        citations=item.get("is-referenced-by-count", 0),
                        doi=item.get("DOI", ""),
                        url=item.get("URL", ""),
                        abstract=abstract
                    )
                )

            return papers

        except Exception as e:

            print(f"Crossref error: {e}")

            return []