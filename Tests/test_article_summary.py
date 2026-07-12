from Models.article_summary import ArticleSummary


def main():

    summary = ArticleSummary(

        title="Artificial Intelligence in Education",

        authors="Lijia Chen",

        year=2020,

        journal="IEEE Access",

        doi="10.1109/access.2020.2988510",

        problem="Application of AI in education",

        methodology="Literature Review",

        findings="AI improves learning and administration",

        limitations="Need more empirical studies",

        conclusion="AI has high potential in education",

        keywords=[
            "AI",
            "Education",
            "Machine Learning"
        ]

    )

    print(summary)


if __name__ == "__main__":
    main()