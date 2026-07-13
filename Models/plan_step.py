class PlanStep:

    def __init__(self, agent, goal):

        self.agent = agent
        self.goal = goal

    def __repr__(self):

        return (
            f"PlanStep("
            f"agent='{self.agent}', "
            f"goal='{self.goal}')"
        )