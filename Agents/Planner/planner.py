from Agents.base_agent import BaseAgent

from Models.plan import Plan
from Models.plan_step import PlanStep


class Planner(BaseAgent):

    PROMPT_NAME = "planner"

    MODEL_NAME = "PLANNER_MODEL"

    def execute(self, task):

        prompt = f"""
Твоя задача — построить план выполнения задачи.

Используй только существующих агентов.

Допустимые агенты:

Researcher
Ranking
Summarizer
Cluster
Outline
Writer
Reviewer
Translator
Programmer

Каждый агент может встречаться только ОДИН раз.

Ответ должен быть строго в формате:

Agent|Goal

Пример:

Researcher|Find scientific papers
Ranking|Rank papers by quality
Summarizer|Summarize papers
Cluster|Cluster studies
Outline|Create outline
Writer|Write literature review

Без JSON.
Без Markdown.
Без нумерации.

Запрос пользователя:

{task}
"""

        answer = self.ask_llm(prompt)

        plan = Plan()

        added_agents = set()

        for line in answer.splitlines():

            line = line.strip()

            if not line:
                continue

            if "|" not in line:
                continue

            agent, goal = line.split("|", 1)

            agent = agent.strip()
            goal = goal.strip()

            if agent in added_agents:
                continue

            added_agents.add(agent)

            plan.add(
                PlanStep(
                    agent,
                    goal
                )
            )

        return plan