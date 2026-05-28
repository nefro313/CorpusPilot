import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_user_id
from api.sse import SSE_HEADERS, SSE_MEDIA_TYPE, format_sse
from domain.profiles import CorpusDomain, list_domain_profiles
from schemas.api import (
    DocumentOut,
    DocumentUploadResponse,
    DomainProfileOut,
)
from services.documents import (
    index_document,
    read_upload_payload,
    stream_index_documents,
)
from services.retrieval import invalidate_retrieval_cache
from storage.database import get_db
from storage.repositories.document_repo import (
    get_document,
    list_chunk_ids,
    list_documents_with_chunk_counts,
)
from vectorstores import vector_store

router = APIRouter(prefix="/api/documents", tags=["documents"])
logger = logging.getLogger(__name__)


@router.get("/domains", response_model=list[DomainProfileOut])
async def list_domains() -> list[DomainProfileOut]:
    return [
        DomainProfileOut(
            value=profile.value,
            label=profile.label,
            description=profile.description,
            chunking_strategy=profile.chunking_strategy,
            retrieval_strategy=profile.retrieval_strategy,
        )
        for profile in list_domain_profiles()
    ]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    domain: CorpusDomain = Form(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> DocumentUploadResponse:
    payload = await read_upload_payload(file)
    result = await index_document(
        db=db,
        filename=file.filename or "untitled",
        payload=payload,
        domain=domain,
        user_id=user_id,
        mime_type=file.content_type,
    )
    if not result.document:
        raise HTTPException(status_code=400, detail=result.message)
    return result.document


@router.post("/upload/stream")
async def upload_documents_stream(
    files: list[UploadFile] = File(...),
    domain: CorpusDomain = Form(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> StreamingResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    return _sse_stream(stream_index_documents(db=db, files=files, domain=domain, user_id=user_id))


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    domain: CorpusDomain | None = None,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> list[DocumentOut]:
    rows = await list_documents_with_chunk_counts(db, domain, user_id)
    return [
        DocumentOut(
            id=row.id,
            filename=row.filename,
            title=row.title,
            domain=row.domain,
            mime_type=row.mime_type,
            created_at=row.created_at,
            chunk_count=row.chunk_count,
        )
        for row in rows
    ]


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> Response:
    document = await get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not your document")

    chunk_ids = await list_chunk_ids(db, document_id)
    domain = document.domain
    filename = document.filename

    try:
        await db.delete(document)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    if chunk_ids:
        try:
            await vector_store.delete_chunks(chunk_ids)
        except Exception as exc:
            logger.warning(
                "vector cleanup failed for document %s (%s): %s",
                document_id,
                filename,
                exc,
            )

    await invalidate_retrieval_cache(domain, user_id)
    logger.info(
        "deleted document %s (%s); removed %d chunks from corpus",
        document_id,
        filename,
        len(chunk_ids),
    )
    return Response(status_code=204)


def _sse_stream(
    source: AsyncGenerator[tuple[str, dict[str, Any]], None],
) -> StreamingResponse:
    async def event_generator():
        try:
            async for event_type, data in source:
                yield format_sse(event_type, data)
            yield format_sse("done", {})
        except Exception as exc:
            yield format_sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type=SSE_MEDIA_TYPE,
        headers=SSE_HEADERS,
    )
