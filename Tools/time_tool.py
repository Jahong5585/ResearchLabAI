from datetime import datetime

from Tools.base_tool import BaseTool


class TimeTool(BaseTool):

    NAME = "TimeTool"

    def execute(self):

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")