import os

from dotenv import load_dotenv
from google import genai

from Config.settings import GEMINI_MODEL


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask(prompt, system_prompt="", model=None):

    try:

        full_prompt = prompt

        if system_prompt:

            full_prompt = (
                system_prompt
                + "\n\n"
                + prompt
            )

        response = client.models.generate_content(

            model=model or GEMINI_MODEL,

            contents=full_prompt

        )

        return response.text

    except Exception as e:

        return f"Gemini error: {e}"