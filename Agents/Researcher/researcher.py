from Agents.base_agent import BaseAgent

from Core.research_service import ResearchService
from Core.query_optimizer import QueryOptimizer
from Core.event_logger import log
from Core.corpus_analyzer import CorpusAnalyzer


class Researcher(BaseAgent):

    PROMPT_NAME = "researcher"
    MODEL_NAME = "RESEARCHER_MODEL"

    def execute(self, task):

        optimizer = QueryOptimizer()

        search_query = optimizer.optimize(
            task.user_request
        )

        log(
            "Researcher",
            f"Поисковый запрос: {search_query}"
        )

        service = ResearchService()

        papers = service.search(
            search_query,
            rows=25
        )

        log(
            "Researcher",
            f"ResearchService вернул: {len(papers)} статей"
        )

        task.papers.clear()

        task.papers.add_many(papers)

        log(
            "Researcher",
            f"После добавления в PaperRepository: {task.papers.count()} статей"
        )

        report = CorpusAnalyzer.build(
            task.papers.get_all()
        )

        task.memory.set(
            "search_query",
            search_query
        )

        task.memory.set(
            "papers_count",
            task.papers.count()
        )

        task.memory.set(
            "corpus_report",
            report
        )

        task.memory.set(
            "papers",
            task.papers.get_all()
        )

        return None