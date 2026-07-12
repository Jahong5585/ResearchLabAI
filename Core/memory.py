class Memory:

    def __init__(self):

        self._data = {}

    # ==================================================
    # BASIC
    # ==================================================

    def set(self, key, value):

        self._data[key] = value

    def get(self, key, default=None):

        return self._data.get(key, default)

    def has(self, key):

        return key in self._data

    def remove(self, key):

        if key in self._data:

            del self._data[key]

    def clear(self):

        self._data.clear()

    def keys(self):

        return list(self._data.keys())

    def items(self):

        return self._data.items()

    def all(self):

        return self._data

    # ==================================================
    # ARTICLE SUMMARIES
    # ==================================================

    def add_article_summary(self, summary):

        self._data.setdefault(
            "article_summaries",
            []
        ).append(summary)

    def get_article_summaries(self):

        return self._data.get(
            "article_summaries",
            []
        )

    # ==================================================
    # KEYWORDS
    # ==================================================

    def add_keyword(self, keyword):

        if not keyword or keyword == "Not specified":
            return

        self._data.setdefault(
            "keywords",
            set()
        ).add(keyword)

    def get_keywords(self):

        return sorted(

            list(

                self._data.get(
                    "keywords",
                    set()
                )

            )

        )

    # ==================================================
    # METHODOLOGIES
    # ==================================================

    def add_methodology(self, methodology):

        if not methodology or methodology == "Not specified":
            return

        self._data.setdefault(
            "methodologies",
            []
        ).append(methodology)

    def get_methodologies(self):

        return self._data.get(
            "methodologies",
            []
        )

    # ==================================================
    # FINDINGS
    # ==================================================

    def add_finding(self, finding):

        if not finding or finding == "Not specified":
            return

        self._data.setdefault(
            "findings",
            []
        ).append(finding)

    def get_findings(self):

        return self._data.get(
            "findings",
            []
        )

    # ==================================================
    # LIMITATIONS
    # ==================================================

    def add_limitation(self, limitation):

        if not limitation or limitation == "Not specified":
            return

        self._data.setdefault(
            "limitations",
            []
        ).append(limitation)

    def get_limitations(self):

        return self._data.get(
            "limitations",
            []
        )

    # ==================================================
    # CONCLUSIONS
    # ==================================================

    def add_conclusion(self, conclusion):

        if not conclusion or conclusion == "Not specified":
            return

        self._data.setdefault(
            "conclusions",
            []
        ).append(conclusion)

    def get_conclusions(self):

        return self._data.get(
            "conclusions",
            []
        )

    # ==================================================
    # RESEARCH OBJECTIVES
    # ==================================================

    def add_research_objective(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "research_objectives",
            []
        ).append(value)

    def get_research_objectives(self):

        return self._data.get(
            "research_objectives",
            []
        )

    # ==================================================
    # STUDY TYPES
    # ==================================================

    def add_study_type(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "study_types",
            []
        ).append(value)

    def get_study_types(self):

        return self._data.get(
            "study_types",
            []
        )

    # ==================================================
    # RESULTS
    # ==================================================

    def add_result(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "results",
            []
        ).append(value)

    def get_results(self):

        return self._data.get(
            "results",
            []
        )

    # ==================================================
    # STRENGTHS
    # ==================================================

    def add_strength(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "strengths",
            []
        ).append(value)

    def get_strengths(self):

        return self._data.get(
            "strengths",
            []
        )

    # ==================================================
    # WEAKNESSES
    # ==================================================

    def add_weakness(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "weaknesses",
            []
        ).append(value)

    def get_weaknesses(self):

        return self._data.get(
            "weaknesses",
            []
        )

    # ==================================================
    # PRACTICAL IMPLICATIONS
    # ==================================================

    def add_practical_implication(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "practical_implications",
            []
        ).append(value)

    def get_practical_implications(self):

        return self._data.get(
            "practical_implications",
            []
        )

    # ==================================================
    # FUTURE RESEARCH
    # ==================================================

    def add_future_research(self, value):

        if not value or value == "Not specified":
            return

        self._data.setdefault(
            "future_research",
            []
        ).append(value)

    def get_future_research(self):

        return self._data.get(
            "future_research",
            []
        )

    # ==================================================
    # VERIFIED FACTS
    # ==================================================

    def add_verified_fact(self, fact):

        if not fact or fact == "Not specified":
            return

        self._data.setdefault(
            "verified_facts",
            []
        ).append(fact)

    def get_verified_facts(self):

        return self._data.get(
            "verified_facts",
            []
        )