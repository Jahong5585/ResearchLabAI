from Agents.base_agent import BaseAgent

from Core.event_logger import log
from Core.json_parser import parse_json
from Core.synthesis_context_builder import SynthesisContextBuilder
from Core.synthesis_engine import SynthesisEngine


class SynthesisAgent(BaseAgent):
    """
    Performs cross-paper analysis before the Writer stage.

    The agent receives structured summaries, compares the studies
    and creates evidence-based synthesis claims.
    """

    PROMPT_NAME = "synthesis"
    MODEL_NAME = "SYNTHESIS_MODEL"

    def execute(self, task):
        summaries = task.article_summaries or []

        log(
            "Synthesis",
            f"Получено summaries для анализа: {len(summaries)}",
        )

        if not summaries:
            report = SynthesisEngine.fallback([])

            task.synthesis_report = report
            task.memory.set("synthesis_report", report)
            task.result = report

            log(
                "Synthesis",
                "Нет summaries. Создан пустой резервный отчёт.",
            )

            return report

        context = SynthesisContextBuilder.build(
            summaries,
            task.outline,
        )

        prompt = f"""
Analyze the numbered scientific article summaries below.

You must compare the articles and produce only claims supported by the
provided records.

Requirements:

1. Do not use external knowledge.
2. Every claim must include the numbers of supporting articles.
3. If comparable articles report opposing results, include the numbers
   of contradicting articles.
4. Do not treat differences in populations, outcomes, timepoints,
   countries or methodologies as direct contradictions.
5. Create analytical cross-paper claims, not separate article summaries.
6. Return only one valid JSON object following the schema defined
   in the system prompt.

ARTICLE DATA

{context}
"""

        # This call was missing in the previous version.
        answer = self.ask_llm(prompt)

        # Save the raw response for diagnostics.
        task.memory.set(
            "synthesis_raw_answer",
            answer if answer is not None else "",
        )

        if not isinstance(answer, str) or not answer.strip():
            log(
                "Synthesis",
                "Модель вернула пустой ответ. Используется fallback.",
            )

            report = SynthesisEngine.fallback(summaries)

        else:
            try:
                data = parse_json(answer)

                report = SynthesisEngine.from_llm_data(
                    data,
                    summaries,
                )

                report = SynthesisEngine.remove_invalid_claims(
                    report,
                    len(summaries),
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

                report = SynthesisEngine.fallback(summaries)

        log(
            "Synthesis",
            (
                f"Создано claims: {len(report.claims)}; "
                f"методологических паттернов: "
                f"{len(report.methodology_patterns)}; "
                f"тенденций: {len(report.trends)}; "
                f"противоречий: {len(report.contradictions)}; "
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