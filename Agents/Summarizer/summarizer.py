from Agents.base_agent import BaseAgent

from Models.article_summary import ArticleSummary
from Core.evidence_builder import EvidenceBuilder


class Summarizer(BaseAgent):

    PROMPT_NAME = "summarizer"

    MODEL_NAME = "SUMMARIZER_MODEL"

    def execute(self, task):

        summaries = []

        task.memory.remove("article_summaries")
        task.memory.remove("keywords")
        task.memory.remove("methodologies")
        task.memory.remove("findings")
        task.memory.remove("limitations")
        task.memory.remove("conclusions")

        for paper in task.papers.get_all():

            prompt = f"""
Проанализируй следующую научную публикацию.

==================================================

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

            sections = {}

            current = None

            for line in answer.splitlines():

                line = line.strip()

                if not line:
                    continue

                if line.endswith(":"):

                    current = line[:-1]

                    sections[current] = ""

                    continue

                if current:

                    sections[current] += line + " "

            keywords = []

            if "Keywords" in sections:

                keywords = [

                    item.strip()

                    for item in sections["Keywords"].split(",")

                    if item.strip()

                ]

            verified_facts = []

            if "VerifiedFacts" in sections:

                verified_facts = [

                    item.strip("- ").strip()

                    for item in sections["VerifiedFacts"].split("-")

                    if item.strip()

                ]

            if (
                len(verified_facts) == 1
                and verified_facts[0].lower() == "not specified"
            ):

                verified_facts = []

            summary = ArticleSummary(

                title=paper.title,

                authors=", ".join(paper.authors),

                year=paper.year,

                journal=paper.journal,

                doi=paper.doi,

                abstract=paper.abstract,

                problem=sections.get(
                    "Problem",
                    "Not specified"
                ).strip(),

                methodology=sections.get(
                    "Methodology",
                    "Not specified"
                ).strip(),

                findings=sections.get(
                    "Findings",
                    "Not specified"
                ).strip(),

                limitations=sections.get(
                    "Limitations",
                    "Not specified"
                ).strip(),

                conclusion=sections.get(
                    "Conclusion",
                    "Not specified"
                ).strip(),

                keywords=keywords,

                verified_facts=verified_facts

            )

            summaries.append(summary)

            task.memory.add_article_summary(summary)

            for keyword in keywords:

                task.memory.add_keyword(keyword)

            task.memory.add_methodology(summary.methodology)
            task.memory.add_finding(summary.findings)
            task.memory.add_limitation(summary.limitations)
            task.memory.add_conclusion(summary.conclusion)

        task.article_summaries = summaries

        task.evidences = EvidenceBuilder.build(summaries)

        task.result = summaries

        print(f"[Summarizer] summaries: {len(summaries)}")
        print(f"[Summarizer] task.article_summaries: {len(task.article_summaries)}")

        return summaries