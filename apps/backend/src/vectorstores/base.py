from dataclasses import dataclass

from domain.profiles import CorpusDomain


@dataclass(slots=True)
class VectorChunkRecord:
    chunk_id: str
    document_id: str
    document_filename: str
    domain: CorpusDomain
    chunk_index: int
    page_number: int | None
    section_title: str | None
    content: str
    embedding: list[float]
    user_id: str = ""


@dataclass(slots=True)
class VectorSearchResult:
    chunk_id: str
    document_id: str
    document_filename: str
    domain: CorpusDomain
    content: str
    chunk_index: int
    page_number: int | None
    section_title: str | None
    semantic_score: float | None = None
