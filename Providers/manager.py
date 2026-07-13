from Config.settings import CURRENT_PROVIDER


def ask(prompt, system_prompt="", model=None):
    """Call only the configured provider.

    Imports are intentionally lazy. The application can therefore use
    OpenRouter without requiring Ollama, Gemini, and OpenAI SDKs to import
    successfully at startup.
    """

    if CURRENT_PROVIDER == "ollama":
        from Providers.ollama_provider import ask as provider_ask
    elif CURRENT_PROVIDER == "openai":
        from Providers.openai_provider import ask as provider_ask
    elif CURRENT_PROVIDER == "gemini":
        from Providers.gemini_provider import ask as provider_ask
    elif CURRENT_PROVIDER == "openrouter":
        from Providers.openrouter_provider import ask as provider_ask
    else:
        raise ValueError(f"Unknown provider: {CURRENT_PROVIDER}")

    return provider_ask(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
    )
