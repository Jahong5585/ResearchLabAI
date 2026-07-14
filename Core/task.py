from Core.memory import Memory
from Core.paper_repository import PaperRepository


class Task:
    """
    Stores the state and results of one ResearchLab AI workflow.
    """

    def __init__(self, user_request, plan=None):
        self.user_request = user_request
        self.plan = plan

        self.memory = Memory()
        self.current_agent = None
        self.result = None

        # Retrieved and ranked publications.
        self.papers = PaperRepository()

        # Structured extraction for every selected publication.
        self.article_summaries = []

        # Deterministic article-by-article comparison matrix.
        self.comparison_matrix = []

        # Evidence and citation validation.
        self.evidences = []
        self.citation_errors = []

        # Thematic organization.
        self.clusters = []
        self.outline = None

        # Cross-paper synthesis.
        self.synthesis_report = None

        # Final writing and review.
        self.literature_review = ""
        self.review = None