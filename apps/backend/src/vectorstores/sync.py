from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services.embeddings import embed_documents
from storage.models import Document, DocumentChunk
from vectorstores import vector_store
from vectorstores.base import VectorChunkRecord


async def backfill_missing_vectors(session_factory: async_sessionmaker[AsyncSession]) -> None:
    await vector_store.ensure_ready()

    async with session_factory() as session:
        # Parents (rows that have children pointing at them) are Postgres-only;
        # exclude them from the embedding backfill.
        parent_ids_subq = (
            select(DocumentChunk.parent_chunk_id)
            .where(DocumentChunk.parent_chunk_id.is_not(None))
            .distinct()
        )
        leaf_filter = DocumentChunk.id.not_in(parent_ids_subq)
        total_chunks = int(
            await session.scalar(
                select(func.count(DocumentChunk.id)).where(leaf_filter)
            )
            or 0
        )
        if total_chunks == 0:
            return

        indexed_chunks = await vector_store.count_chunks()
        if indexed_chunks >= total_chunks:
            return

        rows = (
            await session.execute(
                select(
                    DocumentChunk.id,
                    DocumentChunk.content,
                    DocumentChunk.chunk_index,
                    DocumentChunk.page_number,
                    DocumentChunk.section_title,
                    Document.id.label("document_id"),
                    Document.filename,
                    Document.domain,
                )
                .join(Document, Document.id == DocumentChunk.document_id)
                .where(leaf_filter)
                .order_by(Document.created_at.asc(), DocumentChunk.chunk_index.asc())
            )
        ).all()

    batch_size = 32
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        ids = [str(row.id) for row in batch]
        existing_ids = await vector_store.get_existing_chunk_ids(ids)
        missing = [row for row in batch if str(row.id) not in existing_ids]
        if not missing:
            continue

        embeddings = await embed_documents([row.content for row in missing])
        records = [
            VectorChunkRecord(
                chunk_id=str(row.id),
                document_id=str(row.document_id),
                document_filename=row.filename,
                domain=row.domain,
                chunk_index=row.chunk_index,
                page_number=row.page_number,
                section_title=row.section_title,
                content=row.content,
                embedding=embedding,
            )
            for row, embedding in zip(missing, embeddings, strict=True)
        ]
        await vector_store.upsert_chunks(records)
