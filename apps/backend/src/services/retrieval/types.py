from dataclasses import dataclass

from domain.profiles import CorpusDomain


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_filename: str
    domain: CorpusDomain
    content: str
    chunk_index: int
    page_number: int | None
    section_title: str | None
    semantic_score: float | None = None
    lexical_score: float | None = None
    fusion_score: float | None = None
    rerank_score: float | None = None
    citation_id: str | None = None


@dataclass(slots=True)
class HybridRetrievalResult:
    semantic_hits: list[RetrievedChunk]
    lexical_hits: list[RetrievedChunk]
    fused_hits: list[RetrievedChunk]
