from Core.task import Task
from Core.workflow import Workflow
from Core.event_logger import log
from Core.workflow_builder import WorkflowBuilder


class Orchestrator:

    def execute(self, user_request, plan=None):

        task = Task(
            user_request=user_request,
            plan=plan
        )

        plan = WorkflowBuilder.build(
            user_request,
            plan
        )

        workflow = Workflow(task)

        if plan is not None:

            for step in plan:

                workflow.add(step.agent)

            log(
                "Orchestrator",
                f"Workflow создан ({workflow.size()} шагов)"
            )

        return workflow.run()