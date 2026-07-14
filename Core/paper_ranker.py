import math
import re
from datetime import datetime
from typing import Any


class PaperRanker:
    """
    Deterministic scientific-paper ranking.

    The score considers:

    - thematic relevance to the research query;
    - title relevance;
    - abstract relevance;
    - citation count;
    - publication recency;
    - DOI availability;
    - abstract completeness;
    - study design;
    - publication-source type.

    No LLM or paid API is used.
    """

    TOKEN_PATTERN = re.compile(
        r"[A-Za-zА-Яа-яЁё0-9]"
        r"[A-Za-zА-Яа-яЁё0-9+.#_-]*"
    )

    STOP_WORDS = {
        # English
        "a",
        "an",
        "and",
        "about",
        "article",
        "articles",
        "effect",
        "effects",
        "for",
        "in",
        "impact",
        "of",
        "on",
        "paper",
        "papers",
        "research",
        "review",
        "role",
        "study",
        "studies",
        "the",
        "to",
        "use",
        "using",
        "with",

        # Russian
        "анализ",
        "в",
        "влияние",
        "для",
        "и",
        "исследование",
        "исследования",
        "на",
        "об",
        "обзор",
        "о",
        "по",
        "применение",
        "применения",
        "роль",
        "статья",
        "статьи",
    }

    TOKEN_ALIASES = {
        "students": "student",
        "learners": "student",
        "learner": "student",
        "pupils": "student",
        "educational": "education",
        "universities": "university",
        "colleges": "college",
        "writings": "writing",
        "technologies": "technology",
        "models": "model",
        "algorithms": "algorithm",
        "teachers": "teacher",
        "instructors": "teacher",
        "educators": "teacher",
        "challenges": "challenge",
        "risks": "risk",
        "outcomes": "outcome",
    }

    PREPRINT_MARKERS = {
        "ssrn",
        "osf",
        "arxiv",
        "preprint",
        "research square",
        "medrxiv",
        "biorxiv",
    }

    CONFERENCE_MARKERS = {
        "conference",
        "proceedings",
        "symposium",
        "annual meeting",
        "workshop",
    }

    STUDY_DESIGN_SCORES = (
        (
            (
                "meta-analysis",
                "meta analysis",
                "мета-анализ",
            ),
            3.5,
        ),
        (
            (
                "systematic review",
                "систематический обзор",
            ),
            3.0,
        ),
        (
            (
                "randomized controlled trial",
                "randomised controlled trial",
                "controlled experiment",
            ),
            3.0,
        ),
        (
            (
                "experimental study",
                "experiment",
                "эксперимент",
            ),
            2.0,
        ),
        (
            (
                "mixed methods",
                "mixed-methods",
                "смешанные методы",
            ),
            1.5,
        ),
        (
            (
                "longitudinal",
                "лонгитюд",
            ),
            1.5,
        ),
        (
            (
                "survey",
                "questionnaire",
                "опрос",
            ),
            1.0,
        ),
        (
            (
                "scoping review",
                "rapid review",
                "literature review",
            ),
            1.0,
        ),
        (
            (
                "case study",
                "кейс",
            ),
            0.75,
        ),
    )

    def calculate(
        self,
        paper,
        query: str = "",
    ) -> float:
        """
        Return the total ranking score.

        The query argument is optional to preserve compatibility
        with the existing RankingAgent.
        """

        breakdown = self.explain(
            paper,
            query,
        )

        return round(
            breakdown["total_score"],
            2,
        )

    def explain(
        self,
        paper,
        query: str = "",
    ) -> dict[str, float]:
        """
        Return a transparent score breakdown for diagnostics.
        """

        title = self._text(
            getattr(
                paper,
                "title",
                "",
            )
        )

        abstract = self._text(
            getattr(
                paper,
                "abstract",
                "",
            )
        )

        journal = self._text(
            getattr(
                paper,
                "journal",
                "",
            )
        )

        doi = self._text(
            getattr(
                paper,
                "doi",
                "",
            )
        )

        citations = self._to_int(
            getattr(
                paper,
                "citations",
                0,
            )
        )

        year = self._to_int(
            getattr(
                paper,
                "year",
                0,
            )
        )

        relevance_score = self._relevance_score(
            query=query,
            title=title,
            abstract=abstract,
        )

        citation_score = self._citation_score(
            citations
        )

        recency_score = self._recency_score(
            year
        )

        doi_score = 1.5 if doi else 0.0

        abstract_score = self._abstract_score(
            abstract
        )

        study_design_score = self._study_design_score(
            title,
            abstract,
        )

        source_score = self._source_score(
            title=title,
            abstract=abstract,
            journal=journal,
        )

        total_score = (
            relevance_score
            + citation_score
            + recency_score
            + doi_score
            + abstract_score
            + study_design_score
            + source_score
        )

        return {
            "relevance": round(
                relevance_score,
                2,
            ),
            "citations": round(
                citation_score,
                2,
            ),
            "recency": round(
                recency_score,
                2,
            ),
            "doi": round(
                doi_score,
                2,
            ),
            "abstract": round(
                abstract_score,
                2,
            ),
            "study_design": round(
                study_design_score,
                2,
            ),
            "source_type": round(
                source_score,
                2,
            ),
            "total_score": round(
                total_score,
                2,
            ),
        }

    def _relevance_score(
        self,
        query: str,
        title: str,
        abstract: str,
    ) -> float:
        query_tokens = self._tokens(
            query
        )

        if not query_tokens:
            return 0.0

        title_tokens = self._tokens(
            title
        )

        abstract_tokens = self._tokens(
            abstract
        )

        query_set = set(
            query_tokens
        )

        title_set = set(
            title_tokens
        )

        abstract_set = set(
            abstract_tokens
        )

        title_hits = (
            query_set
            & title_set
        )

        abstract_hits = (
            query_set
            & abstract_set
        )

        combined_hits = (
            query_set
            & (
                title_set
                | abstract_set
            )
        )

        query_count = max(
            len(query_set),
            1,
        )

        title_coverage = (
            len(title_hits)
            / query_count
        )

        abstract_coverage = (
            len(abstract_hits)
            / query_count
        )

        combined_coverage = (
            len(combined_hits)
            / query_count
        )

        score = (
            title_coverage * 8.0
            + abstract_coverage * 5.0
            + combined_coverage * 4.0
        )

        query_bigrams = self._bigrams(
            query_tokens
        )

        if query_bigrams:
            title_bigrams = self._bigrams(
                title_tokens
            )

            abstract_bigrams = self._bigrams(
                abstract_tokens
            )

            title_bigram_coverage = (
                len(
                    query_bigrams
                    & title_bigrams
                )
                / len(query_bigrams)
            )

            abstract_bigram_coverage = (
                len(
                    query_bigrams
                    & abstract_bigrams
                )
                / len(query_bigrams)
            )

            score += (
                title_bigram_coverage * 3.0
                + abstract_bigram_coverage * 1.5
            )

        if not combined_hits:
            score -= 8.0
        elif combined_coverage < 0.4:
            score -= 2.0

        return max(
            -8.0,
            min(
                score,
                20.0,
            ),
        )

    @staticmethod
    def _citation_score(
        citations: int,
    ) -> float:
        if citations <= 0:
            return 0.0

        return min(
            math.log10(
                citations + 1
            ) * 1.8,
            5.0,
        )

    @staticmethod
    def _recency_score(
        year: int,
    ) -> float:
        if year <= 0:
            return 0.0

        current_year = (
            datetime.now().year
        )

        age = max(
            0,
            current_year - year,
        )

        return max(
            0.0,
            4.0 - age * 0.35,
        )

    @staticmethod
    def _abstract_score(
        abstract: str,
    ) -> float:
        word_count = len(
            abstract.split()
        )

        if word_count >= 150:
            return 2.0

        if word_count >= 75:
            return 1.5

        if word_count >= 30:
            return 1.0

        if word_count > 0:
            return 0.5

        return 0.0

    def _study_design_score(
        self,
        title: str,
        abstract: str,
    ) -> float:
        text = (
            f"{title} {abstract}"
        ).casefold()

        scores = []

        for markers, score in self.STUDY_DESIGN_SCORES:
            if any(
                marker in text
                for marker in markers
            ):
                scores.append(
                    score
                )

        if not scores:
            return 0.0

        return max(
            scores
        )

    def _source_score(
        self,
        title: str,
        abstract: str,
        journal: str,
    ) -> float:
        text = (
            f"{title} {abstract} {journal}"
        ).casefold()

        score = 0.0

        if journal:
            score += 1.0

        if any(
            marker in text
            for marker in self.PREPRINT_MARKERS
        ):
            score -= 2.5

        if any(
            marker in text
            for marker in self.CONFERENCE_MARKERS
        ):
            score -= 1.0

        return score

    def _tokens(
        self,
        text: str,
    ) -> list[str]:
        raw_tokens = self.TOKEN_PATTERN.findall(
            self._text(text).casefold()
        )

        tokens = []

        for raw_token in raw_tokens:
            token = raw_token.strip(
                "._-"
            )

            if not token:
                continue

            if token in self.STOP_WORDS:
                continue

            token = self.TOKEN_ALIASES.get(
                token,
                token,
            )

            if token not in tokens:
                tokens.append(
                    token
                )

        return tokens

    @staticmethod
    def _bigrams(
        tokens: list[str],
    ) -> set[str]:
        return {
            f"{tokens[index]} {tokens[index + 1]}"
            for index in range(
                len(tokens) - 1
            )
        }

    @staticmethod
    def _text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        return str(
            value
        ).strip()

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int:
        try:
            return int(
                value or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0