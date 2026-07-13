import os

import pytest


def test_gemini_provider_integration():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured")

    pytest.importorskip("google.genai")
    from Providers.gemini_provider import ask

    answer = ask("Ответь одним словом. Работает?")
    assert isinstance(answer, str)
    assert answer.strip()
