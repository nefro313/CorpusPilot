"""Document parsing.

LlamaParse handles the cloud parse for PDF / DOCX / PPTX / XLSX / HTML
uploads. `pypdf` powers two local paths: `extract_preview_text` for the
classifier's first-page peek, and `_extract_pdf_full_text` as a fallback
when LlamaParse returns nothing (missing key, image-only PDF, transport
error).
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
import re
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any

from llama_cloud_services import LlamaParse
from pypdf import PdfReader

from core.config import get_settings

logger = logging.getLogger(__name__)

# Extensions LlamaParse genuinely improves on. Lightweight plaintext formats
# (md, txt, csv) stay local — paying for a cloud parse on `.md` is wasteful.
_LLAMAPARSE_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm"}

_MIME_BY_EXTENSION: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".html": "text/html",
    ".htm": "text/html",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".csv": "text/csv",
}

_SUPPORTED_MIME_TYPES = set(_MIME_BY_EXTENSION.values())

_parser: LlamaParse | None = None


def _get_parser() -> LlamaParse:
    global _parser
    if _parser is None:
        settings = get_settings()
        _parser = LlamaParse(
            api_key=settings.llama_cloud_api_key,
            result_type=settings.llamaparse_result_type,
            num_workers=settings.llamaparse_num_workers,
            language=settings.llamaparse_language,
            verbose=False,
        )
    return _parser


def resolve_mime(filename: str, mime_type: str | None) -> str | None:
    if mime_type and mime_type in _SUPPORTED_MIME_TYPES:
        return mime_type
    suffix = Path(filename).suffix.lower()
    return _MIME_BY_EXTENSION.get(suffix)


def checksum_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def infer_title(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").replace("-", " ").strip() or filename


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clip_preview_text(text: str, max_chars: int = 3500) -> str:
    if len(text) <= max_chars:
        return text
    trimmed = text[:max_chars].rsplit(" ", 1)[0].strip()
    return trimmed or text[:max_chars].strip()


def _extract_pdf_preview_text(payload: bytes) -> str:
    # pypdf raises on malformed / truncated / encrypted PDFs. Treat any
    # such failure as "no preview text available" so callers can fall back
    # gracefully instead of crashing.
    try:
        reader = PdfReader(BytesIO(payload))
    except Exception:
        return ""
    if not reader.pages:
        return ""
    try:
        first_page_text = reader.pages[0].extract_text() or ""
    except Exception:
        return ""
    return normalize_text(first_page_text)


def extract_preview_text(filename: str, payload: bytes, mime_type: str | None) -> tuple[str, str]:
    """Cheap local-only preview.

    PDFs use pypdf; everything else falls back to a UTF-8 decode (adequate
    for .txt / .md / .html, noisy for binary office formats). The upload
    pipeline does not depend on this — it's exposed for any caller that
    wants a fast no-network peek at a file.
    """
    lower_name = filename.lower()
    if lower_name.endswith(".pdf") or mime_type == "application/pdf":
        return "application/pdf", _clip_preview_text(_extract_pdf_preview_text(payload))

    resolved_mime = resolve_mime(filename, mime_type) or "text/plain"
    decoded = payload.decode("utf-8", errors="ignore")
    return resolved_mime, _clip_preview_text(normalize_text(decoded))


def _extract_pdf_full_text(payload: bytes) -> list[dict[str, Any]]:
    """Full-document pypdf fallback for PDFs.

    Walks every page, extracting text. Returns one unit per page that has
    extractable text. Encrypted, malformed, or image-only PDFs return an
    empty list so the caller can surface a precise rejection message.
    """
    try:
        reader = PdfReader(BytesIO(payload))
    except Exception as exc:
        logger.warning("pypdf failed to open PDF: %s", exc)
        return []
    units: list[dict[str, Any]] = []
    for idx, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            continue
        text = normalize_text(text)
        if text:
            units.append({"text": text, "page_number": idx + 1})
    return units


def _units_have_text(units: list[dict[str, Any]]) -> bool:
    return any(unit.get("text") for unit in units)


async def _llamaparse_parse(filename: str, payload: bytes) -> list[dict[str, Any]]:
    suffix = Path(filename).suffix or ""
    parser = _get_parser()

    # LlamaParse's high-level helpers expect a path on disk. Writing the
    # upload to a temp file is simpler and safer than streaming bytes through
    # the lower-level job API, and the file lives only for the duration of
    # the parse call.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        documents = await parser.aload_data(file_path=tmp_path)
    finally:
        with contextlib.suppress(OSError):
            Path(tmp_path).unlink(missing_ok=True)

    units: list[dict[str, Any]] = []
    for idx, doc in enumerate(documents):
        text = normalize_text(getattr(doc, "text", "") or "")
        if not text:
            continue
        metadata = getattr(doc, "metadata", {}) or {}
        raw_page = metadata.get("page_label") or metadata.get("page_number")
        try:
            page_no = int(raw_page) if raw_page is not None else idx + 1
        except (TypeError, ValueError):
            page_no = idx + 1
        units.append({"text": text, "page_number": page_no})

    return units or [{"text": "", "page_number": 1}]


async def extract_text_units(
    filename: str, payload: bytes, mime_type: str | None
) -> tuple[str, list[dict[str, Any]]]:
    """Full document parse.

    Cloud-backed for the formats LlamaParse handles best; local UTF-8 decode
    for plaintext-ish formats where the network round-trip would be wasteful.
    PDFs fall back to pypdf when LlamaParse returns nothing usable
    (missing API key, image-only PDF, parse failure), so a working text-PDF
    still indexes without the cloud service.
    """
    resolved_mime = resolve_mime(filename, mime_type)
    suffix = Path(filename).suffix.lower()

    if suffix in _LLAMAPARSE_EXTENSIONS:
        settings = get_settings()
        units: list[dict[str, Any]] = []
        if settings.llama_cloud_api_key:
            try:
                units = await _llamaparse_parse(filename, payload)
            except Exception as exc:
                logger.warning("LlamaParse failed for %s: %s", filename, exc)
                units = []
        else:
            logger.info(
                "LLAMA_CLOUD_API_KEY not set; skipping LlamaParse for %s.", filename
            )

        if not _units_have_text(units) and suffix == ".pdf":
            logger.info("Falling back to pypdf for %s.", filename)
            units = _extract_pdf_full_text(payload)

        return resolved_mime or "application/octet-stream", units

    decoded = payload.decode("utf-8", errors="ignore")
    return resolved_mime or "text/plain", [{"text": normalize_text(decoded), "page_number": 1}]
