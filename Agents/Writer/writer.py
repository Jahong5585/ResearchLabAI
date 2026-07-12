from Agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):

    PROMPT_NAME = "writer"
    MODEL_NAME = "WRITER_MODEL"

    def execute(self, task):

        if not task.article_summaries:

            task.literature_review = (
                "Нет данных для построения обзора."
            )

            task.result = task.literature_review

            return task.literature_review

        context = ""

        # =====================================================
        # RESEARCH INFORMATION
        # =====================================================

        context += "==============================\n"
        context += "RESEARCH INFORMATION\n"
        context += "==============================\n\n"

        context += (
            f"Search query: "
            f"{task.memory.get('search_query', '')}\n"
        )

        context += (
            f"Total papers: "
            f"{task.memory.get('papers_count', 0)}\n\n"
        )

        corpus = task.memory.get(
            "corpus_report",
            {}
        )

        context += (
            f"Average citations: "
            f"{corpus.get('average_citations', 0)}\n\n"
        )

        context += "Publication years\n"

        for year, count in corpus.get(
            "years",
            {}
        ).items():

            context += f"{year}: {count}\n"

        context += "\n"

        # =====================================================
        # EVIDENCE
        # =====================================================

        context += "==============================\n"
        context += "EVIDENCE\n"
        context += "==============================\n\n"

        for evidence in task.evidences:

            context += f"""
Topic:
{evidence.topic}

Confidence:
{evidence.confidence}

Supporting articles:
{len(evidence.supporting_articles)}
"""

            if hasattr(evidence, "common_findings"):

                for finding in evidence.common_findings:

                    context += f"- {finding}\n"

            context += "\n"

        # =====================================================
        # VERIFIED FACTS
        # =====================================================

        context += "==============================\n"
        context += "VERIFIED FACTS\n"
        context += "==============================\n"

        references = []

        article_number = 1

        for article in task.article_summaries:

            if not article.verified_facts:
                article_number += 1
                continue

            context += f"""

--------------------------------

ARTICLE {article_number}

Verified facts

"""

            for fact in article.verified_facts:

                context += f"- {fact}\n"

            references.append(
                f"""

ARTICLE {article_number}

Title:
{article.title}

Authors:
{article.authors}

Journal:
{article.journal}

Year:
{article.year}

DOI:
{article.doi}
"""
            )

            article_number += 1

        # =====================================================
        # REFERENCES
        # =====================================================

        context += """

==============================
REFERENCE LIST
==============================

"""

        context += "\n".join(references)

        prompt = f"""
Используй только информацию ниже.

Единственный источник содержания —

VERIFIED FACTS.

Дополнительно разрешается использовать только:

RESEARCH INFORMATION

EVIDENCE

Запрещено:

- использовать знания модели;
- делать предположения;
- интерпретировать VERIFIED FACTS;
- изменять числа;
- изменять годы;
- изменять проценты;
- изменять методы;
- изменять технологии;
- придумывать статистику;
- придумывать авторов;
- придумывать DOI;
- использовать статьи вне списка ARTICLE;
- использовать сведения из Abstract;
- использовать сведения из Problem;
- использовать сведения из Findings;
- использовать сведения из Methodology;
- использовать сведения из Conclusion;
- использовать сведения из Limitations.

Если VERIFIED FACTS отсутствуют —
не упоминай такую статью.

Не анализируй статьи,
для которых отсутствуют VERIFIED FACTS.

Каждое утверждение должно опираться
только на VERIFIED FACTS.

==============================

{context}

==============================

Запрос пользователя:

{task.user_request}
"""

        answer = self.ask_llm(prompt)

        task.literature_review = answer

        task.result = answer

        return answer