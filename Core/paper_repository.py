class PaperRepository:

    def __init__(self):

        self._papers = {}

    def _make_key(self, paper):

        if paper.doi:
            return paper.doi.strip().lower()

        return paper.title.strip().lower()

    def add(self, paper):

        self._papers[self._make_key(paper)] = paper

    def add_many(self, papers):

        for paper in papers:
            self.add(paper)

    def get_by_doi(self, doi):

        if not doi:
            return None

        return self._papers.get(doi.strip().lower())

    def get_by_title(self, title):

        if not title:
            return None

        return self._papers.get(title.strip().lower())

    def get_all(self):

        return list(self._papers.values())

    def top(self, limit=10):

        papers = self.get_all()

        papers.sort(
            key=lambda paper: getattr(paper, "score", 0),
            reverse=True
        )

        return papers[:limit]

    def count(self):

        return len(self._papers)

    def clear(self):

        self._papers.clear()