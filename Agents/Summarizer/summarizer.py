from Agents.base_agent import BaseAgent
from Core.article_summary_parser import ArticleSummaryParser
from Core.evidence_builder import EvidenceBuilder


class Summarizer(BaseAgent):
    PROMPT_NAME = "summarizer"
    MODEL_NAME = "SUMMARIZER_MODEL"

    def execute(self, task):
        summaries = []

        for key in (
            "article_summaries",
            "keywords",
            "methodologies",
            "findings",
            "limitations",
            "conclusions",
        ):
            task.memory.remove(key)

        for paper in task.papers.get_all():
            prompt = f"""
Analyze the following scientific publication metadata and abstract.

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
            summary = ArticleSummaryParser.parse(answer, paper)
            summaries.append(summary)

            task.memory.add_article_summary(summary)

            for keyword in summary.keywords:
                task.memory.add_keyword(keyword)

            task.memory.add_methodology(summary.methodology)
            task.memory.add_finding(summary.findings)
            task.memory.add_limitation(summary.limitations)
            task.memory.add_conclusion(summary.conclusion)
            task.memory.add_research_objective(summary.research_objective)
            task.memory.add_study_type(summary.study_type)
            task.memory.add_result(summary.results)
            task.memory.add_strength(summary.strengths)
            task.memory.add_weakness(summary.weaknesses)
            task.memory.add_practical_implication(summary.practical_implications)
            task.memory.add_future_research(summary.future_research)

            for fact in summary.verified_facts:
                task.memory.add_verified_fact(fact)

        task.article_summaries = summaries
        task.evidences = EvidenceBuilder.build(summaries)
        task.result = summaries

        print(f"[Summarizer] summaries: {len(summaries)}")
        return summaries
