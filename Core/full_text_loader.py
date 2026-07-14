from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from io import BytesIO
from typing import Any
from urllib.parse import quote

import requests
from pypdf import PdfReader


class _VisibleTextParser(HTMLParser):
    """
    Extracts visible text from an HTML document.

    JavaScript, CSS, navigation and other non-article elements
    are ignored.
    """

    SKIP_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "form",
        "button",
        "nav",
        "header",
        "footer",
    }

    BLOCK_TAGS = {
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "figcaption",
        "figure",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "main",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self):
        super().__init__(
            convert_charrefs=True,
        )

        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ) -> None:
        tag = tag.casefold()

        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return

        if (
            self.skip_depth == 0
            and tag in self.BLOCK_TAGS
        ):
            self.parts.append("\n")

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = tag.casefold()

        if tag in self.SKIP_TAGS:
            if self.skip_depth > 0:
                self.skip_depth -= 1
            return

        if (
            self.skip_depth == 0
            and tag in self.BLOCK_TAGS
        ):
            self.parts.append("\n")

    def handle_data(
        self,
        data: str,
    ) -> None:
        if self.skip_depth > 0:
            return

        text = data.strip()

        if text:
            self.parts.append(text)

    def get_text(self) -> str:
        return "\n".join(self.parts)


class FullTextLoader:
    """
    Retrieves and extracts openly available scientific full text.

    Supported formats:

    - PDF;
    - HTML;
    - XML;
    - plain text.

    The loader does not call an LLM and does not consume model credits.

    It modifies and returns the supplied Paper object.
    """

    DEFAULT_TIMEOUT_SECONDS = 25
    DEFAULT_MAX_BYTES = 25 * 1024 * 1024

    MIN_PDF_TEXT_CHARACTERS = 1000
    MIN_HTML_TEXT_CHARACTERS = 4000
    MIN_XML_TEXT_CHARACTERS = 2000
    MIN_PLAIN_TEXT_CHARACTERS = 2000

    USER_AGENT = (
        "ResearchLabAI/0.1 "
        "(scientific full-text retrieval)"
    )

    SECTION_ALIASES = {
        "abstract": {
            "abstract",
            "summary",
            "аннотация",
            "резюме",
        },
        "introduction": {
            "introduction",
            "background",
            "введение",
            "предпосылки",
        },
        "methodology": {
            "method",
            "methods",
            "methodology",
            "materials and methods",
            "research methods",
            "study design",
            "метод",
            "методы",
            "методология",
            "материалы и методы",
            "дизайн исследования",
        },
        "results": {
            "result",
            "results",
            "findings",
            "результат",
            "результаты",
            "результаты исследования",
        },
        "discussion": {
            "discussion",
            "discussion and implications",
            "обсуждение",
        },
        "limitations": {
            "limitation",
            "limitations",
            "study limitations",
            "ограничение",
            "ограничения",
            "ограничения исследования",
        },
        "conclusion": {
            "conclusion",
            "conclusions",
            "concluding remarks",
            "заключение",
            "вывод",
            "выводы",
        },
        "references": {
            "reference",
            "references",
            "bibliography",
            "литература",
            "список литературы",
            "библиография",
        },
    }

    ARTICLE_SECTION_SIGNALS = {
        "introduction",
        "methodology",
        "results",
        "discussion",
        "conclusion",
        "references",
    }

    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept": (
                    "application/pdf,"
                    "application/xml,"
                    "text/xml,"
                    "text/html,"
                    "text/plain;q=0.9,"
                    "*/*;q=0.5"
                ),
            }
        )

    def load(self, paper):
        """
        Tries all available URLs and fills the full-text fields
        of the Paper object.
        """

        paper.full_text_status = "not_attempted"
        paper.full_text_error = ""
        paper.full_text = ""
        paper.full_text_sections = {}

        candidate_urls = self._build_candidate_urls(
            paper
        )

        if not candidate_urls:
            paper.full_text_status = "unavailable"
            paper.full_text_error = (
                "No URL or DOI is available for full-text retrieval."
            )
            return paper

        errors: list[str] = []
        received_response = False

        for candidate_url in candidate_urls:
            try:
                response = self.session.get(
                    candidate_url,
                    timeout=self.timeout_seconds,
                    allow_redirects=True,
                    stream=True,
                )

                received_response = True

                if response.status_code >= 400:
                    errors.append(
                        f"{candidate_url}: "
                        f"HTTP {response.status_code}"
                    )
                    continue

                content = self._read_limited_response(
                    response
                )

                document_format = self._detect_format(
                    content=content,
                    content_type=response.headers.get(
                        "Content-Type",
                        "",
                    ),
                    final_url=response.url,
                )

                extracted_text = self._extract_text(
                    content=content,
                    document_format=document_format,
                )

                extracted_text = self._clean_text(
                    extracted_text
                )

                sections = self.extract_sections(
                    extracted_text
                )

                if not self._is_probable_full_text(
                    text=extracted_text,
                    document_format=document_format,
                    sections=sections,
                ):
                    errors.append(
                        f"{response.url}: downloaded content does "
                        "not appear to contain a complete scientific text."
                    )
                    continue

                paper.full_text_status = "available"
                paper.full_text_url = response.url
                paper.full_text_source = self._identify_source(
                    response.url
                )
                paper.full_text_format = document_format
                paper.full_text = extracted_text
                paper.full_text_sections = sections
                paper.full_text_error = ""

                return paper

            except (
                requests.RequestException,
                ValueError,
                OSError,
                RuntimeError,
            ) as error:
                errors.append(
                    f"{candidate_url}: "
                    f"{type(error).__name__}: {error}"
                )

        paper.full_text_status = (
            "unavailable"
            if received_response
            else "failed"
        )

        paper.full_text_error = self._join_errors(
            errors
        )

        return paper

    def _build_candidate_urls(
        self,
        paper,
    ) -> list[str]:
        """
        Creates a list of possible document locations.
        """

        candidates: list[str] = []

        full_text_url = self._text(
            getattr(
                paper,
                "full_text_url",
                "",
            )
        )

        paper_url = self._text(
            getattr(
                paper,
                "url",
                "",
            )
        )

        doi = self._normalize_doi(
            getattr(
                paper,
                "doi",
                "",
            )
        )

        if full_text_url:
            candidates.append(
                full_text_url
            )

        if paper_url:
            candidates.append(
                paper_url
            )

        if doi:
            candidates.append(
                "https://doi.org/"
                + quote(
                    doi,
                    safe="/()",
                )
            )

        return self._unique_strings(
            candidates
        )

    def _read_limited_response(
        self,
        response: requests.Response,
    ) -> bytes:
        """
        Reads the response with a size limit.
        """

        content_length = response.headers.get(
            "Content-Length"
        )

        if content_length:
            try:
                declared_size = int(
                    content_length
                )
            except ValueError:
                declared_size = 0

            if declared_size > self.max_bytes:
                raise ValueError(
                    "The document exceeds the configured "
                    f"size limit of {self.max_bytes} bytes."
                )

        chunks: list[bytes] = []
        total_size = 0

        for chunk in response.iter_content(
            chunk_size=64 * 1024
        ):
            if not chunk:
                continue

            total_size += len(chunk)

            if total_size > self.max_bytes:
                raise ValueError(
                    "The downloaded document exceeds the configured "
                    f"size limit of {self.max_bytes} bytes."
                )

            chunks.append(chunk)

        return b"".join(chunks)

    @classmethod
    def _detect_format(
        cls,
        content: bytes,
        content_type: str,
        final_url: str,
    ) -> str:
        """
        Detects the downloaded document format.
        """

        lowered_type = (
            content_type
            .split(";")[0]
            .strip()
            .casefold()
        )

        lowered_url = (
            final_url
            .split("?")[0]
            .casefold()
        )

        stripped_content = content.lstrip()

        if (
            content.startswith(b"%PDF")
            or lowered_type == "application/pdf"
            or lowered_url.endswith(".pdf")
        ):
            return "pdf"

        if (
            "xml" in lowered_type
            or stripped_content.startswith(b"<?xml")
            or stripped_content.startswith(b"<article")
        ):
            return "xml"

        if (
            "html" in lowered_type
            or stripped_content[:20]
            .casefold()
            .startswith(b"<!doctype html")
            or stripped_content[:10]
            .casefold()
            .startswith(b"<html")
        ):
            return "html"

        if lowered_type.startswith("text/"):
            return "text"

        if b"<html" in stripped_content[:500].casefold():
            return "html"

        return "unknown"

    @classmethod
    def _extract_text(
        cls,
        content: bytes,
        document_format: str,
    ) -> str:
        """
        Extracts text according to the document format.
        """

        if document_format == "pdf":
            return cls._extract_pdf_text(
                content
            )

        decoded_text = cls._decode_bytes(
            content
        )

        if document_format == "html":
            return cls._extract_html_text(
                decoded_text
            )

        if document_format == "xml":
            return cls._extract_xml_text(
                decoded_text
            )

        if document_format == "text":
            return decoded_text

        return ""

    @staticmethod
    def _extract_pdf_text(
        content: bytes,
    ) -> str:
        """
        Extracts text from a PDF document using pypdf.
        """

        try:
            reader = PdfReader(
                BytesIO(content)
            )
        except Exception as error:
            raise RuntimeError(
                f"Unable to open PDF: {error}"
            ) from error

        page_texts: list[str] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            try:
                text = page.extract_text() or ""
            except Exception as error:
                text = (
                    f"\n[Page {page_number} extraction failed: "
                    f"{error}]\n"
                )

            if text.strip():
                page_texts.append(text)

        return "\n\n".join(
            page_texts
        )

    @staticmethod
    def _extract_html_text(
        html_text: str,
    ) -> str:
        """
        Extracts visible text from HTML.
        """

        parser = _VisibleTextParser()

        try:
            parser.feed(
                html_text
            )
            parser.close()
        except Exception as error:
            raise RuntimeError(
                f"Unable to parse HTML: {error}"
            ) from error

        return unescape(
            parser.get_text()
        )

    @staticmethod
    def _extract_xml_text(
        xml_text: str,
    ) -> str:
        """
        Extracts plain text from an XML document.
        """

        text = re.sub(
            r"<!\[CDATA\[(.*?)\]\]>",
            r"\1",
            xml_text,
            flags=re.DOTALL,
        )

        text = re.sub(
            r"<[^>]+>",
            "\n",
            text,
        )

        return unescape(text)

    @staticmethod
    def _decode_bytes(
        content: bytes,
    ) -> str:
        """
        Decodes downloaded text using common encodings.
        """

        for encoding in (
            "utf-8",
            "utf-8-sig",
            "windows-1251",
            "latin-1",
        ):
            try:
                return content.decode(
                    encoding
                )
            except UnicodeDecodeError:
                continue

        return content.decode(
            "utf-8",
            errors="replace",
        )

    @classmethod
    def extract_sections(
        cls,
        text: str,
    ) -> dict[str, str]:
        """
        Extracts standard scientific sections using heading heuristics.
        """

        cleaned_text = cls._clean_text(
            text
        )

        if not cleaned_text:
            return {}

        lines = cleaned_text.splitlines()

        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                continue

            detected_section = cls._detect_section_heading(
                line
            )

            if detected_section:
                current_section = detected_section

                sections.setdefault(
                    current_section,
                    [],
                )
                continue

            if current_section is not None:
                sections[current_section].append(
                    line
                )

        result: dict[str, str] = {}

        for section_name, section_lines in sections.items():
            section_text = cls._clean_text(
                "\n".join(section_lines)
            )

            if section_text:
                result[section_name] = section_text

        return result

    @classmethod
    def _detect_section_heading(
        cls,
        line: str,
    ) -> str | None:
        """
        Detects a scientific section heading.

        Numbering is removed only when a number or Roman numeral
        is followed by a separator.

        This prevents words such as Introduction, Methods,
        Limitations and Conclusion from losing their first letter.
        """

        if not line:
            return None

        if len(line) > 140:
            return None

        normalized = line.casefold().strip()

        # Supported examples:
        #
        # 1 Introduction
        # 1.2 Methods
        # II. Results
        # Section 3: Discussion
        #
        # A separator after the number is mandatory.
        normalized = re.sub(
            r"^\s*"
            r"(?:section\s+)?"
            r"(?:"
            r"\d+(?:\.\d+)*"
            r"|"
            r"[ivxlcdm]+"
            r")"
            r"(?=[\s.:\-–—)])"
            r"[\s.:\-–—)]*",
            "",
            normalized,
            flags=re.IGNORECASE,
        )

        normalized = re.sub(
            r"[\s:.\-–—]+$",
            "",
            normalized,
        )

        normalized = " ".join(
            normalized.split()
        )

        for section_name, aliases in cls.SECTION_ALIASES.items():
            normalized_aliases = {
                " ".join(
                    alias.casefold().split()
                )
                for alias in aliases
            }

            if normalized in normalized_aliases:
                return section_name

        return None

    @classmethod
    def _is_probable_full_text(
        cls,
        text: str,
        document_format: str,
        sections: dict[str, str],
    ) -> bool:
        """
        Checks whether the downloaded document probably contains
        a complete scientific text rather than a short landing page.
        """

        text_length = len(text)

        if document_format == "pdf":
            return (
                text_length
                >= cls.MIN_PDF_TEXT_CHARACTERS
            )

        if document_format == "xml":
            return (
                text_length
                >= cls.MIN_XML_TEXT_CHARACTERS
            )

        if document_format == "text":
            return (
                text_length
                >= cls.MIN_PLAIN_TEXT_CHARACTERS
            )

        if document_format == "html":
            detected_signals = (
                set(sections)
                & cls.ARTICLE_SECTION_SIGNALS
            )

            return (
                text_length
                >= cls.MIN_HTML_TEXT_CHARACTERS
                and (
                    len(detected_signals) >= 2
                    or text_length >= 12000
                )
            )

        return False

    @staticmethod
    def _identify_source(
        url: str,
    ) -> str:
        """
        Identifies the probable repository or publisher.
        """

        lowered_url = url.casefold()

        source_markers = (
            (
                "pmc.ncbi.nlm.nih.gov",
                "PubMed Central",
            ),
            (
                "ncbi.nlm.nih.gov",
                "PubMed Central",
            ),
            (
                "arxiv.org",
                "arXiv",
            ),
            (
                "openalex.org",
                "OpenAlex",
            ),
            (
                "crossref.org",
                "Crossref",
            ),
            (
                "doi.org",
                "DOI resolver",
            ),
            (
                "springer.com",
                "Springer",
            ),
            (
                "sciencedirect.com",
                "ScienceDirect",
            ),
            (
                "frontiersin.org",
                "Frontiers",
            ),
            (
                "plos.org",
                "PLOS",
            ),
            (
                "mdpi.com",
                "MDPI",
            ),
            (
                "wiley.com",
                "Wiley",
            ),
            (
                "tandfonline.com",
                "Taylor & Francis",
            ),
        )

        for marker, source_name in source_markers:
            if marker in lowered_url:
                return source_name

        return "Publisher or repository"

    @staticmethod
    def _normalize_doi(
        value: Any,
    ) -> str:
        """
        Normalizes a DOI to its canonical identifier.
        """

        doi = FullTextLoader._text(
            value
        )

        if not doi:
            return ""

        doi = re.sub(
            r"^https?://(?:dx\.)?doi\.org/",
            "",
            doi,
            flags=re.IGNORECASE,
        )

        doi = re.sub(
            r"^doi:\s*",
            "",
            doi,
            flags=re.IGNORECASE,
        )

        return doi.strip()

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:
        """
        Normalizes whitespace while preserving paragraphs.
        """

        if not text:
            return ""

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
    def _join_errors(
        errors: list[str],
    ) -> str:
        """
        Joins retrieval errors into one compact diagnostic message.
        """

        if not errors:
            return (
                "No openly accessible full text was found."
            )

        return " | ".join(
            errors
        )[:4000]

    @staticmethod
    def _text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _unique_strings(
        values: list[str],
    ) -> list[str]:
        result: list[str] = []

        for value in values:
            value = str(value).strip()

            if (
                value
                and value not in result
            ):
                result.append(value)

        return result