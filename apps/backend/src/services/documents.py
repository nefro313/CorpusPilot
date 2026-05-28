"""Document ingestion: upload → parse → chunk → embed → persist."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.metrics import DOCUMENT_INGESTIONS_TOTAL
from domain.profiles import DOMAIN_PROFILES, CorpusDomain, get_domain_profile
from schemas.api import (
    BatchUploadSummary,
    DocumentUploadResponse,
    UploadFileResult,
)
from services.embeddings import embed_documents
from services.ingestion import (
    ClassificationResult,
    PreparedDocument,
    build_prepared_document,
    classify_first_page,
    extract_text_units,
)
from services.retrieval import invalidate_retrieval_cache
from storage.models import Document, DocumentChunk, DocumentTableRow
from storage.repositories.document_repo import find_by_checksum
from vectorstores import vector_store
from vectorstores.base import VectorChunkRecord
from vectorstores.llamaindex_milvus import (
    chunks_to_text_nodes,
    get_llamaindex_vector_store,
)

settings = get_settings()
logger = logging.getLogger(__name__)


STAGE_PROGRESS: dict[str, int] = {
    "queued": 0,
    "validating": 15,
    "parsing": 30,
    "chunking": 60,
    "embedding": 82,
    "storing": 95,
    "done": 100,
    "rejected": 100,
}

STAGE_LABELS: dict[str, str] = {
    "queued": "Queued",
    "validating": "Checking domain",
    "parsing": "Parsing document",
    "chunking": "Chunking content",
    "embedding": "Embedding chunks",
    "storing": "Writing to corpus",
    "done": "Indexed",
    "rejected": "Rejected",
}


@dataclass
class _Outcome:
    result: UploadFileResult


def document_response(document: Document, profile) -> DocumentUploadResponse:
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        title=document.title,
        domain=document.domain,
        mime_type=document.mime_type,
        created_at=document.created_at,
        chunk_count=document.total_chunks,
        chunking_strategy=profile.chunking_strategy,
        retrieval_strategy=profile.retrieval_strategy,
    )


_SUPPORTED_DOMAINS_HUMAN = ", ".join(profile.label for profile in DOMAIN_PROFILES.values())


def _domain_label(domain: CorpusDomain) -> str:
    return DOMAIN_PROFILES[domain].label


def _classification_rejection(
    *, filename: str, selected_domain: CorpusDomain, classification: ClassificationResult
) -> UploadFileResult:
    if classification.verdict == "mismatch" and classification.predicted_domain is not None:
        suggested = classification.predicted_domain
        message = (
            f"This looks like a {_domain_label(suggested)} document, not a "
            f"{_domain_label(selected_domain)}. Please re-upload after switching the domain."
        )
        return UploadFileResult(
            filename=filename,
            status="rejected",
            message=message,
            suggested_domain=suggested,
            rejection_reason=classification.reason,
        )
    message = (
        "This file does not match any of the supported domains "
        f"({_SUPPORTED_DOMAINS_HUMAN}). Please upload a document from one of these categories."
    )
    return UploadFileResult(
        filename=filename,
        status="rejected",
        message=message,
        suggested_domain=None,
        rejection_reason=classification.reason,
    )


async def read_upload_payload(file: UploadFile) -> bytes:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(payload) > settings.upload_max_bytes:
        raise HTTPException(status_code=413, detail="File is too large")
    return payload


def _register_llamaindex_nodes(records: list[VectorChunkRecord]) -> None:
    if not records:
        return
    nodes = chunks_to_text_nodes(records)
    try:
        get_llamaindex_vector_store().add(nodes)
    except Exception:
        logger.debug("LlamaIndex dual-write skipped; pymilvus path is authoritative.")


async def _persist_document(
    *,
    db: AsyncSession,
    filename: str,
    domain: CorpusDomain,
    user_id: str,
    prepared: PreparedDocument,
    embeddings: list[list[float]],
) -> Document:
    profile = get_domain_profile(domain)
    chunk_rows: list[DocumentChunk] = []
    document = Document(
        id=uuid.uuid4(),
        user_id=user_id,
        filename=filename,
        title=prepared.title,
        domain=domain,
        mime_type=prepared.mime_type,
        checksum=prepared.checksum,
        content=prepared.content,
        metadata_json={
            "chunking_strategy": profile.chunking_strategy,
            "retrieval_strategy": profile.retrieval_strategy,
        },
        total_chunks=len(prepared.chunks),
    )
    db.add(document)

    parent_id_by_index: dict[int, uuid.UUID] = {}
    for parent in prepared.parents:
        parent_uuid = uuid.uuid4()
        parent_id_by_index[parent.parent_index] = parent_uuid
        db.add(
            DocumentChunk(
                id=parent_uuid,
                document_id=document.id,
                parent_chunk_id=None,
                chunk_index=-(parent.parent_index + 1),
                page_number=parent.page_number,
                section_title=parent.section_title,
                token_count=parent.token_count,
                content=parent.content,
                metadata_json=parent.metadata_json,
            )
        )

    for chunk in prepared.chunks:
        parent_chunk_id = (
            parent_id_by_index.get(chunk.parent_index)
            if chunk.parent_index is not None
            else None
        )
        chunk_row = DocumentChunk(
            id=uuid.uuid4(),
            document_id=document.id,
            parent_chunk_id=parent_chunk_id,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            token_count=chunk.token_count,
            content=chunk.content,
            metadata_json=chunk.metadata_json,
        )
        chunk_rows.append(chunk_row)
        db.add(chunk_row)

    for cell in prepared.table_cells:
        db.add(
            DocumentTableRow(
                id=uuid.uuid4(),
                document_id=document.id,
                table_index=cell.table_index,
                row_index=cell.row_index,
                column_name=cell.column_name,
                cell_value=cell.cell_value,
                page_number=cell.page_number,
                section_title=cell.section_title,
            )
        )

    inserted_chunk_ids: list[str] = []
    try:
        await db.flush()
        vector_records = [
            VectorChunkRecord(
                chunk_id=str(chunk_row.id),
                document_id=str(document.id),
                document_filename=filename,
                domain=domain,
                user_id=user_id,
                chunk_index=chunk_row.chunk_index,
                page_number=chunk_row.page_number,
                section_title=chunk_row.section_title,
                content=chunk_row.content,
                embedding=embedding,
            )
            for chunk_row, embedding in zip(chunk_rows, embeddings, strict=True)
        ]
        inserted_chunk_ids = [record.chunk_id for record in vector_records]
        await vector_store.upsert_chunks(vector_records)
        _register_llamaindex_nodes(vector_records)
        await db.commit()
    except Exception:
        await db.rollback()
        if inserted_chunk_ids:
            await vector_store.delete_chunks(inserted_chunk_ids)
        raise

    await db.refresh(document)
    return document


async def index_document(
    *,
    db: AsyncSession,
    filename: str,
    payload: bytes,
    domain: CorpusDomain,
    user_id: str,
    mime_type: str | None,
) -> UploadFileResult:
    result, stage = await _index_document_inner(
        db=db, filename=filename, payload=payload, domain=domain, user_id=user_id, mime_type=mime_type
    )
    DOCUMENT_INGESTIONS_TOTAL.labels(domain=domain.value, status=result.status, stage=stage).inc()
    return result


async def _index_document_inner(
    *,
    db: AsyncSession,
    filename: str,
    payload: bytes,
    domain: CorpusDomain,
    user_id: str,
    mime_type: str | None,
) -> tuple[UploadFileResult, str]:
    classification = await classify_first_page(
        filename=filename, payload=payload, mime_type=mime_type, selected_domain=domain
    )
    if classification.should_reject:
        return _classification_rejection(
            filename=filename, selected_domain=domain, classification=classification
        ), "classify"

    resolved_mime, units = await extract_text_units(filename, payload, mime_type)
    prepared = build_prepared_document(filename, payload, domain, resolved_mime, units)
    if not prepared.content or not prepared.chunks:
        return UploadFileResult(
            filename=filename,
            status="rejected",
            message=(
                "Could not extract any text from this file. "
                "If it's a scanned/image-only PDF, run it through OCR first; "
                "otherwise check that LLAMA_CLOUD_API_KEY is set and valid."
            ),
        ), "parse"

    existing = await find_by_checksum(db, prepared.checksum, user_id)
    if existing:
        profile = get_domain_profile(existing.domain)
        return UploadFileResult(
            filename=filename,
            status="duplicate",
            message=f"Already indexed as {profile.label.lower()}. Reused the existing corpus entry.",
            document=document_response(existing, profile),
        ), "dedup"

    embeddings = await embed_documents([chunk.content for chunk in prepared.chunks])
    document = await _persist_document(
        db=db,
        filename=filename,
        domain=domain,
        user_id=user_id,
        prepared=prepared,
        embeddings=embeddings,
    )
    await invalidate_retrieval_cache(domain, user_id)
    profile = get_domain_profile(domain)
    return UploadFileResult(
        filename=filename,
        status="indexed",
        message=f"Indexed {prepared.title} with {len(prepared.chunks)} chunks.",
        document=document_response(document, profile),
    ), "store"


def _progress_payload(
    file_index: int,
    total_files: int,
    filename: str,
    stage: str,
    detail: str | None = None,
) -> dict[str, Any]:
    file_progress = STAGE_PROGRESS[stage]
    overall_progress = round(((file_index + (file_progress / 100)) / total_files) * 100)
    payload: dict[str, Any] = {
        "file_index": file_index,
        "total_files": total_files,
        "file_name": filename,
        "stage": stage,
        "stage_label": STAGE_LABELS[stage],
        "file_progress": file_progress,
        "overall_progress": overall_progress,
    }
    if detail:
        payload["detail"] = detail
    return payload


async def _index_with_progress(
    *,
    db: AsyncSession,
    file: UploadFile,
    file_index: int,
    total_files: int,
    domain: CorpusDomain,
    user_id: str,
) -> AsyncGenerator[tuple[str, Any], None]:
    filename = file.filename or f"document-{file_index + 1}"
    result: UploadFileResult
    _stage = "pipeline"
    try:
        yield ("file_progress", _progress_payload(file_index, total_files, filename, "queued"))
        payload = await read_upload_payload(file)

        yield (
            "file_progress",
            _progress_payload(file_index, total_files, filename, "validating"),
        )
        classification = await classify_first_page(
            filename=filename,
            payload=payload,
            mime_type=file.content_type,
            selected_domain=domain,
        )
        if classification.should_reject:
            _stage = "classify"
            result = _classification_rejection(
                filename=filename, selected_domain=domain, classification=classification
            )
        else:
            yield (
                "file_progress",
                _progress_payload(file_index, total_files, filename, "parsing"),
            )
            resolved_mime, units = await extract_text_units(
                filename, payload, file.content_type
            )
            yield (
                "file_progress",
                _progress_payload(file_index, total_files, filename, "chunking"),
            )
            prepared = build_prepared_document(filename, payload, domain, resolved_mime, units)
            if not prepared.content or not prepared.chunks:
                _stage = "parse"
                result = UploadFileResult(
                    filename=filename,
                    status="rejected",
                    message=(
                        "Could not extract any text from this file. "
                        "If it's a scanned/image-only PDF, run it through OCR first; "
                        "otherwise check that LLAMA_CLOUD_API_KEY is set and valid."
                    ),
                )
            else:
                existing = await find_by_checksum(db, prepared.checksum, user_id)
                if existing:
                    _stage = "dedup"
                    profile = get_domain_profile(existing.domain)
                    result = UploadFileResult(
                        filename=filename,
                        status="duplicate",
                        message=(
                            f"Already indexed as {profile.label.lower()}. "
                            "Reused the existing corpus entry."
                        ),
                        document=document_response(existing, profile),
                    )
                else:
                    yield (
                        "file_progress",
                        _progress_payload(
                            file_index,
                            total_files,
                            filename,
                            "embedding",
                            f"{len(prepared.chunks)} chunks",
                        ),
                    )
                    embeddings = await embed_documents(
                        [chunk.content for chunk in prepared.chunks]
                    )
                    yield (
                        "file_progress",
                        _progress_payload(file_index, total_files, filename, "storing"),
                    )
                    document = await _persist_document(
                        db=db,
                        filename=filename,
                        domain=domain,
                        user_id=user_id,
                        prepared=prepared,
                        embeddings=embeddings,
                    )
                    await invalidate_retrieval_cache(domain, user_id)
                    _stage = "store"
                    profile = get_domain_profile(domain)
                    result = UploadFileResult(
                        filename=filename,
                        status="indexed",
                        message=(
                            f"Indexed {prepared.title} with {len(prepared.chunks)} chunks."
                        ),
                        document=document_response(document, profile),
                    )
    except HTTPException as exc:
        await db.rollback()
        result = UploadFileResult(filename=filename, status="rejected", message=str(exc.detail))
        yield (
            "file_progress",
            _progress_payload(file_index, total_files, filename, "rejected", result.message),
        )
    except Exception as exc:
        await db.rollback()
        result = UploadFileResult(
            filename=filename, status="rejected", message=f"Indexing failed: {exc}"
        )
        yield (
            "file_progress",
            _progress_payload(file_index, total_files, filename, "rejected", result.message),
        )
    else:
        sse_stage = "done" if result.status in {"indexed", "duplicate"} else "rejected"
        yield (
            "file_progress",
            _progress_payload(file_index, total_files, filename, sse_stage, result.message),
        )
    finally:
        await file.close()

    DOCUMENT_INGESTIONS_TOTAL.labels(
        domain=domain.value, status=result.status, stage=_stage
    ).inc()
    yield ("__result__", _Outcome(result=result))


async def stream_index_documents(
    *,
    db: AsyncSession,
    files: list[UploadFile],
    domain: CorpusDomain,
    user_id: str,
) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
    total_files = len(files)
    results: list[UploadFileResult] = []
    yield (
        "batch_started",
        {"total_files": total_files, "selected_domain": domain.value},
    )

    for file_index, file in enumerate(files):
        async for event_type, data in _index_with_progress(
            db=db, file=file, file_index=file_index, total_files=total_files, domain=domain, user_id=user_id
        ):
            if event_type == "__result__":
                results.append(data.result)
                yield ("file_result", data.result.model_dump(mode="json"))
            else:
                yield (event_type, data)

    summary = BatchUploadSummary(
        total_files=total_files,
        indexed_count=sum(1 for item in results if item.status == "indexed"),
        duplicate_count=sum(1 for item in results if item.status == "duplicate"),
        rejected_count=sum(1 for item in results if item.status == "rejected"),
        items=results,
    )
    yield ("batch_complete", summary.model_dump(mode="json"))
