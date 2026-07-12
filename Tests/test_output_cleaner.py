from Core.output_cleaner import OutputCleaner


def main():

    text = """
Это тест.

образ九江

000000000000000000000000000000000000000

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Конец.
"""

    print(OutputCleaner.clean(text))


if __name__ == "__main__":
    main()