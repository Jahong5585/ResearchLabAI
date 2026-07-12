from Agents.base_agent import BaseAgent

from Models.cluster import Cluster


class ClusterAgent(BaseAgent):

    PROMPT_NAME = "cluster"
    MODEL_NAME = "CLUSTER_MODEL"

    def execute(self, task):

        clusters = {}

        for article in task.article_summaries:

            topic = "Other"

            if article.keywords:
                topic = article.keywords[0]

            if topic not in clusters:

                clusters[topic] = Cluster(
                    topic=topic
                )

            clusters[topic].articles.append(
                article
            )

            for keyword in article.keywords:

                if keyword not in clusters[topic].keywords:

                    clusters[topic].keywords.append(
                        keyword
                    )

        task.clusters = list(
            clusters.values()
        )

        return task