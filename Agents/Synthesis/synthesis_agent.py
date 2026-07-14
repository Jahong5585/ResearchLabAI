from Agents.base_agent import BaseAgent

from Core.event_logger import log
from Core.json_parser import parse_json
from Core.synthesis_context_builder import SynthesisContextBuilder
from Core.synthesis_engine import SynthesisEngine


class SynthesisAgent(BaseAgent):
    """
    Performs cross-paper scientific synthesis before the Writer stage.

    The agent uses:

    - structured article summaries;
    - analytical outline;
    - deterministic comparison matrix.

    The comparison matrix does not require an additional LLM call.
    """

    PROMPT_NAME = "synthesis"
    MODEL_NAME = "SYNTHESIS_MODEL"

    def execute(self, task):
        summaries = task.article_summaries or []
        comparison_matrix = task.comparison_matrix or []

        log(
            "Synthesis",
            f"Получено summaries для анализа: {len(summaries)}",
        )

        if not summaries:
            report = SynthesisEngine.fallback(
                summaries=[],
                comparison_matrix=[],
            )

            task.synthesis_report = report

            task.memory.set(
                "synthesis_report",
                report,
            )

            task.result = report

            log(
                "Synthesis",
                "Нет summaries. Создан пустой резервный отчёт.",
            )

            return report

        log(
            "Synthesis",
            (
                "Получено строк Comparison Matrix: "
                f"{len(comparison_matrix)}"
            ),
        )

        context = SynthesisContextBuilder.build(
            article_summaries=summaries,
            outline=task.outline,
            comparison_matrix=comparison_matrix,
        )

        prompt = f"""
Analyze the numbered scientific article summaries and the comparison matrix.

Your task is to perform cross-paper scientific synthesis.

Use the COMPARISON MATRIX to directly compare:

- study designs;
- educational levels;
- countries and disciplines;
- participant groups;
- sample sizes;
- methodologies;
- evaluation metrics;
- reported results;
- reported limitations;
- abstract completeness;
- abstract-level evidence usability.

COMPARISON RULES

1. Compare studies by common analytical dimensions.
2. Identify which conclusions are supported by experimental,
   mixed-methods, qualitative, review or meta-analytic evidence.
3. Distinguish findings based on objective writing-performance measures
   from findings based only on student perceptions.
4. Distinguish findings based on one study from findings supported by
   several studies.
5. Identify whether stronger abstract-level evidence supports the same
   conclusions as records with limited abstract-level evidence.
6. Identify methodological heterogeneity that may explain differences
   between findings.
7. Identify areas where direct comparison is impossible because the
   available abstracts do not report compatible data.
8. Do not treat missing abstract information as a weakness of the
   complete original article.
9. Do not use abstract_evidence_level as a full risk-of-bias assessment.
10. Do not claim that one publication is scientifically superior solely
    because its abstract contains more information.

EVIDENCE RULES

11. Use only the supplied records.
12. Do not use external knowledge.
13. Every analytical claim must list the exact supporting article numbers.
14. If comparable articles report opposing results, list the
    contradicting article numbers separately.
15. Do not cite an article merely because it is related to the topic.
16. Preserve all numbers, percentages, sample sizes and years exactly.
17. Do not combine numerical results from different publications.
18. A claim supported by one article must remain explicitly limited to
    one article.
19. Do not treat different populations, outcomes, educational levels,
    countries, timepoints or methodologies as direct contradictions.
20. Return only one valid JSON object following the schema in the
    system prompt.

ARTICLE AND COMPARISON DATA

{context}
"""

        answer = self.ask_llm(prompt)

        task.memory.set(
            "synthesis_raw_answer",
            answer if answer is not None else "",
        )

        if not isinstance(answer, str) or not answer.strip():
            log(
                "Synthesis",
                "Модель вернула пустой ответ. Используется fallback.",
            )

            report = SynthesisEngine.fallback(
                summaries=summaries,
                comparison_matrix=comparison_matrix,
            )

        else:
            try:
                data = parse_json(
                    answer
                )

                report = SynthesisEngine.from_llm_data(
                    data=data,
                    summaries=summaries,
                    comparison_matrix=comparison_matrix,
                )

                report = SynthesisEngine.remove_invalid_claims(
                    report=report,
                    article_count=len(summaries),
                )

            except (
                ValueError,
                TypeError,
                AttributeError,
                KeyError,
            ) as error:
                log(
                    "Synthesis",
                    (
                        "Не удалось разобрать ответ модели: "
                        f"{type(error).__name__}: {error}"
                    ),
                )

                report = SynthesisEngine.fallback(
                    summaries=summaries,
                    comparison_matrix=comparison_matrix,
                )

        profiled_claims = sum(
            1
            for claim in report.claims
            if claim.evidence_profile_note
        )

        log(
            "Synthesis",
            (
                f"Создано claims: {len(report.claims)}; "
                f"доказательных профилей: {profiled_claims}; "
                f"методологических паттернов: "
                f"{len(report.methodology_patterns)}; "
                f"тенденций: {len(report.trends)}; "
                f"противоречий: "
                f"{len(report.contradictions)}; "
                f"пробелов: {len(report.gaps)}"
            ),
        )

        if not report.claims:
            log(
                "Synthesis",
                (
                    "Внимание: Synthesis Report не содержит claims. "
                    "Writer не сможет создать проверяемый "
                    "аналитический обзор."
                ),
            )

        task.synthesis_report = report

        task.memory.set(
            "synthesis_report",
            report,
        )

        task.result = report

        return report