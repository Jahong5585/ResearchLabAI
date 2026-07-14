from Core.event_logger import log
from Core.full_text_service import FullTextService
from Core.paper_ranker import PaperRanker


class RankingAgent:
    """
    Ranks retrieved scientific publications and keeps only
    the most relevant papers.

    After ranking, the agent attempts to retrieve openly available
    full texts only for the selected publications.

    Ranking and full-text retrieval do not use an LLM.
    """

    # Maximum number of publications passed to Summarizer.
    TOP_PAPERS = 10

    # Full-text retrieval can be disabled temporarily when needed.
    ENABLE_FULL_TEXT_RETRIEVAL = True

    def execute(self, task):
        ranker = PaperRanker()

        papers = task.papers.get_all()

        if not papers:
            log(
                "Ranking",
                "Нет статей для ранжирования.",
            )

            task.memory.set(
                "ranking_report",
                [],
            )

            task.memory.set(
                "full_text_report",
                {
                    "total_papers": 0,
                    "available": 0,
                    "unavailable": 0,
                    "failed": 0,
                    "not_attempted": 0,
                    "formats": {},
                    "sources": {},
                    "papers": [],
                },
            )

            task.result = []

            return []

        search_query = task.memory.get(
            "search_query",
            "",
        )

        log(
            "Ranking",
            (
                f"Получено статей: {len(papers)}; "
                f"поисковый запрос: {search_query}"
            ),
        )

        for paper in papers:
            breakdown = ranker.explain(
                paper,
                search_query,
            )

            paper.score = breakdown[
                "total_score"
            ]

            # Diagnostic details are attached directly to the paper.
            paper.ranking_breakdown = breakdown

        papers.sort(
            key=lambda paper: paper.score,
            reverse=True,
        )

        selected_papers = papers[
            :self.TOP_PAPERS
        ]

        rejected_papers = papers[
            self.TOP_PAPERS:
        ]

        task.papers.clear()

        task.papers.add_many(
            selected_papers
        )

        task.memory.set(
            "ranked_papers_count",
            len(selected_papers),
        )

        task.memory.set(
            "rejected_papers_count",
            len(rejected_papers),
        )

        ranking_report = []

        for position, paper in enumerate(
            selected_papers,
            start=1,
        ):
            ranking_item = {
                "position": position,
                "title": paper.title,
                "score": paper.score,
                "breakdown": paper.ranking_breakdown,
            }

            ranking_report.append(
                ranking_item
            )

            log(
                "Ranking",
                (
                    f"{position}. "
                    f"{paper.title} — "
                    f"{paper.score} баллов"
                ),
            )

        task.memory.set(
            "ranking_report",
            ranking_report,
        )

        log(
            "Ranking",
            (
                f"Для Summarizer отобрано: "
                f"{len(selected_papers)} статей; "
                f"исключено после ранжирования: "
                f"{len(rejected_papers)}"
            ),
        )

        full_text_report = self._retrieve_full_texts(
            selected_papers
        )

        task.memory.set(
            "full_text_report",
            full_text_report,
        )

        task.result = selected_papers

        return selected_papers

    def _retrieve_full_texts(
        self,
        selected_papers,
    ):
        """
        Retrieve open full texts only for papers selected by Ranking.
        """

        if not self.ENABLE_FULL_TEXT_RETRIEVAL:
            log(
                "FullText",
                "Поиск полных текстов отключён в RankingAgent.",
            )

            for paper in selected_papers:
                paper.full_text_status = "not_attempted"

            return {
                "total_papers": len(selected_papers),
                "available": 0,
                "unavailable": 0,
                "failed": 0,
                "not_attempted": len(selected_papers),
                "formats": {},
                "sources": {},
                "papers": [],
            }

        service = FullTextService()

        report = service.retrieve(
            selected_papers
        )

        log(
            "Ranking",
            (
                "Результат поиска полных текстов: "
                f"доступно={report.get('available', 0)}; "
                f"недоступно={report.get('unavailable', 0)}; "
                f"ошибок={report.get('failed', 0)}"
            ),
        )

        return report