from __future__ import annotations

import re
from typing import Any


class FullTextContextBuilder:
    """
    Builds a compact source context for Summarizer.

    The builder uses:

    - bibliographic metadata;
    - the available abstract;
    - selected full-text sections when available.

    It never sends the complete PDF text to the LLM.
    This limits token usage and model costs.
    """

    MAX_TOTAL_CHARACTERS = 16000
    MAX_ABSTRACT_CHARACTERS = 3500

    SECTION_PRIORITY = (
        "methodology",
        "results",
        "limitations",
        "discussion",
        "conclusion",
        "introduction",
    )

    SECTION_CHARACTER_LIMITS = {
        "methodology": 4500,
        "results": 4500,
        "limitations": 2500,
        "discussion": 2500,
        "conclusion": 2000,
        "introduction": 1500,
    }

    SECTION_LABELS = {
        "methodology": "METHODOLOGY",
        "results": "RESULTS",
        "limitations": "LIMITATIONS",
        "discussion": "DISCUSSION",
        "conclusion": "CONCLUSION",
        "introduction": "INTRODUCTION",
    }

    @classmethod
    def build(
        cls,
        paper,
    ) -> dict[str, Any]:
        """
        Build a compact source package for one Paper.

        Returns:

        {
            "source_scope": "ABSTRACT_ONLY" or "FULL_TEXT_SECTIONS",
            "source_sections": [...],
            "source_text": "...",
            "source_text_characters": 12345,
            "full_text_url": "...",
            "full_text_source": "..."
        }
        """

        abstract = cls._clean_text(
            getattr(
                paper,
                "abstract",
                "",
            )
        )

        abstract_excerpt = cls._truncate_text(
            abstract,
            cls.MAX_ABSTRACT_CHARACTERS,
        )

        full_text_status = cls._text(
            getattr(
                paper,
                "full_text_status",
                "",
            )
        ).casefold()

        raw_sections = getattr(
            paper,
            "full_text_sections",
            {},
        )

        if not isinstance(
            raw_sections,
            dict,
        ):
            raw_sections = {}

        selected_sections = cls._select_sections(
            raw_sections
        )

        has_full_text_sections = (
            full_text_status == "available"
            and bool(selected_sections)
        )

        if has_full_text_sections:
            source_scope = "FULL_TEXT_SECTIONS"
        else:
            source_scope = "ABSTRACT_ONLY"
            selected_sections = {}

        source_text = cls._build_source_text(
            source_scope=source_scope,
            abstract=abstract_excerpt,
            selected_sections=selected_sections,
        )

        return {
            "source_scope": source_scope,
            "source_sections": list(
                selected_sections.keys()
            ),
            "source_text": source_text,
            "source_text_characters": len(
                source_text
            ),
            "full_text_url": cls._text(
                getattr(
                    paper,
                    "full_text_url",
                    "",
                )
            ),
            "full_text_source": cls._text(
                getattr(
                    paper,
                    "full_text_source",
                    "",
                )
            ),
        }

    @classmethod
    def _select_sections(
        cls,
        raw_sections: dict[str, Any],
    ) -> dict[str, str]:
        """
        Select and truncate the most useful scientific sections.
        """

        selected_sections: dict[str, str] = {}

        remaining_characters = (
            cls.MAX_TOTAL_CHARACTERS
            - cls.MAX_ABSTRACT_CHARACTERS
        )

        for section_name in cls.SECTION_PRIORITY:
            if remaining_characters <= 0:
                break

            raw_text = raw_sections.get(
                section_name,
                "",
            )

            cleaned_text = cls._clean_text(
                raw_text
            )

            if not cleaned_text:
                continue

            section_limit = min(
                cls.SECTION_CHARACTER_LIMITS.get(
                    section_name,
                    2000,
                ),
                remaining_characters,
            )

            section_excerpt = cls._truncate_text(
                cleaned_text,
                section_limit,
            )

            if not section_excerpt:
                continue

            selected_sections[
                section_name
            ] = section_excerpt

            remaining_characters -= len(
                section_excerpt
            )

        return selected_sections

    @classmethod
    def _build_source_text(
        cls,
        source_scope: str,
        abstract: str,
        selected_sections: dict[str, str],
    ) -> str:
        parts = [
            f"SOURCE SCOPE: {source_scope}",
        ]

        if abstract:
            parts.extend(
                [
                    "",
                    "ABSTRACT",
                    abstract,
                ]
            )

        for section_name, section_text in (
            selected_sections.items()
        ):
            label = cls.SECTION_LABELS.get(
                section_name,
                section_name.upper(),
            )

            parts.extend(
                [
                    "",
                    f"FULL-TEXT SECTION: {label}",
                    section_text,
                ]
            )

        return "\n".join(
            parts
        ).strip()

    @staticmethod
    def _truncate_text(
        text: str,
        max_characters: int,
    ) -> str:
        """
        Truncate text preferably at a paragraph or sentence boundary.
        """

        if max_characters <= 0:
            return ""

        if len(text) <= max_characters:
            return text

        candidate = text[
            :max_characters
        ]

        paragraph_position = candidate.rfind(
            "\n\n"
        )

        sentence_positions = [
            candidate.rfind(". "),
            candidate.rfind("? "),
            candidate.rfind("! "),
        ]

        sentence_position = max(
            sentence_positions
        )

        cut_position = max(
            paragraph_position,
            sentence_position,
        )

        minimum_safe_position = int(
            max_characters * 0.65
        )

        if cut_position >= minimum_safe_position:
            candidate = candidate[
                :cut_position + 1
            ]

        return (
            candidate.rstrip()
            + "\n[SECTION TRUNCATED]"
        )

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        text = str(
            value
        )

        text = text.replace(
            "\x00",
            " ",
        )

        text = (
            text
            .replace(
                "\r\n",
                "\n",
            )
            .replace(
                "\r",
                "\n",
            )
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n[ \t]+",
            "\n",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    @staticmethod
    def _text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        return str(
            value
        ).strip()