def choose_agent(task: str):

    task = task.lower()

    programmer = [
        "код",
        "python",
        "программа",
        "скрипт",
        "бот",
        "api",
        "flask",
        "fastapi",
        "django"
    ]

    translator = [
        "переведи",
        "translate",
        "перевод"
    ]

    researcher = [
        "исследуй",
        "исследование",
        "обзор литературы",
        "литература",
        "научная статья",
        "научные статьи",
        "doi",
        "pubmed",
        "crossref",
        "обзор",
        "article",
        "paper",
        "journal",
        "диссертация"
    ]

    if any(x in task for x in programmer):
        return "Programmer"

    if any(x in task for x in translator):
        return "Translator"

    if any(x in task for x in researcher):
        return "Researcher"

    return "Writer"