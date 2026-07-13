from dataclasses import dataclass


@dataclass
class Citation:

    index: int

    title: str

    authors: str

    journal: str

    year: int | None

    doi: str

    url: str

    def format(self):

        return (
            f"[{self.index}] "
            f"{self.authors} "
            f"({self.year}). "
            f"{self.title}. "
            f"{self.journal}. "
            f"DOI: {self.doi}"
        )