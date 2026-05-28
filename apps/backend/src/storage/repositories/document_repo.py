import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.profiles import CorpusDomain
from storage.models import Document, DocumentChunk


async def find_by_checksum(
    db: AsyncSession, checksum: str, user_id: str
) -> Document | None:
    return await db.scalar(
        select(Document).where(
            Document.checksum == checksum,
            Document.user_id == user_id,
        )
    )


async def list_documents_with_chunk_counts(
    db: AsyncSession, domain: CorpusDomain | None, user_id: str
):
    stmt = (
        select(
            Document.id,
            Document.filename,
            Document.title,
            Document.domain,
            Document.mime_type,
            Document.created_at,
            func.count(DocumentChunk.id).label("chunk_count"),
        )
        .outerjoin(DocumentChunk)
        .where(Document.user_id == user_id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc())
    )
    if domain:
        stmt = stmt.where(Document.domain == domain)
    return (await db.execute(stmt)).all()


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    return await db.get(Document, document_id)


async def list_chunk_ids(db: AsyncSession, document_id: uuid.UUID) -> list[str]:
    rows = await db.execute(
        select(DocumentChunk.id).where(DocumentChunk.document_id == document_id)
    )
    return [str(row) for row in rows.scalars().all()]
