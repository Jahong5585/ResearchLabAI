from dataclasses import dataclass, field

from Models.article_summary import ArticleSummary


@dataclass
class Cluster:

    topic: str

    articles: list[ArticleSummary] = field(default_factory=list)

    keywords: list[str] = field(default_factory=list)