import requests

from Tools.base_tool import BaseTool


class CrossrefAbstractTool(BaseTool):

    NAME = "CrossrefAbstract"

    URL = "https://api.crossref.org/works"

    def execute(self, doi: str):

        try:

            response = requests.get(
                f"{self.URL}/{doi}",
                headers={
                    "User-Agent": "ResearchLabAI/1.0 (research)"
                },
                timeout=30
            )

            response.raise_for_status()

            item = response.json()["message"]

            abstract = item.get("abstract")

            if abstract is None:
                return None

            return abstract

        except Exception:

            return None