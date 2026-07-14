import re


class QueryOptimizer:
    """
    Converts a natural-language research request into a compact
    scientific search query.

    The optimizer is deterministic and does not call an LLM,
    so it does not consume API credits.
    """

    MAX_TERMS = 16

    PHRASE_MAP = {
        # Artificial intelligence
        "генеративного искусственного интеллекта": "generative artificial intelligence",
        "генеративному искусственному интеллекту": "generative artificial intelligence",
        "генеративный искусственный интеллект": "generative artificial intelligence",
        "искусственного интеллекта": "artificial intelligence",
        "искусственному интеллекту": "artificial intelligence",
        "искусственным интеллектом": "artificial intelligence",
        "искусственном интеллекте": "artificial intelligence",
        "искусственный интеллект": "artificial intelligence",

        # Machine learning
        "машинного обучения": "machine learning",
        "машинному обучению": "machine learning",
        "машинным обучением": "machine learning",
        "машинное обучение": "machine learning",

        # Deep learning and neural networks
        "глубокого обучения": "deep learning",
        "глубокому обучению": "deep learning",
        "глубокое обучение": "deep learning",
        "нейронных сетей": "neural networks",
        "нейронными сетями": "neural networks",
        "нейронные сети": "neural networks",

        # Education
        "высшего образования": "higher education",
        "высшем образовании": "higher education",
        "высшее образование": "higher education",
        "медицинского образования": "medical education",
        "медицинском образовании": "medical education",
        "медицинское образование": "medical education",
        "дошкольного образования": "preschool education",
        "дошкольном образовании": "preschool education",
        "дошкольное образование": "preschool education",
        "начального образования": "primary education",
        "начальном образовании": "primary education",
        "начальное образование": "primary education",
        "профессионального образования": "vocational education",
        "профессиональное образование": "vocational education",
        "образовательного процесса": "educational process",
        "образовательном процессе": "educational process",
        "образовательный процесс": "educational process",

        # Academic writing and language learning
        "академического письма": "academic writing",
        "академическому письму": "academic writing",
        "академическое письмо": "academic writing",
        "иностранных языков": "foreign language learning",
        "иностранного языка": "foreign language learning",
        "изучении иностранных языков": "foreign language learning",
        "изучение иностранных языков": "foreign language learning",
        "языкового образования": "language education",
        "языковом образовании": "language education",
        "языковое образование": "language education",

        # Educational technology
        "адаптивного обучения": "adaptive learning",
        "адаптивном обучении": "adaptive learning",
        "адаптивное обучение": "adaptive learning",
        "персонализированного обучения": "personalized learning",
        "персонализированное обучение": "personalized learning",
        "автоматизированного оценивания": "automated assessment",
        "автоматизированное оценивание": "automated assessment",
        "цифровых технологий": "digital technologies",
        "цифровые технологии": "digital technologies",

        # Medical topics
        "медицинского дискурса": "medical discourse",
        "медицинском дискурсе": "medical discourse",
        "медицинский дискурс": "medical discourse",
        "врачебного дискурса": "medical discourse",
        "коммуникации врача и пациента": "doctor patient communication",
        "коммуникация врача и пациента": "doctor patient communication",
        "врач пациент": "doctor patient communication",
        "диагностики рака": "cancer diagnosis",
        "диагностике рака": "cancer diagnosis",
        "диагностика рака": "cancer diagnosis",

        # Review terminology
        "систематического обзора": "systematic review",
        "систематический обзор": "systematic review",
        "мета анализа": "meta analysis",
        "мета-анализ": "meta analysis",

        # Named AI systems
        "чат джипити": "ChatGPT",
        "чатгпт": "ChatGPT",
    }

    WORD_MAP = {
        # Application and impact
        "применение": "application",
        "применения": "application",
        "применению": "application",
        "применением": "application",
        "использование": "use",
        "использования": "use",
        "использованию": "use",
        "использованием": "use",
        "влияние": "impact",
        "влияния": "impact",
        "влиянию": "impact",
        "влиянии": "impact",
        "воздействие": "impact",
        "эффективность": "effectiveness",
        "эффективности": "effectiveness",
        "роль": "role",
        "роли": "role",

        # People
        "студенты": "students",
        "студентов": "students",
        "студентами": "students",
        "учащиеся": "learners",
        "учащихся": "learners",
        "обучающиеся": "learners",
        "обучающихся": "learners",
        "преподаватели": "teachers",
        "преподавателей": "teachers",
        "педагоги": "teachers",
        "педагогов": "teachers",
        "учителя": "teachers",
        "учителей": "teachers",
        "дети": "children",
        "детей": "children",
        "пациенты": "patients",
        "пациентов": "patients",

        # Education
        "образование": "education",
        "образования": "education",
        "образовании": "education",
        "образованию": "education",
        "обучение": "learning",
        "обучения": "learning",
        "обучении": "learning",
        "преподавание": "teaching",
        "преподавания": "teaching",

        # Research concepts
        "методология": "methodology",
        "методологии": "methodology",
        "результаты": "outcomes",
        "результатов": "outcomes",
        "риски": "risks",
        "рисков": "risks",
        "этика": "ethics",
        "этический": "ethical",
        "этические": "ethical",
        "проблемы": "challenges",
        "проблем": "challenges",

        # Linguistics
        "метафора": "metaphor",
        "метафоры": "metaphor",
        "метафор": "metaphor",
        "эвфемизм": "euphemism",
        "эвфемизмы": "euphemism",
        "эвфемизмов": "euphemism",
        "дискурс": "discourse",
        "дискурса": "discourse",
        "прагматика": "pragmatics",
        "прагматический": "pragmatic",
        "прагматические": "pragmatic",

        # Medicine
        "медицинский": "medical",
        "медицинская": "medical",
        "медицинское": "medical",
        "медицинские": "medical",
        "диагностика": "diagnosis",
        "диагностики": "diagnosis",
        "диагностике": "diagnosis",
        "рак": "cancer",
        "рака": "cancer",
        "беременность": "pregnancy",
        "беременности": "pregnancy",
    }

    STOP_WORDS = {
        # Russian task words
        "сделай",
        "сделайте",
        "напиши",
        "напишите",
        "подготовь",
        "подготовьте",
        "создай",
        "создайте",
        "покажи",
        "покажите",
        "проведи",
        "проведите",
        "дай",
        "дайте",

        # Russian document words
        "обзор",
        "обзора",
        "литературы",
        "литература",
        "исследований",
        "исследования",
        "исследование",
        "научных",
        "научной",
        "научный",
        "статей",
        "статьи",
        "статья",
        "публикаций",
        "публикации",
        "тема",
        "теме",
        "тему",

        # Russian connecting words
        "по",
        "для",
        "о",
        "об",
        "и",
        "или",
        "в",
        "во",
        "на",
        "к",
        "из",
        "с",
        "со",
        "при",
        "через",
        "между",
        "что",
        "как",
        "который",
        "которая",
        "которые",
        "современный",
        "современном",
        "современных",

        # English task and document words
        "write",
        "create",
        "prepare",
        "show",
        "provide",
        "review",
        "literature",
        "papers",
        "paper",
        "articles",
        "article",
        "publications",
        "publication",
        "research",

        # English connecting words
        "about",
        "on",
        "of",
        "the",
        "a",
        "an",
        "and",
        "or",
        "for",
        "in",
        "to",
        "with",
        "between",
    }

    TOKEN_PATTERN = re.compile(
        r"[A-Za-zА-Яа-яЁё0-9]"
        r"[A-Za-zА-Яа-яЁё0-9+.#/_-]*"
    )

    def optimize(self, query: str) -> str:
        original = self._normalize_spaces(
            str(query or "")
        )

        if not original:
            return ""

        text = original.casefold()

        text = self._replace_phrases(text)

        tokens = self.TOKEN_PATTERN.findall(text)

        optimized_terms = []
        seen_terms = set()

        for token in tokens:
            normalized_token = token.strip(
                "._-/ "
            )

            if not normalized_token:
                continue

            token_key = normalized_token.casefold()

            if token_key in self.STOP_WORDS:
                continue

            translated_token = self.WORD_MAP.get(
                token_key,
                normalized_token,
            )

            translated_key = translated_token.casefold()

            if translated_key in self.STOP_WORDS:
                continue

            if translated_key in seen_terms:
                continue

            seen_terms.add(translated_key)
            optimized_terms.append(translated_token)

            if len(optimized_terms) >= self.MAX_TERMS:
                break

        optimized = " ".join(
            optimized_terms
        ).strip()

        return optimized or original

    def _replace_phrases(self, text: str) -> str:
        phrases = sorted(
            self.PHRASE_MAP.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        result = text

        for source, target in phrases:
            pattern = (
                r"(?<![A-Za-zА-Яа-яЁё0-9])"
                + re.escape(source)
                + r"(?![A-Za-zА-Яа-яЁё0-9])"
            )

            result = re.sub(
                pattern,
                target,
                result,
                flags=re.IGNORECASE,
            )

        return result

    @staticmethod
    def _normalize_spaces(text: str) -> str:
        return " ".join(
            text.split()
        )