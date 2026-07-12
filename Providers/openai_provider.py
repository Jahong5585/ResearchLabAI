from Config.settings import OPENAI_MODEL


def ask(prompt, system_prompt="", model=None):

    return (
        "OpenAI пока не подключен. "
        f"Запрошенная модель: {model or OPENAI_MODEL}"
    )