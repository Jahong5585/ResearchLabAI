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
        ("рак", "Cancer")
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
        "как"
    }

    def optimize(self, query: str):

        text = query.lower()

        for source, target in self.PHRASES:
            text = text.replace(source, target)

        words = re.findall(r"[A-Za-z]+", text)

        return " ".join(words)