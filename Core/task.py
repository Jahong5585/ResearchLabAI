from Core.memory import Memory
from Core.paper_repository import PaperRepository


class Task:
    def __init__(self, user_request, plan=None):
        self.user_request = user_request
        self.plan = plan
        self.memory = Memory()
        self.current_agent = None
        self.result = None

        self.papers = PaperRepository()
        self.article_summaries = []
        self.evidences = []
        self.citation_errors = []
        self.clusters = []
        self.outline = None
        self.synthesis_report = None
        self.literature_review = ""
        self.review = None
