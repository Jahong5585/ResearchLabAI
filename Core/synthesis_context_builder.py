from __future__ import annotations

import json


class SynthesisContextBuilder:
    """Create compact, numbered input for cross-paper synthesis."""

    @staticmethod
    def build(article_summaries, outline=None) -> str:
        articles = []

        for number, summary in enumerate(article_summaries, start=1):
            articles.append(
                {
                    "article_number": number,
                    "title": summary.title,
                    "authors": summary.authors,
                    "year": summary.year,
                    "journal": summary.journal,
                    "doi": summary.doi,
                    "keywords": summary.keywords,
                    "research_objective": summary.research_objective,
                    "research_questions": summary.research_questions,
                    "study_type": summary.study_type,
                    "educational_level": summary.educational_level,
                    "country": summary.country,
                    "discipline": summary.discipline,
                    "participants": summary.participants,
                    "dataset": summary.dataset,
                    "sample_size": summary.sample_size,
                    "study_period": summary.study_period,
                    "ai_field": summary.ai_field,
                    "ai_models": summary.ai_models,
                    "algorithms": summary.algorithms,
                    "tools": summary.tools,
                    "frameworks": summary.frameworks,
                    "methodology": summary.methodology,
                    "evaluation_metrics": summary.evaluation_metrics,
                    "results": summary.results,
                    "findings": summary.findings,
                    "strengths": summary.strengths,
                    "weaknesses": summary.weaknesses,
                    "limitations": summary.limitations,
                    "practical_implications": summary.practical_implications,
                    "future_research": summary.future_research,
                    "conclusion": summary.conclusion,
                    "verified_facts": summary.verified_facts,
                }
            )

        outline_data = []

        for section in outline or []:
            outline_data.append(
                {
                    "title": section.title,
                    "description": section.description,
                }
            )

        return json.dumps(
            {
                "outline": outline_data,
                "articles": articles,
            },
            ensure_ascii=False,
            indent=2,
        )
