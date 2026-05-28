from dataclasses import dataclass
from typing import Any

from domain.profiles import CorpusDomain
from services.ingestion.chunking import PreparedChunk, PreparedParent, chunk_units
from services.ingestion.parsing import (
    checksum_bytes,
    extract_text_units,
    infer_title,
)
from services.ingestion.tables import PreparedTableCell, extract_table_cells


@dataclass(frozen=True)
class PreparedDocument:
    title: str
    mime_type: str
    checksum: str
    content: str
    chunks: list[PreparedChunk]
    parents: list[PreparedParent]
    table_cells: list[PreparedTableCell]


def build_prepared_document(
    filename: str,
    payload: bytes,
    domain: CorpusDomain,
    resolved_mime: str,
    units: list[dict[str, Any]],
) -> PreparedDocument:
    parents, chunks, content = chunk_units(units, domain)
    table_cells = (
        extract_table_cells(units) if domain == CorpusDomain.FINANCIAL_DOCUMENT else []
    )
    return PreparedDocument(
        title=infer_title(filename),
        mime_type=resolved_mime,
        checksum=checksum_bytes(payload),
        content=content,
        chunks=chunks,
        parents=parents,
        table_cells=table_cells,
    )


async def prepare_document(
    filename: str,
    payload: bytes,
    domain: CorpusDomain,
    mime_type: str | None,
) -> PreparedDocument:
    resolved_mime, units = await extract_text_units(filename, payload, mime_type)
    return build_prepared_document(filename, payload, domain, resolved_mime, units)
