import json

from Core.article_summary_parser import ArticleSummaryParser
from Models.paper import Paper


def make_paper():
    return Paper(
        title="AI in Education",
        authors=["A. Author"],
        journal="Test Journal",
        publisher="Test Publisher",
        year=2025,
        paper_type="journal-article",
        citations=10,
        doi="10.1000/test",
        url="https://example.org",
        abstract="A study of AI in higher education.",
    )


def test_json_summary_parsing():
    payload = {
        "Keywords": ["AI", "Education"],
        "ResearchObjective": "Evaluate AI use.",
        "StudyType": "Survey",
        "Methodology": "Questionnaire",
        "Findings": "Positive attitudes were reported.",
        "VerifiedFacts": [
            "The study used a questionnaire.",
            "The study focused on higher education.",
        ],
    }

    summary = ArticleSummaryParser.parse(
        json.dumps(payload),
        make_paper(),
    )

    assert summary.title == "AI in Education"
    assert summary.keywords == ["AI", "Education"]
    assert summary.study_type == "Survey"
    assert len(summary.verified_facts) == 2
    assert summary.country == "Not specified"
