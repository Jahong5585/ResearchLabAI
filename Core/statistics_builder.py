from collections import Counter


class StatisticsBuilder:

    @staticmethod
    def build(papers):

        years = Counter()
        journals = Counter()
        publishers = Counter()
        keywords = Counter()

        citations = []

        doi_count = 0

        for paper in papers:

            if paper.year:
                years[paper.year] += 1

            if paper.journal:
                journals[paper.journal] += 1

            if paper.publisher:
                publishers[paper.publisher] += 1

            if paper.doi:
                doi_count += 1

            citations.append(
                getattr(paper, "citations", 0)
            )

        top_cited = sorted(

            papers,

            key=lambda x: getattr(
                x,
                "citations",
                0
            ),

            reverse=True

        )[:5]

        average_citations = 0

        if citations:

            average_citations = round(

                sum(citations) /

                len(citations),

                2

            )

        return {

            "papers": len(papers),

            "years": dict(

                sorted(

                    years.items()

                )

            ),

            "journals": journals.most_common(10),

            "publishers": publishers.most_common(10),

            "doi_count": doi_count,

            "average_citations": average_citations,

            "top_cited": top_cited

        }