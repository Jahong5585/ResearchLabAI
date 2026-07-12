from Models.paper import Paper


class PaperSorter:

    @staticmethod
    def sort_by_citations(papers: list[Paper], reverse: bool = True):

        return sorted(
            papers,
            key=lambda paper: paper.citations,
            reverse=reverse
        )