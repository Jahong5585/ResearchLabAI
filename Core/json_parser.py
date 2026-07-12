import json
import re


def parse_json(text: str):

    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    text = re.sub(r'"\s+"title"', '"title"', text)

    return json.loads(text)