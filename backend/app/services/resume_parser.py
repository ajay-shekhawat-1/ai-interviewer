from io import BytesIO

import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class ResumeParsingError(Exception):
    """Raised when a resume cannot be parsed successfully."""


def normalize_text(text: str) -> str:
    """
    Normalize extracted document text.

    Removes unnecessary whitespace while preserving
    paragraph-level readability.
    """

    lines = []

    for line in text.splitlines():
        cleaned = " ".join(line.split())

        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines).strip()


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from a PDF document.
    """

    try:
        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf",
        )

        try:
            pages = []

            for page in document:
                pages.append(page.get_text())

            return normalize_text("\n".join(pages))

        finally:
            document.close()

    except Exception as exc:
        raise ResumeParsingError(
            "Unable to extract text from PDF."
        ) from exc


def extract_docx_text(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX document.
    """

    try:
        document = Document(BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return normalize_text("\n".join(paragraphs))

    except Exception as exc:
        raise ResumeParsingError(
            "Unable to extract text from DOCX."
        ) from exc


def parse_resume(
    filename: str,
    file_bytes: bytes,
) -> str:
    """
    Extract and normalize text from a supported resume.

    Supported formats:
    - PDF
    - DOCX
    """

    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)

    elif filename_lower.endswith(".docx"):
        text = extract_docx_text(file_bytes)

    else:
        raise ResumeParsingError(
            "Unsupported resume format. Only PDF and DOCX are supported."
        )

    if not text:
        raise ResumeParsingError(
            "No readable text was found in the resume."
        )

    return text