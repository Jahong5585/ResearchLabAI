from Core.event_logger import log
from Core.paper_ranker import PaperRanker


class RankingAgent:
    """
    Ranks all retrieved papers and keeps only the most relevant ones.

    Ranking is deterministic and does not use an LLM.
    Therefore, this stage does not consume model credits.
    """

    # Maximum number of papers passed to Summarizer.
    TOP_PAPERS = 10

    def execute(self, task):
        ranker = PaperRanker()

        papers = task.papers.get_all()

        if not papers:
            log(
                "Ranking",
                "Нет статей для ранжирования.",
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

            # Save score details for diagnostics.
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
            ranking_report.append(
                {
                    "position": position,
                    "title": paper.title,
                    "score": paper.score,
                    "breakdown": (
                        paper.ranking_breakdown
                    ),
                }
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

        task.result = selected_papers

        return selected_papers