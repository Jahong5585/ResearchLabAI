from collections import Counter


class CorpusAnalyzer:

    @staticmethod
    def build(papers):

        report = {}

        report["papers_count"] = len(papers)

        # -------------------------
        # Годы публикации
        # -------------------------

        years = Counter()

        for paper in papers:

            if paper.year:

                years[paper.year] += 1

        report["years"] = dict(

            sorted(

                years.items()

            )

        )

        # -------------------------
        # Типы публикаций
        # -------------------------

        types = Counter()

        for paper in papers:

            if paper.paper_type:

                types[paper.paper_type] += 1

        report["paper_types"] = dict(types)

        # -------------------------
        # Журналы
        # -------------------------

        journals = Counter()

        for paper in papers:

            if paper.journal:

                journals[paper.journal] += 1

        report["journals"] = journals.most_common(10)

        # -------------------------
        # Издатели
        # -------------------------

        publishers = Counter()

        for paper in papers:

            if paper.publisher:

                publishers[paper.publisher] += 1

        report["publishers"] = publishers.most_common(10)

        # -------------------------
        # Цитируемость
        # -------------------------

        citations = [

            paper.citations

            for paper in papers

        ]

        if citations:

            report["average_citations"] = round(

                sum(citations) /

                len(citations),

                2

            )

        else:

            report["average_citations"] = 0

        report["top_cited"] = sorted(

            papers,

            key=lambda x: x.citations,

            reverse=True

        )[:5]

        return report
    