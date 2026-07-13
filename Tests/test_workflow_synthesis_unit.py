from Core.workflow_builder import WorkflowBuilder


def test_literature_workflow_contains_synthesis_before_writer():
    plan = WorkflowBuilder.build(
        "Сделай обзор литературы по искусственному интеллекту",
        None,
    )
    agents = [step.agent for step in plan]

    assert "Synthesis" in agents
    assert agents.index("Synthesis") < agents.index("Writer")
