from Config.settings import CURRENT_PROVIDER

from Providers.ollama_provider import ask as ollama_ask
from Providers.openai_provider import ask as openai_ask
from Providers.gemini_provider import ask as gemini_ask
from Providers.openrouter_provider import ask as openrouter_ask


def ask(prompt, system_prompt="", model=None):

    if CURRENT_PROVIDER == "ollama":
        return ollama_ask(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model
        )

    elif CURRENT_PROVIDER == "openai":
        return openai_ask(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model
        )

    elif CURRENT_PROVIDER == "gemini":
        return gemini_ask(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model
        )

    elif CURRENT_PROVIDER == "openrouter":
        return openrouter_ask(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model
        )

    else:
        return "Неизвестный провайдер."