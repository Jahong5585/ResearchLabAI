import json
from collections import Counter
from typing import Any

from Agents.base_agent import BaseAgent
from Core.event_logger import log


class WriterAgent(BaseAgent):
    """
    Converts validated cross-paper synthesis into an academic
    literature review.

    Writer does not search for information and does not independently
    analyze the original publications.

    The agent may use:

    - validated synthesis claims;
    - claim-level evidence profiles;
    - the Comparison Matrix;
    - extraction provenance.

    Extraction provenance distinguishes records analyzed only from an
    abstract from records that also used selected full-text sections.
    """

    PROMPT_NAME = "writer"
    MODEL_NAME = "WRITER_MODEL"

    COMPARISON_FIELDS = (
        "article_number",

        # Extraction provenance.
        "source_scope",
        "uses_full_text",
        "source_sections",
        "source_text_characters",
        "full_text_source",

        # Methodological characteristics.
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

        provenance_summary = self._build_provenance_summary(
            comparison_matrix
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
                f"{len(comparison_matrix)}; "
                f"FULL_TEXT_SECTIONS: "
                f"{provenance_summary['full_text_count']}; "
                f"ABSTRACT_ONLY: "
                f"{provenance_summary['abstract_only_count']}"
            ),
        )

        context = self._build_context(task)

        prompt = f"""
Write a coherent academic literature review for the user's request.

Write in the same language as the user's request.

The scientific comparison has already been completed by the Synthesis Agent.

You must not perform a new independent analysis of the original publications.

AVAILABLE STRUCTURED DATA

You receive:

- validated SYNTHESIS CLAIMS;
- claim-level EVIDENCE PROFILES;
- METHODOLOGY PATTERNS;
- TRENDS;
- CONTRADICTIONS;
- GAPS;
- RECURRING LIMITATIONS;
- AGGREGATE STATISTICS;
- COMPARISON MATRIX;
- EXTRACTION PROVENANCE;
- REFERENCE METADATA.

SOURCE SCOPES

Every publication has one of two source scopes:

ABSTRACT_ONLY

or:

FULL_TEXT_SECTIONS

ABSTRACT_ONLY means that extraction was based on bibliographic metadata and
the available abstract.

FULL_TEXT_SECTIONS means that extraction was based on bibliographic metadata,
the abstract and selected sections extracted from an openly accessible full
text.

FULL_TEXT_SECTIONS does not mean that:

- every page was analyzed;
- every section was available;
- the complete publication was assessed;
- the publication automatically has higher scientific quality;
- a formal risk-of-bias assessment was performed.

SOURCE-PROVENANCE RULES

1. Preserve the distinction between ABSTRACT_ONLY and FULL_TEXT_SECTIONS.

2. When discussing corpus limitations, state how many publications were
   analyzed using selected full-text sections and how many were analyzed only
   from abstracts, when these counts are supplied.

3. Do not write:

   "The complete article shows..."

   unless the system actually supplied the complete article, which the current
   architecture does not guarantee.

4. Use formulations such as:

   - "В выбранных разделах полного текста статьи..."
   - "В доступной аннотации статьи..."
   - "Для части корпуса использовались выбранные разделы полного текста..."
   - "Для остальных публикаций анализ ограничивался доступными аннотациями..."
   - "Смешанный характер источников ограничивает одинаковую глубину сравнения..."

5. Do not call FULL_TEXT_SECTIONS a complete full-text review.

6. Do not claim that FULL_TEXT_SECTIONS records are automatically more
   reliable than ABSTRACT_ONLY records.

7. Do not describe a longer supplied text as evidence of a better study.

8. If a conclusion is supported by both source scopes, you may state that the
   conclusion appears across different extraction scopes, but do not present
   this as proof of scientific validity.

9. When a result comes only from an ABSTRACT_ONLY record, avoid wording that
   implies verification against the full article.

10. When a result comes from FULL_TEXT_SECTIONS, specify that it was found in
    the selected supplied sections, not necessarily in a complete full-text
    assessment.

SCIENTIFIC BOUNDARY

The evidence profiles and Comparison Matrix are based on source material
supplied to the system.

The following internal values are not:

- complete scientific-quality assessments;
- risk-of-bias assessments;
- journal rankings;
- peer-review assessments;
- proof that one publication is superior;
- proof that a claim is true:

abstract_completeness_score
abstract_evidence_level
design_weight
quality_weighted_support
source_text_characters

Do not print raw internal scores in the final review.

MANDATORY COVERAGE RULES

11. Use every valid item in SYNTHESIS CLAIMS.

12. Do not omit a synthesis claim merely to make the review shorter.

13. Compatible claims may be combined in one paragraph, but their meaning,
    confidence, caveats and article numbers must be preserved.

14. SYNTHESIS CLAIMS remain the only source for conclusions about effects,
    benefits, risks, relationships, contradictions and trends.

15. COMPARISON MATRIX may be used for factual methodological comparison and
    for qualifying validated claims.

16. EVIDENCE PROFILES may be used to explain which types of evidence support
    each validated claim.

17. EXTRACTION PROVENANCE may be used to explain the depth and limitations of
    the source material available to the system.

18. Do not independently reinterpret individual article results.

19. Do not create a majority conclusion from several matrix rows unless that
    conclusion is explicitly present in SYNTHESIS CLAIMS.

20. Do not use external knowledge.

EVIDENCE-PROFILE RULES

21. When useful, explain whether a claim is supported by:

    - objectively measured outcomes;
    - perception or self-report evidence;
    - review or meta-analytic evidence;
    - more than one evidence type.

22. A claim supported by one publication must be explicitly described as a
    single-study or single-publication finding.

23. A claim supported only by perception evidence must not be described as an
    objectively demonstrated effect.

24. A claim supported only by review evidence must not be presented as a new
    primary empirical result.

25. When objective and perception evidence support the same validated claim,
    state cautiously that the conclusion is supported across different
    evidence types.

26. Do not imply methodological convergence unless the evidence profile
    actually contains multiple evidence types or compatible study designs.

27. When a meta-analysis and primary empirical studies support the same claim,
    describe this cautiously as support from evidence synthesis and primary
    studies.

28. Do not print quality_weighted_support in the finished review.

29. Do not treat a larger weighted-support value as proof of truth or
    scientific superiority.

DIRECT COMPARISON REQUIREMENTS

30. Include a substantive section devoted to methodological comparison when
    the supplied data permit it.

31. Compare, where available:

    - intervention or experimental studies;
    - controlled studies;
    - mixed-methods studies;
    - qualitative interviews and focus groups;
    - surveys and perception studies;
    - literature reviews;
    - systematic reviews;
    - meta-analyses.

32. Clearly distinguish:

    - objective writing-performance results;
    - participant perceptions and attitudes;
    - review-based conclusions;
    - conceptual discussion.

33. Explain whether findings are consistent across different designs only
    when a validated claim and its evidence profile support this statement.

34. When sample sizes, participants, metrics, countries or durations are
    unavailable, specify that they were not reported in the source text
    supplied to the system.

35. Do not state that the complete publications lack these data.

36. Do not describe source-scope differences as contradictions.

37. Do not describe methodological differences as contradictions unless the
    validated synthesis explicitly identifies a genuine contradiction.

MISSING-INFORMATION RULES

38. The value:

    "Not reported in the supplied source text"

    means only that information was not identified in the metadata, abstract
    or selected full-text sections supplied to the system.

39. Never convert it into:

    - "The authors failed to report..."
    - "The article does not contain..."
    - "The study has no sample..."
    - "The complete paper lacks limitations..."

40. Clearly distinguish:

    - limitations explicitly stated by a publication;
    - missing information in the supplied source material;
    - limitations of the review corpus.

ANALYTICAL STRUCTURE

41. Avoid an article-by-article catalogue.

42. Organize the review around:

    - agreements and majority patterns;
    - minority findings;
    - measured outcomes;
    - participant perceptions;
    - methodological similarities and differences;
    - evidence consistency across designs;
    - extraction-provenance boundaries;
    - temporal, geographical or population differences;
    - contradictions;
    - recurring limitations;
    - evidence gaps.

43. When appropriate, compare groups of studies:

    - experiments versus perception studies;
    - primary empirical studies versus reviews;
    - meta-analytic evidence versus individual interventions;
    - FULL_TEXT_SECTIONS records versus ABSTRACT_ONLY records.

44. Do not create a section when the supplied context contains no supported
    information for that category.

45. Preserve every confidence level and caveat.

46. Do not strengthen tentative or low-confidence conclusions.

47. Do not repeat the same conclusion in several sections.

CITATION RULES

48. Every analytical statement derived from a synthesis claim must contain
    citations in this exact format:

    [ARTICLE 1; ARTICLE 2]

49. Use supporting article numbers exactly as supplied.

50. If contradicting article numbers are supplied, explain the disagreement
    and cite both groups.

51. A factual methodological or provenance statement derived from the
    Comparison Matrix must cite the corresponding article number.

52. Do not add an article to a citation unless it supports the relevant
    statement.

53. For corpus-level statements derived from aggregate data, use the exact
    all-article citation supplied in the context.

54. Never print service placeholders such as:

    ALL_ARTICLE_NUMBERS
    ALL_ARTICLES_CITATION

REFERENCE RULES

55. Use only REFERENCE METADATA for the reference list.

56. Include every reference cited in the review.

57. Do not include uncited references.

58. Do not invent missing authors, years, journals, issue numbers, pages or
    DOI values.

OUTPUT STRUCTURE

Produce a developed academic literature review containing, when supported:

- introduction;
- synthesis of principal findings;
- interpretation of evidence profiles;
- direct comparison of methodologies and evidence types;
- comparison of measured outcomes and participant perceptions;
- source-provenance and corpus limitations;
- risks, limitations or contradictions;
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
        comparison_matrix = task.comparison_matrix or []

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
                    "source_scope": getattr(
                        article,
                        "source_scope",
                        "ABSTRACT_ONLY",
                    ),
                    "source_sections": getattr(
                        article,
                        "source_sections",
                        [],
                    ),
                    "full_text_source": getattr(
                        article,
                        "full_text_source",
                        "",
                    ),
                }
            )

        comparison_context = (
            cls._build_comparison_context(
                comparison_matrix
            )
        )

        provenance_summary = (
            cls._build_provenance_summary(
                comparison_matrix
            )
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
                "The analysis may use metadata and abstracts or metadata, "
                "abstracts and selected full-text sections. Selected "
                "sections do not necessarily represent the complete article."
            ),
            "search_query": task.memory.get(
                "search_query",
                "",
            ),
            "all_article_numbers": all_article_numbers,
            "all_articles_citation": all_articles_citation,
            "provenance_summary": provenance_summary,
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
            "comparison_matrix": comparison_context,
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
        Keep only fields required by Writer.

        This reduces duplicated data and model-token usage.
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
    def _build_provenance_summary(
        comparison_matrix,
    ) -> dict[str, Any]:
        scope_counter = Counter()
        section_counter = Counter()
        source_counter = Counter()

        full_text_article_numbers = []
        abstract_only_article_numbers = []

        for row in comparison_matrix or []:
            if not isinstance(
                row,
                dict,
            ):
                continue

            article_number = row.get(
                "article_number"
            )

            source_scope = str(
                row.get(
                    "source_scope",
                    "ABSTRACT_ONLY",
                )
                or "ABSTRACT_ONLY"
            ).strip()

            scope_counter[
                source_scope
            ] += 1

            if source_scope == "FULL_TEXT_SECTIONS":
                full_text_article_numbers.append(
                    article_number
                )
            else:
                abstract_only_article_numbers.append(
                    article_number
                )

            source_sections = row.get(
                "source_sections",
                [],
            )

            if isinstance(
                source_sections,
                list,
            ):
                for section_name in source_sections:
                    section_text = str(
                        section_name
                    ).strip()

                    if section_text:
                        section_counter[
                            section_text
                        ] += 1

            full_text_source = str(
                row.get(
                    "full_text_source",
                    "",
                )
                or ""
            ).strip()

            if full_text_source:
                source_counter[
                    full_text_source
                ] += 1

        return {
            "total_articles": len(
                comparison_matrix or []
            ),
            "full_text_count": scope_counter.get(
                "FULL_TEXT_SECTIONS",
                0,
            ),
            "abstract_only_count": scope_counter.get(
                "ABSTRACT_ONLY",
                0,
            ),
            "source_scope_counts": dict(
                scope_counter
            ),
            "full_text_article_numbers": (
                full_text_article_numbers
            ),
            "abstract_only_article_numbers": (
                abstract_only_article_numbers
            ),
            "full_text_section_counts": dict(
                section_counter
            ),
            "full_text_source_counts": dict(
                source_counter
            ),
            "interpretation_boundary": (
                "FULL_TEXT_SECTIONS means selected extracted sections, "
                "not necessarily complete full-text analysis."
            ),
        }

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