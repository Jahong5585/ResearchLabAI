_tools = {}


def register(name, tool):
    _tools[name] = tool


def get(name):
    return _tools.get(name)


def list_tools():
    return list(_tools.keys())
