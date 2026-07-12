import os

from dotenv import load_dotenv
from openai import OpenAI

from Config.settings import OPENROUTER_MODEL


load_dotenv()


client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)


def ask(prompt, system_prompt="", model=None):

    try:

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

        response = client.chat.completions.create(

            model=model or OPENROUTER_MODEL,

            messages=messages,

            temperature=0.2,

            max_tokens=2048

        )

        return response.choices[0].message.content

    except Exception as e:

        return f"OpenRouter error: {e}"