from collections import defaultdict

from Models.evidence import Evidence


class EvidenceBuilder:

    @staticmethod
    def build(article_summaries):

        evidence_map = defaultdict(list)

        for article in article_summaries:

            for keyword in article.keywords:

                keyword = keyword.strip()

                if keyword:

                    evidence_map[keyword].append(article)

        evidences = []

        for topic, articles in evidence_map.items():

            evidence = Evidence(topic=topic)

            evidence.supporting_articles.extend(articles)

            findings = []
            limitations = []

            for article in articles:

                if article.findings:
                    findings.append(article.findings)

                if article.limitations:
                    limitations.append(article.limitations)

            evidence.common_findings = findings
            evidence.common_limitations = limitations

            count = len(articles)

            if count >= 10:
                evidence.confidence = "High"

            elif count >= 5:
                evidence.confidence = "Medium"

            else:
                evidence.confidence = "Low"

            evidences.append(evidence)

        evidences.sort(
            key=lambda x: len(x.supporting_articles),
            reverse=True
        )

        return evidences