from Models.citation import Citation


class CitationBuilder:

    @staticmethod
    def build(papers):

        citations = []

        for index, paper in enumerate(papers, start=1):

            citation = Citation(

                index=index,

                title=paper.title,

                authors=", ".join(paper.authors),

                journal=paper.journal,

                year=paper.year,

                doi=paper.doi,

                url=paper.url

            )

            citations.append(citation)

        return citations