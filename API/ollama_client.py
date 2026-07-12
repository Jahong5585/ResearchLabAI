from ollama import chat


def ask_ollama(prompt: str):
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":
    answer = ask_ollama("Привет! Представься.")
    print(answer)