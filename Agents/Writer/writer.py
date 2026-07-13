import json

from Agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):
    """Convert validated synthesis claims into academic prose."""

    PROMPT_NAME = "writer"
    MODEL_NAME = "WRITER_MODEL"

    def execute(self, task):
        report = task.synthesis_report

        if not task.article_summaries:
            task.literature_review = "Нет данных для построения обзора."
            task.result = task.literature_review
            return task.literature_review

        if report is None:
            task.literature_review = (
                "Аналитический синтез не выполнен. Writer не может "
                "самостоятельно анализировать статьи."
            )
            task.result = task.literature_review
            return task.literature_review

        context = self._build_context(task)

        prompt = f"""
Write an academic literature review for the user's request.

Use only the supplied SYNTHESIS CLAIMS and AGGREGATE STATISTICS. The analysis
has already been completed by the Synthesis Agent. Your task is to organize it
into coherent academic prose.

Rules:
1. Do not create a new scientific claim.
2. Do not use external knowledge.
3. Do not change numbers, years, article numbers, methods, or conclusions.
4. Every analytical claim must cite its supplied articles in the form
   [ARTICLE 1; ARTICLE 2].
5. When contradicting articles are supplied, describe the disagreement and
   cite both supporting and contradicting articles.
6. Respect caveats and confidence levels.
7. Do not write an article-by-article catalogue unless a single study is
   uniquely relevant.
8. Prefer synthesis language such as "most studies", "a recurring pattern",
   "the evidence is mixed", and "methodological differences", but use such
   wording only when the supplied claim justifies it.
9. Include a references section using only REFERENCE METADATA.

USER REQUEST
{task.user_request}

VALIDATED RESEARCH CONTEXT
{context}
"""

        answer = self.ask_llm(prompt)
        task.literature_review = answer
        task.result = answer
        return answer

    @staticmethod
    def _build_context(task) -> str:
        report = task.synthesis_report

        claims = []

        for number, claim in enumerate(report.claims, start=1):
            claims.append(
                {
                    "claim_number": number,
                    "claim_type": claim.claim_type,
                    "statement": claim.statement,
                    "supporting_articles": claim.supporting_articles,
                    "contradicting_articles": claim.contradicting_articles,
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

        for number, article in enumerate(task.article_summaries, start=1):
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

        data = {
            "search_query": task.memory.get("search_query", ""),
            "outline": outline,
            "synthesis_overview": report.overview,
            "synthesis_claims": claims,
            "aggregate_statistics": report.aggregate_statistics,
            "reference_metadata": references,
        }

        return json.dumps(data, ensure_ascii=False, indent=2)
