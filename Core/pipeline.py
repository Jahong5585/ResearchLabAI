class Pipeline:

    def __init__(self):

        self.steps = []

    def add(self, step):

        self.steps.append(step)

    def run(self, data):

        result = data

        for step in self.steps:

            result = step.execute(result)

        return result

    def clear(self):

        self.steps.clear()

    def size(self):

        return len(self.steps)