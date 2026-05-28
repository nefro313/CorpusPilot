from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document as LCDocument
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.profiles import CorpusDomain
from services.retrieval.cache import get_cached_retriever, set_cached_retriever
from services.retrieval.types import RetrievedChunk
from storage.models import Document, DocumentChunk


async def _load_corpus_documents(
    db: AsyncSession, domain: CorpusDomain | None, user_id: str
) -> list[LCDocument]:
    # Exclude parent rows: any chunk that has children (i.e. its id appears
    # as some other chunk's parent_chunk_id) is a parent and must not appear
    # in BM25 — only the focused child chunks are searchable.
    parent_ids_subq = (
        select(DocumentChunk.parent_chunk_id)
        .where(DocumentChunk.parent_chunk_id.is_not(None))
        .distinct()
    )
    stmt = (
        select(
            DocumentChunk.id,
            Document.id.label("document_id"),
            Document.filename,
            Document.domain,
            DocumentChunk.content,
            DocumentChunk.chunk_index,
            DocumentChunk.page_number,
            DocumentChunk.section_title,
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.id.not_in(parent_ids_subq))
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc(), DocumentChunk.chunk_index.asc())
    )
    if domain:
        stmt = stmt.where(Document.domain == domain)
    rows = (await db.execute(stmt)).all()
    return [
        LCDocument(
            page_content=row.content,
            metadata={
                "chunk_id": str(row.id),
                "document_id": str(row.document_id),
                "filename": row.filename,
                "domain": row.domain.value,
                "chunk_index": row.chunk_index,
                "page_number": row.page_number,
                "section_title": row.section_title,
            },
        )
        for row in rows
    ]


async def _get_or_build_bm25(
    db: AsyncSession, domain: CorpusDomain | None, k: int, user_id: str = ""
) -> BM25Retriever:
    cached = await get_cached_retriever(domain, user_id)
    if cached is not None:
        cached.k = k
        return cached

    docs = await _load_corpus_documents(db, domain, user_id)
    retriever = BM25Retriever.from_documents(
        docs or [LCDocument(page_content="", metadata={})], k=k
    )
    await set_cached_retriever(domain, retriever, user_id)
    return retriever


async def lexical_search(
    db: AsyncSession, query: str, domain: CorpusDomain | None, top_k: int, user_id: str = ""
) -> list[RetrievedChunk]:
    retriever = await _get_or_build_bm25(db, domain, top_k, user_id)
    docs = retriever.invoke(query)
    hits: list[RetrievedChunk] = []
    for rank, doc in enumerate(docs):
        metadata = doc.metadata
        chunk_id = metadata.get("chunk_id")
        if not chunk_id:
            continue
        hits.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                document_id=metadata["document_id"],
                document_filename=metadata["filename"],
                domain=CorpusDomain(metadata["domain"]),
                content=doc.page_content,
                chunk_index=int(metadata["chunk_index"]),
                page_number=metadata.get("page_number"),
                section_title=metadata.get("section_title"),
                lexical_score=round(1.0 / (rank + 1), 6),
            )
        )
    return hits
