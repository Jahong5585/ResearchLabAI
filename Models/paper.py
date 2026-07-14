from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Paper:
    """
    Represents one scientific publication.

    The object stores bibliographic metadata, the available abstract
    and, when accessible, extracted full-text content.

    Full-text fields have safe defaults, so existing search tools
    and tests remain backward compatible.
    """

    # Bibliographic metadata.
    title: str
    authors: List[str]
    journal: str
    publisher: str
    year: int | None
    paper_type: str
    citations: int
    doi: str
    url: str

    # Abstract and ranking.
    abstract: str = ""
    score: float = 0.0

    # Full-text retrieval status.
    #
    # Allowed values:
    # not_attempted
    # available
    # unavailable
    # failed
    full_text_status: str = "not_attempted"

    # Direct location of the retrieved PDF, XML or HTML document.
    full_text_url: str = ""

    # Source from which the full text was obtained.
    #
    # Examples:
    # Unpaywall
    # Crossref
    # OpenAlex
    # PubMed Central
    # arXiv
    # Publisher
    full_text_source: str = ""

    # Retrieved document format.
    #
    # Examples:
    # pdf
    # xml
    # html
    # text
    full_text_format: str = ""

    # Extracted complete plain text.
    full_text: str = ""

    # Important sections extracted from the complete text.
    #
    # Example:
    # {
    #     "introduction": "...",
    #     "methodology": "...",
    #     "results": "...",
    #     "limitations": "...",
    #     "conclusion": "..."
    # }
    full_text_sections: Dict[str, str] = field(
        default_factory=dict
    )

    # Retrieval or extraction error message.
    full_text_error: str = ""