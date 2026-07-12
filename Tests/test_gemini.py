from Providers.gemini_provider import ask


def main():

    answer = ask(
        "Ответь одним словом. Работает?"
    )

    print(answer)


if __name__ == "__main__":
    main()