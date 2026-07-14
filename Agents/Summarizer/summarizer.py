from Agents.base_agent import BaseAgent

from Core.article_summary_parser import ArticleSummaryParser
from Core.comparison_matrix_builder import ComparisonMatrixBuilder
from Core.evidence_builder import EvidenceBuilder
from Core.event_logger import log


class Summarizer(BaseAgent):
    """
    Analyzes every selected publication separately.

    The agent extracts structured information from bibliographic metadata
    and the available abstract. After extraction, a deterministic comparison
    matrix is created without an additional LLM call.
    """

    PROMPT_NAME = "summarizer"
    MODEL_NAME = "SUMMARIZER_MODEL"

    def execute(self, task):
        summaries = []

        for key in (
            "article_summaries",
            "comparison_matrix",
            "keywords",
            "methodologies",
            "findings",
            "limitations",
            "conclusions",
        ):
            task.memory.remove(key)

        papers = task.papers.get_all()

        log(
            "Summarizer",
            f"Получено статей для анализа: {len(papers)}",
        )

        for article_number, paper in enumerate(
            papers,
            start=1,
        ):
            prompt = f"""
Analyze the following scientific publication metadata and abstract.

This is ARTICLE {article_number} in the current research corpus.

Title:
{paper.title}

Authors:
{", ".join(paper.authors)}

Journal:
{paper.journal}

Year:
{paper.year}

DOI:
{paper.doi}

Abstract:
{paper.abstract}
"""

            answer = self.ask_llm(prompt)

            summary = ArticleSummaryParser.parse(
                answer,
                paper,
            )

            summaries.append(summary)

            task.memory.add_article_summary(
                summary
            )

            for keyword in summary.keywords:
                task.memory.add_keyword(
                    keyword
                )

            task.memory.add_methodology(
                summary.methodology
            )

            task.memory.add_finding(
                summary.findings
            )

            task.memory.add_limitation(
                summary.limitations
            )

            task.memory.add_conclusion(
                summary.conclusion
            )

            task.memory.add_research_objective(
                summary.research_objective
            )

            task.memory.add_study_type(
                summary.study_type
            )

            task.memory.add_result(
                summary.results
            )

            task.memory.add_strength(
                summary.strengths
            )

            task.memory.add_weakness(
                summary.weaknesses
            )

            task.memory.add_practical_implication(
                summary.practical_implications
            )

            task.memory.add_future_research(
                summary.future_research
            )

            for fact in summary.verified_facts:
                task.memory.add_verified_fact(
                    fact
                )

            log(
                "Summarizer",
                (
                    f"ARTICLE {article_number} обработана: "
                    f"{summary.title}"
                ),
            )

        task.article_summaries = summaries

        task.comparison_matrix = (
            ComparisonMatrixBuilder.build(
                summaries
            )
        )

        task.memory.set(
            "comparison_matrix",
            task.comparison_matrix,
        )

        task.evidences = EvidenceBuilder.build(
            summaries
        )

        task.result = summaries

        evidence_levels = {}

        for row in task.comparison_matrix:
            level = row.get(
                "abstract_evidence_level",
                "Unknown",
            )

            evidence_levels[level] = (
                evidence_levels.get(
                    level,
                    0,
                )
                + 1
            )

        log(
            "Summarizer",
            f"Summaries создано: {len(summaries)}",
        )

        log(
            "Summarizer",
            (
                "Comparison Matrix создана: "
                f"{len(task.comparison_matrix)} строк"
            ),
        )

        log(
            "Summarizer",
            (
                "Уровни пригодности доказательств по аннотациям: "
                f"{evidence_levels}"
            ),
        )

        return summaries