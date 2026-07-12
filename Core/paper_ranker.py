from datetime import datetime


class PaperRanker:

    def calculate(self, paper):

        score = 0.0

        # Цитирования
        score += min(paper.citations / 1000, 10)

        # Новизна статьи
        if paper.year:

            age = datetime.now().year - paper.year

            score += max(0, 5 - age * 0.2)

        # DOI
        if paper.doi:
            score += 2

        # Аннотация
        if paper.abstract:
            score += 1

        return round(score, 2)