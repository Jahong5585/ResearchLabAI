from ollama import chat

from Config.settings import OLLAMA_MODEL


def ask(prompt, system_prompt="", model=None):

    messages = []

    if system_prompt:

        messages.append(
            {
                "role": "system",
                "content": system_prompt
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    response = chat(

        model=model or OLLAMA_MODEL,

        messages=messages

    )

    return response["message"]["content"]