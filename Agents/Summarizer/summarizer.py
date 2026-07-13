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

                research_objective=sections.get(
                    "ResearchObjective",
                    "Not specified"
                ).strip(),

                research_questions=sections.get(
                    "ResearchQuestions",
                    "Not specified"
                ).strip(),

                study_type=sections.get(
                    "StudyType",
                    "Not specified"
                ).strip(),

                educational_level=sections.get(
                    "EducationalLevel",
                    "Not specified"
                ).strip(),

                country=sections.get(
                    "Country",
                    "Not specified"
                ).strip(),

                discipline=sections.get(
                    "Discipline",
                    "Not specified"
                ).strip(),

                participants=sections.get(
                    "Participants",
                    "Not specified"
                ).strip(),

                dataset=sections.get(
                    "Dataset",
                    "Not specified"
                ).strip(),

                sample_size=sections.get(
                    "SampleSize",
                    "Not specified"
                ).strip(),

                study_period=sections.get(
                    "StudyPeriod",
                    "Not specified"
                ).strip(),

                ai_field=sections.get(
                    "AIField",
                    "Not specified"
                ).strip(),
                ai_models=sections.get(
                    "AIModels",
                    "Not specified"
                ).strip(),

                algorithms=sections.get(
                    "Algorithms",
                    "Not specified"
                ).strip(),

                tools=sections.get(
                    "Tools",
                    "Not specified"
                ).strip(),

                frameworks=sections.get(
                    "Frameworks",
                    "Not specified"
                ).strip(),

                evaluation_metrics=sections.get(
                    "EvaluationMetrics",
                    "Not specified"
                ).strip(),

                results=sections.get(
                    "Results",
                    "Not specified"
                ).strip(),

                strengths=sections.get(
                    "Strengths",
                    "Not specified"
                ).strip(),

                weaknesses=sections.get(
                    "Weaknesses",
                    "Not specified"
                ).strip(),

                practical_implications=sections.get(
                    "PracticalImplications",
                    "Not specified"
                ).strip(),

                future_research=sections.get(
                    "FutureResearch",
                    "Not specified"
                ).strip(),

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
        print(
            f"[Summarizer] task.article_summaries: "
            f"{len(task.article_summaries)}"
        )

        return summaries