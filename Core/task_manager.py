from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:

    title: str
    description: str

    status: str = "pending"

    assigned_agent: str | None = None

    subtasks: List["Task"] = field(default_factory=list)