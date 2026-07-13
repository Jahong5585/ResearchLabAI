from Agents.base_agent import BaseAgent
from Core.json_parser import parse_json
from Core.synthesis_context_builder import SynthesisContextBuilder
from Core.synthesis_engine import SynthesisEngine


class SynthesisAgent(BaseAgent):
    """Perform cross-paper analysis before the Writer stage."""

    PROMPT_NAME = "synthesis"
    MODEL_NAME = "SYNTHESIS_MODEL"

    def execute(self, task):
        summaries = task.article_summaries

        if not summaries:
            report = SynthesisEngine.fallback([])
            task.synthesis_report = report
            task.memory.set("synthesis_report", report)
            return report

        context = SynthesisContextBuilder.build(
            summaries,
            task.outline,
        )

        prompt = f"""
Analyze the numbered scientific article summaries below.

You must compare articles and produce only claims supported by the supplied
records. Do not use external knowledge. Every claim must list the article
numbers that support it. If articles conflict, list the contradicting article
numbers separately. Do not treat different populations, outcomes, timepoints,
or methods as a direct contradiction unless they are genuinely comparable.

Return one valid JSON object that follows the schema in the system prompt.

ARTICLE DATA

{context}
"""

        answer = self.ask_llm(prompt)

        try:
            data = parse_json(answer)
            report = SynthesisEngine.from_llm_data(data, summaries)
            report = SynthesisEngine.remove_invalid_claims(
                report,
                len(summaries),
            )
        except (ValueError, TypeError, AttributeError):
            report = SynthesisEngine.fallback(summaries)

        if not report.claims and not report.methodology_patterns:
            report = SynthesisEngine.fallback(summaries)

        task.synthesis_report = report
        task.memory.set("synthesis_report", report)
        task.result = report
        return report
