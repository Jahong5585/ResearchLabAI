import json

from Agents.Synthesis.synthesis_agent import SynthesisAgent
from Agents.Writer.writer import WriterAgent
from Core.task import Task
from Models.article_summary import ArticleSummary
from Models.outline_section import OutlineSection


def test_synthesis_to_writer_pipeline_without_api(monkeypatch):
    task = Task("Write an analytical review")
    task.article_summaries = [
        ArticleSummary(
            title="Study one",
            authors="A. Author",
            year=2023,
            journal="Journal A",
            doi="10.1/a",
            study_type="Survey",
            methodology="Questionnaire",
            findings="Positive attitudes were reported.",
        ),
        ArticleSummary(
            title="Study two",
            authors="B. Author",
            year=2024,
            journal="Journal B",
            doi="10.1/b",
            study_type="Survey",
            methodology="Questionnaire",
            findings="Positive attitudes were reported.",
        ),
    ]
    task.outline = [OutlineSection(title="Attitudes")]

    synthesis_payload = {
        "overview": "Two studies were compared.",
        "claims": [
            {
                "claim_type": "CONSENSUS",
                "statement": "Both studies report positive attitudes.",
                "supporting_articles": [1, 2],
                "contradicting_articles": [],
                "confidence": "Medium",
                "rationale": "Both extracted findings have the same direction.",
                "caveats": ["Both studies used surveys."],
            }
        ],
        "methodology_patterns": ["Both studies used questionnaires."],
        "trends": [],
        "contradictions": [],
        "gaps": [],
        "recurring_limitations": [],
    }

    monkeypatch.setattr(
        SynthesisAgent,
        "ask_llm",
        lambda self, prompt: json.dumps(synthesis_payload),
    )

    SynthesisAgent().execute(task)

    captured = {}

    def fake_writer(self, prompt):
        captured["prompt"] = prompt
        return "Both studies report positive attitudes [ARTICLE 1; ARTICLE 2]."

    monkeypatch.setattr(WriterAgent, "ask_llm", fake_writer)
    result = WriterAgent().execute(task)

    assert task.synthesis_report.claims[0].supporting_articles == [1, 2]
    assert "Both studies report positive attitudes" in captured["prompt"]
    assert result.endswith("[ARTICLE 1; ARTICLE 2].")
