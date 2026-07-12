import re


class OutputCleaner:

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        # Удаляем длинные последовательности нулей
        text = re.sub(r"0{10,}", "", text)

        # Удаляем длинные последовательности одинаковых символов
        text = re.sub(r"(.)\1{15,}", r"\1", text)

        # Удаляем китайские символы (часто появляются как мусор)
        text = re.sub(r"[\u4e00-\u9fff]+", "", text)

        # Удаляем лишние пустые строки
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Удаляем пробелы в конце строк
        lines = [line.rstrip() for line in text.splitlines()]

        text = "\n".join(lines)

        return text.strip()