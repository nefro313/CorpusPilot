from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from sqlalchemy.ext.asyncio import AsyncSession

from domain.profiles import CorpusDomain
from services.retrieval.types import RetrievedChunk
from vectorstores.llamaindex_milvus import get_llamaindex_index


def _node_to_chunk(scored: NodeWithScore) -> RetrievedChunk | None:
    node = scored.node
    metadata = getattr(node, "metadata", None) or {}
    chunk_id = node.node_id or metadata.get("chunk_id")
    domain_value = metadata.get("domain")
    if not chunk_id or not domain_value:
        return None
    page_number_raw = metadata.get("page_number")
    page_number: int | None
    if page_number_raw is None or page_number_raw == -1 or page_number_raw == "":
        page_number = None
    else:
        page_number = int(page_number_raw)
    section_title = metadata.get("section_title") or None
    semantic_score = round(float(scored.score), 6) if scored.score is not None else None
    return RetrievedChunk(
        chunk_id=str(chunk_id),
        document_id=str(metadata.get("document_id", "")),
        document_filename=str(metadata.get("document_filename", "")),
        domain=CorpusDomain(str(domain_value)),
        content=node.get_content() if hasattr(node, "get_content") else getattr(node, "text", ""),
        chunk_index=int(metadata.get("chunk_index", 0)),
        page_number=page_number,
        section_title=section_title,
        semantic_score=semantic_score,
    )


async def semantic_search(
    db: AsyncSession,
    query: str,
    domain: CorpusDomain | None,
    top_k: int,
    user_id: str = "",
) -> list[RetrievedChunk]:
    index = get_llamaindex_index()
    filter_list: list[ExactMatchFilter] = []
    if user_id:
        filter_list.append(ExactMatchFilter(key="user_id", value=user_id))
    if domain:
        filter_list.append(ExactMatchFilter(key="domain", value=domain.value))
    filters = MetadataFilters(filters=filter_list) if filter_list else None
    retriever = index.as_retriever(similarity_top_k=top_k, filters=filters)
    scored_nodes = await retriever.aretrieve(query)
    hits: list[RetrievedChunk] = []
    for scored in scored_nodes:
        chunk = _node_to_chunk(scored)
        if chunk is not None:
            hits.append(chunk)
    return hits
