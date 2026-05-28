"""LlamaIndex view of the existing Zilliz Milvus collection.

Reuses the same `document_chunks` collection populated by the pymilvus-based
`vectorstores.milvus.MilvusVectorStore`. Field mapping is configured so that
LlamaIndex reads:

    chunk_id  -> node.id_
    content   -> node.text
    embedding -> node.embedding
    {document_id, document_filename, domain, chunk_index,
     page_number, section_title} -> node.metadata

This keeps a single canonical row per chunk; both the pymilvus client and the
LlamaIndex client point at it.
"""

from __future__ import annotations

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import IndexManagement, MilvusVectorStore

from core.config import get_settings
from vectorstores.base import VectorChunkRecord

settings = get_settings()

_LLAMAINDEX_OUTPUT_FIELDS = [
    "document_id",
    "document_filename",
    "domain",
    "chunk_index",
    "page_number",
    "section_title",
    "user_id",
]

_vector_store: MilvusVectorStore | None = None
_vector_index: VectorStoreIndex | None = None
_embed_model: OpenAIEmbedding | None = None


def _get_embed_model() -> OpenAIEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = OpenAIEmbedding(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            dimensions=settings.embedding_dimensions,
        )
    return _embed_model


def get_llamaindex_vector_store() -> MilvusVectorStore:
    """Module-level singleton pointing at the existing Zilliz collection."""
    global _vector_store
    if _vector_store is None:
        endpoint = settings.zillizcloud_endpoint.strip()
        api_key = settings.zillizcloud_api_key.strip()
        if not endpoint or not api_key:
            raise RuntimeError(
                "Zilliz Cloud is not configured. Set ZILLIZCLOUD_ENDPOINT and ZILLIZCLOUD_API_KEY."
            )
        _vector_store = MilvusVectorStore(
            uri=endpoint,
            token=api_key,
            collection_name=settings.milvus_collection_name,
            dim=settings.embedding_dimensions,
            embedding_field=settings.milvus_vector_field_name,
            doc_id_field="chunk_id",
            text_key="content",
            output_fields=_LLAMAINDEX_OUTPUT_FIELDS,
            similarity_metric=settings.milvus_metric_type,
            overwrite=False,
            index_management=IndexManagement.NO_VALIDATION,
        )
    return _vector_store


def get_llamaindex_index() -> VectorStoreIndex:
    """`VectorStoreIndex` bound to the shared store + OpenAI embedder."""
    global _vector_index
    if _vector_index is None:
        _vector_index = VectorStoreIndex.from_vector_store(
            vector_store=get_llamaindex_vector_store(),
            embed_model=_get_embed_model(),
        )
    return _vector_index


def chunk_to_text_node(chunk: VectorChunkRecord) -> TextNode:
    """Convert a `VectorChunkRecord` into a LlamaIndex `TextNode`.

    Used during ingestion so newly indexed chunks have a canonical
    LlamaIndex representation; the metadata fields mirror the schema columns
    that the retriever surfaces back out as `node.metadata`.
    """
    return TextNode(
        id_=chunk.chunk_id,
        text=chunk.content,
        embedding=chunk.embedding,
        metadata={
            "document_id": chunk.document_id,
            "document_filename": chunk.document_filename,
            "domain": chunk.domain.value,
            "user_id": chunk.user_id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number if chunk.page_number is not None else -1,
            "section_title": chunk.section_title or "",
        },
    )


def chunks_to_text_nodes(chunks: list[VectorChunkRecord]) -> list[TextNode]:
    return [chunk_to_text_node(chunk) for chunk in chunks]
