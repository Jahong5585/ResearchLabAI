from Core.paper_ranker import PaperRanker


class RankingAgent:

    def execute(self, task):

        ranker = PaperRanker()

        papers = task.papers.get_all()

        for paper in papers:

            paper.score = ranker.calculate(paper)

        papers.sort(
            key=lambda paper: paper.score,
            reverse=True
        )

        task.papers.clear()
        task.papers.add_many(papers)

        task.result = papers

        return papers