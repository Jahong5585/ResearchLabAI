import os

from dotenv import load_dotenv

from Config.settings import OPENROUTER_MODEL


load_dotenv()


def ask(prompt, system_prompt="", model=None):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing. Add it to the local .env file."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required for the OpenRouter provider. "
            "Run: pip install -r requirements.txt"
        ) from exc

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    try:
        response = client.chat.completions.create(
            model=model or OPENROUTER_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=4096,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("OpenRouter returned an empty response.")

    return content
