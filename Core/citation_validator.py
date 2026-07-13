import re


class CitationValidator:
    """
    Validates citation markers in the literature-review body.

    Required citation format:

        [ARTICLE 1]
        [ARTICLE 1; ARTICLE 2]

    Numbered entries inside the reference list, such as [1], are not
    treated as in-text citation errors.
    """

    REFERENCE_HEADING_PATTERN = re.compile(
        r"(?im)^\s*"
        r"(?:#{1,6}\s*)?"
        r"(?:список литературы|литература|references|bibliography)"
        r"\s*:?\s*$"
    )

    VALID_CITATION_PATTERN = re.compile(
        r"\[\s*"
        r"ARTICLE\s+\d+"
        r"(?:\s*;\s*ARTICLE\s+\d+)*"
        r"\s*\]",
        re.IGNORECASE,
    )

    VALID_CITATION_CONTENT_PATTERN = re.compile(
        r"ARTICLE\s+\d+"
        r"(?:\s*;\s*ARTICLE\s+\d+)*",
        re.IGNORECASE,
    )

    ARTICLE_NUMBER_PATTERN = re.compile(
        r"ARTICLE\s+(\d+)",
        re.IGNORECASE,
    )

    NUMERIC_CITATION_PATTERN = re.compile(
        r"\d+(?:\s*;\s*\d+)*"
    )

    @classmethod
    def validate(cls, text, task):
        errors = []

        if not isinstance(text, str) or not text.strip():
            return ["Текст обзора отсутствует."]

        article_count = len(task.article_summaries)

        body = cls._get_review_body(text)

        cls._validate_placeholders(
            body,
            article_count,
            errors,
        )

        cls._validate_citation_blocks(
            body,
            article_count,
            errors,
        )

        return cls._remove_duplicates(errors)

    @classmethod
    def _get_review_body(cls, text):
        """
        Removes the reference-list section from citation-format checking.

        This prevents bibliography numbering such as [1], [2], [3]
        from being mistaken for incorrect in-text citations.
        """

        heading_match = cls.REFERENCE_HEADING_PATTERN.search(text)

        if heading_match is None:
            return text

        return text[:heading_match.start()]

    @classmethod
    def _validate_placeholders(
        cls,
        body,
        article_count,
        errors,
    ):
        if "ALL_ARTICLE_NUMBERS" not in body:
            return

        if article_count > 0:
            expected = "; ".join(
                f"ARTICLE {number}"
                for number in range(1, article_count + 1)
            )

            replacement = f"[{expected}]"
        else:
            replacement = "удалить маркер"

        errors.append(
            "Обнаружен служебный маркер [ALL_ARTICLE_NUMBERS]. "
            f"Необходимо заменить его на {replacement}."
        )

    @classmethod
    def _validate_citation_blocks(
        cls,
        body,
        article_count,
        errors,
    ):
        citation_blocks = re.findall(
            r"\[([^\[\]]+)\]",
            body,
        )

        for raw_content in citation_blocks:
            content = raw_content.strip()

            if not content:
                continue

            if content == "ALL_ARTICLE_NUMBERS":
                continue

            if cls.NUMERIC_CITATION_PATTERN.fullmatch(content):
                errors.append(
                    f"Неправильный формат внутритекстовой ссылки: "
                    f"[{content}]. Требуется формат "
                    "[ARTICLE 1; ARTICLE 2]."
                )
                continue

            contains_article_marker = bool(
                re.search(
                    r"\bARTICLE\b",
                    content,
                    re.IGNORECASE,
                )
            )

            if not contains_article_marker:
                continue

            if not cls.VALID_CITATION_CONTENT_PATTERN.fullmatch(
                content
            ):
                errors.append(
                    f"Неправильный формат ссылки: [{content}]. "
                    "Допустимый формат: "
                    "[ARTICLE 1; ARTICLE 2]."
                )
                continue

            numbers = [
                int(number)
                for number in cls.ARTICLE_NUMBER_PATTERN.findall(
                    content
                )
            ]

            for number in numbers:
                if number < 1 or number > article_count:
                    errors.append(
                        f"ARTICLE {number} отсутствует. "
                        f"Допустимый диапазон: "
                        f"ARTICLE 1–ARTICLE {article_count}."
                    )

    @staticmethod
    def _remove_duplicates(errors):
        unique_errors = []

        for error in errors:
            if error not in unique_errors:
                unique_errors.append(error)

        return unique_errors