from Core.agent_registry import get
from Core.event_logger import log


class Workflow:

    def __init__(self, task):

        self.task = task

        self.steps = []

    def add(self, agent_name):

        self.steps.append(agent_name)

    def size(self):

        return len(self.steps)

    def run(self):

        for agent_name in self.steps:

            log(
                "Workflow",
                f"Запуск {agent_name}"
            )

            agent = get(agent_name)

            if agent is None:

                log(
                    "Workflow",
                    f"Агент {agent_name} не найден."
                )

                continue

            self.task.current_agent = agent_name

            agent.execute(self.task)

        if self.task.literature_review:

            self.task.result = self.task.literature_review

        return self.task