class Plan:

    def __init__(self):

        self.steps = []

    def add(self, step):

        self.steps.append(step)

    def clear(self):

        self.steps.clear()

    def size(self):

        return len(self.steps)

    def __iter__(self):

        return iter(self.steps)

    def __repr__(self):

        return "\n".join(
            str(step)
            for step in self.steps
        )