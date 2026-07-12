from Core.statistics_builder import StatisticsBuilder


class PaperContextBuilder:

    @staticmethod
    def build(papers):

        statistics = StatisticsBuilder.build(
            papers
        )

        text = f"""
==============================
STATISTICS

Total papers:
{statistics["papers"]}

Papers with DOI:
{statistics["doi_count"]}

Average citations:
{statistics["average_citations"]}

Publication years:

"""

        for year, count in statistics["years"].items():

            text += f"{year}: {count}\n"

        text += "\nTop cited papers:\n\n"

        for paper in statistics["top_cited"]:

            text += f"""

Title:
{paper.title}

Year:
{paper.year}

Citations:
{paper.citations}

DOI:
{paper.doi}

"""

        text += "\n==============================\n"

        for index, paper in enumerate(

            papers,

            start=1

        ):

            text += f"""

==================================================
Paper {index}

Title:
{paper.title}

Authors:
{", ".join(paper.authors)}

Journal:
{paper.journal}

Year:
{paper.year}

Citations:
{paper.citations}

DOI:
{paper.doi}

Abstract:
{paper.abstract if paper.abstract else "Abstract not available."}
"""

        return text