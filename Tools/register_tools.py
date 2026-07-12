from Core.tool_manager import register

from Tools.time_tool import TimeTool
from Tools.web_search_tool import WebSearchTool
from Tools.http_tool import HttpTool
from Tools.crossref_tool import CrossrefTool
from Tools.crossref_abstract_tool import CrossrefAbstractTool
from Tools.openalex_tool import OpenAlexTool


def register_tools():

    register("TimeTool", TimeTool())
    register("WebSearch", WebSearchTool())
    register("Http", HttpTool())
    register("Crossref", CrossrefTool())
    register("CrossrefAbstract", CrossrefAbstractTool())
    register("OpenAlex", OpenAlexTool())