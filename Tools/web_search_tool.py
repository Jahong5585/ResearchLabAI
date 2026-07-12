import requests

from Tools.base_tool import BaseTool


class WebSearchTool(BaseTool):

    NAME = "WebSearch"

    def execute(self, query: str, max_results: int = 5):

        url = "https://duckduckgo.com/html/"

        try:

            response = requests.post(
                url,
                data={
                    "q": query
                },
                headers={
                    "User-Agent": "ResearchLabAI"
                },
                timeout=20
            )

            return {
                "status": response.status_code,
                "query": query,
                "html": response.text[:10000]
            }

        except Exception as e:

            return {
                "status": "ERROR",
                "message": str(e)
            }