import re


class CitationValidator:

    @staticmethod
    def validate(text, task):

        errors = []

        numbers = set()

        for match in re.findall(r"ARTICLE\s+(\d+)", text):

            numbers.add(int(match))

        max_articles = len(task.article_summaries)

        for number in sorted(numbers):

            if number < 1 or number > max_articles:

                errors.append(
                    f"ARTICLE {number} отсутствует."
                )

        return errors