import json

from Agents.base_agent import BaseAgent
from Core.event_logger import log


class WriterAgent(BaseAgent):
    """
    Converts validated cross-paper synthesis into an academic
    literature review.

    Writer does not search for information and does not independently
    analyze the original articles.
    """

    PROMPT_NAME = "writer"
    MODEL_NAME = "WRITER_MODEL"

    def execute(self, task):
        report = task.synthesis_report
        summaries = task.article_summaries or []

        if not summaries:
            task.literature_review = (
                "Нет данных для построения обзора литературы."
            )
            task.result = task.literature_review
            return task.literature_review

        if report is None:
            task.literature_review = (
                "Аналитический синтез не выполнен. Writer не может "
                "самостоятельно анализировать статьи."
            )
            task.result = task.literature_review
            return task.literature_review

        if not report.claims:
            task.literature_review = (
                "Synthesis Report не содержит проверенных аналитических "
                "утверждений. Написание обзора остановлено во избежание "
                "неподтверждённых выводов."
            )
            task.result = task.literature_review
            return task.literature_review

        log(
            "Writer",
            (
                f"Получено claims: {len(report.claims)}; "
                f"методологических паттернов: "
                f"{len(report.methodology_patterns)}; "
                f"тенденций: {len(report.trends)}; "
                f"противоречий: {len(report.contradictions)}; "
                f"пробелов: {len(report.gaps)}; "
                f"повторяющихся ограничений: "
                f"{len(report.recurring_limitations)}"
            ),
        )

        context = self._build_context(task)

        prompt = f"""
Write a coherent academic literature review for the user's request.

Write in the same language as the user's request.

The scientific comparison has already been completed by the Synthesis Agent.
You must not perform a new analysis of the original articles.

MANDATORY COVERAGE RULES

1. Use every valid item in SYNTHESIS CLAIMS.
2. Do not omit a synthesis claim merely to make the review shorter.
3. Compatible claims may be combined in one paragraph, but the meaning,
   confidence, caveats and article numbers of every claim must be preserved.
4. SYNTHESIS CLAIMS are the only source for analytical conclusions.
5. METHODOLOGY PATTERNS, TRENDS, CONTRADICTIONS, GAPS and
   RECURRING LIMITATIONS may be used to organize sections, but they must
   not be converted into unsupported conclusions.
6. When an auxiliary pattern is supported by a SYNTHESIS CLAIM, present it
   using the citations supplied with that claim.
7. Do not invent article numbers for auxiliary patterns.
8. Do not use external knowledge.

CITATION RULES

9. Every analytical statement derived from a synthesis claim must contain
   citations in this exact form:
   [ARTICLE 1; ARTICLE 2]

10. Use supporting article numbers exactly as supplied.
11. If contradicting article numbers are supplied, explain the disagreement
    and cite both groups.
12. Do not add an article to a citation unless it is supplied by the relevant
    synthesis claim.
13. For corpus-level statements derived from AGGREGATE STATISTICS, use the
    exact citation provided in ALL_ARTICLES_CITATION.
14. Never print the words ALL_ARTICLES_CITATION or ALL_ARTICLE_NUMBERS
    in the finished review.

ACADEMIC WRITING RULES

15. Avoid an article-by-article catalogue.
16. Organize paragraphs around:
    - agreements and majority patterns;
    - applications and outcomes;
    - methodological patterns;
    - temporal, geographical or population differences;
    - contradictions;
    - recurring limitations;
    - evidence gaps.

17. Do not write a section for a category when the supplied context contains
    no supported information for that category.
18. Clearly distinguish strong evidence from evidence based on one article.
19. Preserve all caveats and confidence levels.
20. Do not strengthen tentative or low-confidence conclusions.
21. Do not invent causes, results, percentages, sample sizes, countries,
    models, methods, years, authors, journals or DOI values.
22. Do not repeat the same conclusion in multiple sections.
23. Produce a developed academic review, not a short abstract.
24. Include an introduction, analytical thematic sections, limitations of
    the available evidence, research gaps, a conclusion and references.
25. Use only REFERENCE METADATA for the reference list.
26. Include every reference that is cited in the review.
27. Do not include uncited references.

USER REQUEST

{task.user_request}

VALIDATED RESEARCH CONTEXT

{context}
"""

        answer = self.ask_llm(prompt)

        # Deterministic protection against unresolved service placeholders.
        all_articles_citation = self._build_all_articles_citation(
            len(summaries)
        )

        answer = answer.replace(
            "[ALL_ARTICLE_NUMBERS]",
            all_articles_citation,
        )

        answer = answer.replace(
            "ALL_ARTICLE_NUMBERS",
            all_articles_citation,
        )

        answer = answer.replace(
            "[ALL_ARTICLES_CITATION]",
            all_articles_citation,
        )

        answer = answer.replace(
            "ALL_ARTICLES_CITATION",
            all_articles_citation,
        )

        task.literature_review = answer
        task.result = answer

        log(
            "Writer",
            f"Обзор создан. Длина: {len(answer)} символов.",
        )

        return answer

    @staticmethod
    def _build_context(task) -> str:
        report = task.synthesis_report
        summaries = task.article_summaries or []

        claims = []

        for number, claim in enumerate(report.claims, start=1):
            claims.append(
                {
                    "claim_number": number,
                    "claim_type": claim.claim_type,
                    "statement": claim.statement,
                    "supporting_articles": claim.supporting_articles,
                    "contradicting_articles": (
                        claim.contradicting_articles
                    ),
                    "confidence": claim.confidence,
                    "rationale": claim.rationale,
                    "caveats": claim.caveats,
                }
            )

        outline = []

        for section in task.outline or []:
            outline.append(
                {
                    "title": section.title,
                    "description": section.description,
                }
            )

        references = []

        for number, article in enumerate(summaries, start=1):
            references.append(
                {
                    "article_number": number,
                    "title": article.title,
                    "authors": article.authors,
                    "journal": article.journal,
                    "year": article.year,
                    "doi": article.doi,
                }
            )

        all_article_numbers = list(
            range(
                1,
                len(summaries) + 1,
            )
        )

        all_articles_citation = (
            WriterAgent._build_all_articles_citation(
                len(summaries)
            )
        )

        data = {
            "search_query": task.memory.get(
                "search_query",
                "",
            ),
            "all_article_numbers": all_article_numbers,
            "all_articles_citation": all_articles_citation,
            "outline": outline,
            "synthesis_overview": report.overview,
            "synthesis_claims": claims,
            "methodology_patterns": report.methodology_patterns,
            "trends": report.trends,
            "contradictions": report.contradictions,
            "gaps": report.gaps,
            "recurring_limitations": (
                report.recurring_limitations
            ),
            "aggregate_statistics": (
                report.aggregate_statistics
            ),
            "reference_metadata": references,
        }

        return json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def _build_all_articles_citation(article_count: int) -> str:
        if article_count <= 0:
            return ""

        article_markers = [
            f"ARTICLE {number}"
            for number in range(1, article_count + 1)
        ]

        return f"[{'; '.join(article_markers)}]"