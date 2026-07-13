import re


class QueryOptimizer:
    PHRASES = [
        ("искусственному интеллекту", "Artificial Intelligence"),
        ("искусственный интеллект", "Artificial Intelligence"),
        ("искусственного интеллекта", "Artificial Intelligence"),
        ("искусственном интеллекте", "Artificial Intelligence"),
        ("машинному обучению", "Machine Learning"),
        ("машинное обучение", "Machine Learning"),
        ("машинного обучения", "Machine Learning"),
        ("глубокому обучению", "Deep Learning"),
        ("глубокое обучение", "Deep Learning"),
        ("нейронные сети", "Neural Networks"),
        ("нейронных сетей", "Neural Networks"),
        ("образовании", "Education"),
        ("образование", "Education"),
        ("образования", "Education"),
        ("обучении", "Learning"),
        ("обучение", "Learning"),
        ("беременности", "Pregnancy"),
        ("беременность", "Pregnancy"),
        ("диагностике", "Diagnosis"),
        ("диагностика", "Diagnosis"),
        ("рака", "Cancer"),
        ("рак", "Cancer"),
    ]

    STOP_WORDS = {
        "сделай",
        "напиши",
        "подготовь",
        "создай",
        "покажи",
        "обзор",
        "литературы",
        "литература",
        "исследований",
        "исследование",
        "статей",
        "статьи",
        "по",
        "для",
        "о",
        "об",
        "и",
        "в",
        "на",
        "к",
        "из",
        "что",
        "как",
        "write",
        "create",
        "prepare",
        "show",
        "review",
        "literature",
        "papers",
        "articles",
        "about",
        "on",
        "of",
        "the",
        "a",
        "an",
    }

    def optimize(self, query: str) -> str:
        original = " ".join(str(query or "").split())
        text = original.lower()

        for source, target in self.PHRASES:
            text = text.replace(source, target)

        # Preserve both Latin and Cyrillic scientific terms. Crossref and
        # OpenAlex accept multilingual queries, so unknown topics must not be
        # silently deleted.
        words = re.findall(r"[A-Za-zА-Яа-яЁё0-9][A-Za-zА-Яа-яЁё0-9_-]*", text)
        useful_words = [
            word
            for word in words
            if word.lower() not in self.STOP_WORDS
        ]

        optimized = " ".join(useful_words).strip()
        return optimized or original
