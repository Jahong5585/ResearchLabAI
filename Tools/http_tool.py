import requests

from Tools.base_tool import BaseTool


class HttpTool(BaseTool):

    NAME = "Http"

    def execute(self, url: str):

        try:

            response = requests.get(
                url,
                timeout=20,
                headers={
                    "User-Agent": "ResearchLabAI"
                }
            )

            return {
                "status": response.status_code,
                "text": response.text[:5000]
            }

        except Exception as e:

            return {
                "status": "ERROR",
                "message": str(e)
            }