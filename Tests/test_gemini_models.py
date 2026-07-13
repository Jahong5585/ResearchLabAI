import os

import pytest


def test_gemini_model_listing_integration():
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured")

    genai = pytest.importorskip("google.genai")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    models = list(client.models.list())

    assert isinstance(models, list)
