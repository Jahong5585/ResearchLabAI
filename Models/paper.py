from dataclasses import dataclass
from typing import List


@dataclass
class Paper:

    title: str

    authors: List[str]

    journal: str

    publisher: str

    year: int | None

    paper_type: str

    citations: int

    doi: str

    url: str

    abstract: str = ""

    score: float = 0.0