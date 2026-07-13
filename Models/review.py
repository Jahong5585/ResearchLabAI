from dataclasses import dataclass, field


@dataclass
class Review:

    score: float = 0.0

    strengths: list[str] = field(default_factory=list)

    weaknesses: list[str] = field(default_factory=list)

    missing_topics: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    decision: str = "approve"