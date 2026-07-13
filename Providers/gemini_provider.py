import os

from dotenv import load_dotenv

from Config.settings import GEMINI_MODEL


load_dotenv()


def ask(prompt, system_prompt="", model=None):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the local .env file."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "The 'google-genai' package is required for the Gemini provider. "
            "Run: pip install -r requirements.txt"
        ) from exc

    client = genai.Client(api_key=api_key)
    full_prompt = prompt

    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"

    try:
        response = client.models.generate_content(
            model=model or GEMINI_MODEL,
            contents=full_prompt,
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
