from Agents.base_agent import BaseAgent

from Models.outline_section import OutlineSection


class OutlineAgent(BaseAgent):

    PROMPT_NAME = "outline"
    MODEL_NAME = "OUTLINE_MODEL"

    def execute(self, task):

        outline = []

        for cluster in task.clusters:

            section = OutlineSection(

                title=cluster.topic,

                description=f"Обзор исследований по теме {cluster.topic}"

            )

            section.clusters.append(cluster)

            outline.append(section)

        task.outline = outline

        task.result = task

        return task