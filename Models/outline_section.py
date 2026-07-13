from dataclasses import dataclass, field


@dataclass
class OutlineSection:

    title: str

    description: str = ""

    clusters: list = field(default_factory=list)