from __future__ import annotations

from collections import Counter
from typing import Any

from Core.event_logger import log
from Core.full_text_loader import FullTextLoader


class FullTextService:
    """
    Retrieves openly accessible full texts for papers selected by Ranking.

    The service:

    - processes only the supplied papers;
    - does not use an LLM;
    - does not consume model credits;
    - preserves the abstract when full text is unavailable;
    - records a transparent retrieval report.

    Retrieval is sequential to avoid unnecessary request bursts
    and publisher rate-limit problems.
    """

    def __init__(
        self,
        loader: FullTextLoader | None = None,
    ):
        self.loader = loader or FullTextLoader()

    def retrieve(
        self,
        papers,
    ) -> dict[str, Any]:
        """
        Attempt full-text retrieval for every supplied paper.

        Returns a summary report.
        """

        paper_list = list(
            papers or []
        )

        report: dict[str, Any] = {
            "total_papers": len(paper_list),
            "available": 0,
            "unavailable": 0,
            "failed": 0,
            "not_attempted": 0,
            "formats": {},
            "sources": {},
            "papers": [],
        }

        if not paper_list:
            log(
                "FullText",
                "Нет статей для загрузки полного текста.",
            )

            return report

        log(
            "FullText",
            (
                "Начат поиск открытых полных текстов: "
                f"{len(paper_list)} статей"
            ),
        )

        format_counter = Counter()
        source_counter = Counter()

        for article_number, paper in enumerate(
            paper_list,
            start=1,
        ):
            title = self._text(
                getattr(
                    paper,
                    "title",
                    "",
                )
            )

            log(
                "FullText",
                (
                    f"ARTICLE {article_number}: "
                    f"поиск полного текста — {title}"
                ),
            )

            try:
                self.loader.load(
                    paper
                )

            except Exception as error:
                paper.full_text_status = "failed"
                paper.full_text_error = (
                    f"{type(error).__name__}: {error}"
                )

            status = self._normalize_status(
                getattr(
                    paper,
                    "full_text_status",
                    "not_attempted",
                )
            )

            report[status] += 1

            document_format = self._text(
                getattr(
                    paper,
                    "full_text_format",
                    "",
                )
            )

            source = self._text(
                getattr(
                    paper,
                    "full_text_source",
                    "",
                )
            )

            if document_format:
                format_counter[
                    document_format
                ] += 1

            if source:
                source_counter[
                    source
                ] += 1

            sections = getattr(
                paper,
                "full_text_sections",
                {},
            ) or {}

            full_text = self._text(
                getattr(
                    paper,
                    "full_text",
                    "",
                )
            )

            paper_report = {
                "article_number": article_number,
                "title": title,
                "status": status,
                "full_text_url": self._text(
                    getattr(
                        paper,
                        "full_text_url",
                        "",
                    )
                ),
                "source": source,
                "format": document_format,
                "text_characters": len(
                    full_text
                ),
                "sections": sorted(
                    sections.keys()
                ),
                "error": self._text(
                    getattr(
                        paper,
                        "full_text_error",
                        "",
                    )
                ),
            }

            report["papers"].append(
                paper_report
            )

            if status == "available":
                log(
                    "FullText",
                    (
                        f"ARTICLE {article_number}: полный текст найден; "
                        f"формат={document_format or 'unknown'}; "
                        f"символов={len(full_text)}; "
                        f"разделы={sorted(sections.keys())}"
                    ),
                )

            elif status == "unavailable":
                log(
                    "FullText",
                    (
                        f"ARTICLE {article_number}: "
                        "открытый полный текст не найден."
                    ),
                )

            elif status == "failed":
                log(
                    "FullText",
                    (
                        f"ARTICLE {article_number}: ошибка загрузки — "
                        f"{paper_report['error']}"
                    ),
                )

            else:
                log(
                    "FullText",
                    (
                        f"ARTICLE {article_number}: "
                        "загрузка не была выполнена."
                    ),
                )

        report["formats"] = dict(
            format_counter
        )

        report["sources"] = dict(
            source_counter
        )

        log(
            "FullText",
            (
                "Поиск полного текста завершён: "
                f"доступно={report['available']}; "
                f"недоступно={report['unavailable']}; "
                f"ошибок={report['failed']}; "
                f"не обработано={report['not_attempted']}"
            ),
        )

        return report

    @staticmethod
    def _normalize_status(
        status: Any,
    ) -> str:
        normalized = str(
            status or "not_attempted"
        ).strip().casefold()

        allowed_statuses = {
            "available",
            "unavailable",
            "failed",
            "not_attempted",
        }

        if normalized not in allowed_statuses:
            return "failed"

        return normalized

    @staticmethod
    def _text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        return str(
            value
        ).strip()