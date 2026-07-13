import os

import pytest


def test_openrouter_provider_integration():
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY is not configured")

    pytest.importorskip("openai")
    from Providers.openrouter_provider import ask

    answer = ask("Ответь одним словом. Работает?")
    assert isinstance(answer, str)
    assert answer.strip()
