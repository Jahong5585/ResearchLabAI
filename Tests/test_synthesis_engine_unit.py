from Core.synthesis_engine import SynthesisEngine
from Models.article_summary import ArticleSummary


def make_summaries():
    return [
        ArticleSummary(
            title="Study one",
            year=2023,
            study_type="Survey",
            methodology="Questionnaire",
            country="Uzbekistan",
            findings="Students reported positive attitudes.",
            limitations="Small sample",
        ),
        ArticleSummary(
            title="Study two",
            year=2024,
            study_type="Survey",
            methodology="Questionnaire",
            country="Kazakhstan",
            findings="Students reported positive attitudes.",
            limitations="Small sample",
        ),
        ArticleSummary(
            title="Study three",
            year=2024,
            study_type="Experimental study",
            methodology="Controlled experiment",
            country="Uzbekistan",
            findings="No measurable improvement was found.",
            limitations="Short study period",
        ),
    ]


def test_statistics_and_valid_claims():
    summaries = make_summaries()
    data = {
        "overview": "Three studies were compared.",
        "claims": [
            {
                "claim_type": "MAJORITY_PATTERN",
                "statement": "Two studies reported positive attitudes.",
                "supporting_articles": [1, 2],
                "contradicting_articles": [],
                "confidence": "Medium",
                "rationale": "The two survey records report the same direction.",
                "caveats": ["The outcome was attitude, not achievement."],
            }
        ],
        "methodology_patterns": ["Survey methods were most frequent."],
        "trends": [],
        "contradictions": [],
        "gaps": [],
        "recurring_limitations": ["Small samples recurred."],
    }

    report = SynthesisEngine.from_llm_data(data, summaries)

    assert report.aggregate_statistics["total_articles"] == 3
    assert report.aggregate_statistics["study_types"]["Survey"] == 2
    assert report.claims[0].supporting_articles == [1, 2]
    assert report.validation_errors == []


def test_invalid_article_reference_is_removed():
    summaries = make_summaries()
    data = {
        "claims": [
            {
                "claim_type": "CONSENSUS",
                "statement": "Unsupported claim.",
                "supporting_articles": [99],
                "contradicting_articles": [],
                "confidence": "High",
            }
        ]
    }

    report = SynthesisEngine.from_llm_data(data, summaries)
    assert report.validation_errors

    report = SynthesisEngine.remove_invalid_claims(report, len(summaries))
    assert report.claims == []
