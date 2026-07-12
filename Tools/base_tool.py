class BaseTool:

    NAME = ""

    def execute(self, *args, **kwargs):
        raise NotImplementedError
    