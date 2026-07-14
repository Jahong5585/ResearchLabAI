import json
from typing import Any

from Agents.base_agent import BaseAgent
from Core.event_logger import log


class WriterAgent(BaseAgent):
    """
    Converts validated cross-paper synthesis into an academic
    literature review.

    Writer does not search for information and does not independently
    analyze the original articles.

    The Comparison Matrix and evidence profiles may be used only to
    qualify and organize validated synthesis claims.
    """

    PROMPT_NAME = "writer"
    MODEL_NAME = "WRITER_MODEL"

    COMPARISON_FIELDS = (
        "article_number",
        "normalized_design",
        "source_type",
        "abstract_completeness_score",
        "abstract_evidence_level",
        "educational_level",
        "country",
        "discipline",
        "participants",
        "sample_size",
        "study_period",
        "methodology",
        "evaluation_metrics",
        "results",
        "findings",
        "limitations",
        "reported_core_fields",
        "missing_core_fields",
    )

    def execute(self, task):
        report = task.synthesis_report
        summaries = task.article_summaries or []
        comparison_matrix = task.comparison_matrix or []

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

        profiled_claims = sum(
            1
            for claim in report.claims
            if claim.evidence_profile_note
        )

        log(
            "Writer",
            (
                f"Получено claims: {len(report.claims)}; "
                f"доказательных профилей: {profiled_claims}; "
                f"методологических паттернов: "
                f"{len(report.methodology_patterns)}; "
                f"тенденций: {len(report.trends)}; "
                f"противоречий: {len(report.contradictions)}; "
                f"пробелов: {len(report.gaps)}; "
                f"повторяющихся ограничений: "
                f"{len(report.recurring_limitations)}; "
                f"строк Comparison Matrix: "
                f"{len(comparison_matrix)}"
            ),
        )

        context = self._build_context(task)

        prompt = f"""
Write a coherent academic literature review for the user's request.

Write in the same language as the user's request.

The scientific comparison has already been completed by the Synthesis Agent.
You must not perform a new scientific analysis of the original publications.

AVAILABLE STRUCTURED DATA

You receive:

- validated SYNTHESIS CLAIMS;
- EVIDENCE PROFILES for synthesis claims;
- METHODOLOGY PATTERNS;
- TRENDS;
- CONTRADICTIONS;
- GAPS;
- RECURRING LIMITATIONS;
- AGGREGATE STATISTICS;
- COMPARISON MATRIX;
- REFERENCE METADATA.

The COMPARISON MATRIX contains factual study characteristics extracted from
metadata and available abstracts.

The EVIDENCE PROFILE of each claim may contain:

- supporting study designs;
- objective-evidence article numbers;
- perception or self-report article numbers;
- review or meta-analytic article numbers;
- distribution of abstract-level evidence usability;
- a deterministic weighted-support score;
- a human-readable evidence-profile note.

SCIENTIFIC BOUNDARY

The evidence profiles are based only on metadata and available abstracts.

The value quality_weighted_support is not:

- a full risk-of-bias assessment;
- a journal-quality score;
- a final assessment of scientific quality;
- proof that one publication is superior to another.

It is only a deterministic indicator describing the methodological
composition and abstract-level usability of the supporting records.

MANDATORY COVERAGE RULES

1. Use every valid item in SYNTHESIS CLAIMS.
2. Do not omit a synthesis claim merely to make the review shorter.
3. Compatible claims may be combined in one paragraph, but their meaning,
   confidence, caveats and article numbers must be preserved.
4. SYNTHESIS CLAIMS remain the only source for conclusions about effects,
   benefits, risks, relationships and trends.
5. COMPARISON MATRIX may be used for factual methodological comparison and
   for qualifying validated claims.
6. EVIDENCE PROFILES may be used to explain what kinds of evidence support
   each validated claim.
7. Do not independently reinterpret individual article results.
8. Do not create a majority conclusion from several matrix rows unless that
   conclusion is explicitly present in SYNTHESIS CLAIMS.
9. Do not use external knowledge.

EVIDENCE PROFILE RULES

10. When useful, explain whether a claim is supported by:

    - objective outcome measurements;
    - perception or self-report evidence;
    - review or meta-analytic evidence;
    - more than one evidence type.

11. When objective and perception evidence support the same claim, state that
    the conclusion is supported across different evidence types.

12. Do not imply methodological convergence unless the evidence profile
    actually contains multiple evidence types.

13. A claim supported by one article must be explicitly described as a
    single-study or single-publication finding.

14. A claim supported only by perception evidence must not be described as an
    objectively demonstrated effect.

15. A claim supported only by review evidence must not be presented as a new
    primary empirical result.

16. A claim supported by objective evidence may be described as involving
    measured outcomes only when the profile identifies objective-evidence
    articles.

17. When a meta-analysis and individual empirical studies support the same
    claim, explain this cautiously as support from both evidence synthesis and
    primary studies.

18. Do not print the raw quality_weighted_support number in the final text
    unless the user explicitly requests technical system diagnostics.

19. Do not describe a larger weighted-support score as proof of higher
    scientific truth or full-text quality.

DIRECT COMPARISON REQUIREMENTS

20. Include a substantive section devoted to comparative methodology and
    evidence characteristics when the supplied data permit it.

21. Compare, where available:

    - intervention or experimental research;
    - mixed-methods research;
    - qualitative interviews or focus groups;
    - surveys and perception studies;
    - literature reviews;
    - systematic reviews or meta-analyses.

22. Clearly distinguish:

    - objective writing-performance results;
    - self-reported perceptions;
    - conceptual or review-based conclusions.

23. Explain whether conclusions are consistent across different study
    designs only when a SYNTHESIS CLAIM and its EVIDENCE PROFILE support
    that statement.

24. When sample sizes, participants, metrics or countries are unavailable,
    say that they are not reported in the available abstracts.

25. Do not say that the complete articles lack these data.

26. Do not describe abstract_evidence_level as final scientific quality,
    risk of bias or journal quality.

27. Use formulations such as:

    - "По доступным аннотациям..."
    - "На уровне доступных аннотаций..."
    - "Данный вывод поддерживается исследованиями разных типов..."
    - "Объективные измерения дополняются данными о восприятии студентов..."
    - "Вывод основан преимущественно на самоотчётах участников..."
    - "Метааналитические данные согласуются с отдельными эмпирическими
      исследованиями..."
    - "Прямое сравнение ограничено отсутствием сведений в аннотациях..."

28. Do not claim that an article is scientifically superior merely because
    its abstract is more complete.

ANALYTICAL STRUCTURE

29. Avoid an article-by-article catalogue.

30. Organize the review around:

    - agreements and majority patterns;
    - minority findings;
    - measured outcomes;
    - student perceptions;
    - methodological similarities and differences;
    - evidence consistency across research designs;
    - temporal, geographical or population differences;
    - contradictions;
    - recurring limitations;
    - evidence gaps.

31. When suitable, compare groups of studies in one paragraph, for example:

    - experimental studies versus perception studies;
    - empirical studies versus literature reviews;
    - meta-analytic evidence versus individual interventions.

32. Do not create a section when the supplied context contains no supported
    information for that category.

33. Clearly distinguish evidence supported by several studies from a finding
    reported in only one publication.

34. Preserve every confidence level and caveat.

35. Do not strengthen tentative or low-confidence conclusions.

36. Do not repeat the same conclusion in multiple sections.

SOURCE BOUNDARY

37. The supplied records may be based only on bibliographic metadata and
    available abstracts, not on complete article texts.

38. Missing information in an abstract is not automatically a weakness of
    the complete study.

39. Never convert:

    "Not reported in the available abstract"

    into:

    "The authors failed to report"
    or
    "The article does not contain".

40. Explicitly distinguish:

    - limitations stated by the publication;
    - limitations of the available abstract-level evidence.

CITATION RULES

41. Every analytical statement derived from a synthesis claim must contain
    citations in this exact form:

    [ARTICLE 1; ARTICLE 2]

42. Use supporting article numbers exactly as supplied.

43. If contradicting article numbers are supplied, explain the disagreement
    and cite both groups.

44. Do not add an article to a citation unless it supports the relevant claim.

45. A factual study-characteristic statement derived from COMPARISON MATRIX
    must cite the corresponding article number.

46. An evidence-profile statement must cite the articles represented by the
    relevant evidence-profile group.

47. For corpus-level statements derived from AGGREGATE STATISTICS, use the
    exact citation provided in ALL_ARTICLES_CITATION.

48. Never print the words ALL_ARTICLES_CITATION or ALL_ARTICLE_NUMBERS in
    the finished review.

REFERENCE RULES

49. Use only REFERENCE METADATA for the reference list.

50. Include every reference cited in the review.

51. Do not include uncited references.

52. Do not invent missing authors, years, journals, issue numbers, pages or
    DOI values.

OUTPUT STRUCTURE

Produce a developed academic literature review containing, when supported:

- introduction;
- synthesis of principal findings;
- evidence-profile interpretation;
- direct comparison of methodologies and evidence types;
- comparison of measured outcomes and participant perceptions;
- risks, limitations or contradictions;
- limitations of the available abstract-level evidence;
- research gaps;
- conclusion;
- references.

Do not return a short abstract.
Do not return an article-by-article list.
Do not return JSON.

USER REQUEST

{task.user_request}

VALIDATED RESEARCH CONTEXT

{context}
"""

        answer = self.ask_llm(prompt)

        all_articles_citation = self._build_all_articles_citation(
            len(summaries)
        )

        answer = self._replace_service_placeholders(
            answer,
            all_articles_citation,
        )

        task.literature_review = answer
        task.result = answer

        log(
            "Writer",
            f"Обзор создан. Длина: {len(answer)} символов.",
        )

        return answer

    @classmethod
    def _build_context(cls, task) -> str:
        report = task.synthesis_report
        summaries = task.article_summaries or []

        claims = []

        for number, claim in enumerate(
            report.claims,
            start=1,
        ):
            claims.append(
                {
                    "claim_number": number,
                    "claim_type": claim.claim_type,
                    "statement": claim.statement,
                    "supporting_articles": (
                        claim.supporting_articles
                    ),
                    "contradicting_articles": (
                        claim.contradicting_articles
                    ),
                    "confidence": claim.confidence,
                    "rationale": claim.rationale,
                    "caveats": claim.caveats,
                    "evidence_count": (
                        claim.evidence_count
                    ),
                    "contradiction_count": (
                        claim.contradiction_count
                    ),
                    "supporting_designs": (
                        claim.supporting_designs
                    ),
                    "objective_evidence_articles": (
                        claim.objective_evidence_articles
                    ),
                    "objective_evidence_count": (
                        claim.objective_evidence_count
                    ),
                    "perception_evidence_articles": (
                        claim.perception_evidence_articles
                    ),
                    "perception_evidence_count": (
                        claim.perception_evidence_count
                    ),
                    "review_evidence_articles": (
                        claim.review_evidence_articles
                    ),
                    "review_evidence_count": (
                        claim.review_evidence_count
                    ),
                    "has_multiple_evidence_types": (
                        claim.has_multiple_evidence_types
                    ),
                    "abstract_evidence_levels": (
                        claim.abstract_evidence_levels
                    ),
                    "quality_weighted_support": (
                        claim.quality_weighted_support
                    ),
                    "evidence_profile_note": (
                        claim.evidence_profile_note
                    ),
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

        for number, article in enumerate(
            summaries,
            start=1,
        ):
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

        comparison_matrix = cls._build_comparison_context(
            task.comparison_matrix
        )

        all_article_numbers = list(
            range(
                1,
                len(summaries) + 1,
            )
        )

        all_articles_citation = (
            cls._build_all_articles_citation(
                len(summaries)
            )
        )

        data = {
            "source_boundary": (
                "The analysis is based on bibliographic metadata "
                "and available abstracts, not necessarily full texts."
            ),
            "search_query": task.memory.get(
                "search_query",
                "",
            ),
            "all_article_numbers": all_article_numbers,
            "all_articles_citation": all_articles_citation,
            "outline": outline,
            "synthesis_overview": report.overview,
            "synthesis_claims": claims,
            "methodology_patterns": (
                report.methodology_patterns
            ),
            "trends": report.trends,
            "contradictions": report.contradictions,
            "gaps": report.gaps,
            "recurring_limitations": (
                report.recurring_limitations
            ),
            "aggregate_statistics": (
                report.aggregate_statistics
            ),
            "comparison_matrix": comparison_matrix,
            "reference_metadata": references,
        }

        return json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )

    @classmethod
    def _build_comparison_context(
        cls,
        comparison_matrix,
    ) -> list[dict[str, Any]]:
        """
        Keep only comparison fields needed by Writer.

        This avoids passing duplicate metadata and reduces token usage.
        """

        comparison_data = []

        for raw_row in comparison_matrix or []:
            if not isinstance(
                raw_row,
                dict,
            ):
                continue

            row = {}

            for field_name in cls.COMPARISON_FIELDS:
                if field_name in raw_row:
                    row[field_name] = raw_row[
                        field_name
                    ]

            comparison_data.append(
                row
            )

        return comparison_data

    @staticmethod
    def _build_all_articles_citation(
        article_count: int,
    ) -> str:
        if article_count <= 0:
            return ""

        article_markers = [
            f"ARTICLE {number}"
            for number in range(
                1,
                article_count + 1,
            )
        ]

        return f"[{'; '.join(article_markers)}]"

    @staticmethod
    def _replace_service_placeholders(
        answer: str,
        all_articles_citation: str,
    ) -> str:
        replacements = (
            "[ALL_ARTICLE_NUMBERS]",
            "ALL_ARTICLE_NUMBERS",
            "[ALL_ARTICLES_CITATION]",
            "ALL_ARTICLES_CITATION",
        )

        result = answer

        for placeholder in replacements:
            result = result.replace(
                placeholder,
                all_articles_citation,
            )

        return result