import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from domain.profiles import CorpusDomain


class DomainProfileOut(BaseModel):
    value: CorpusDomain
    label: str
    description: str
    chunking_strategy: str
    retrieval_strategy: str


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    title: str
    domain: CorpusDomain
    mime_type: str
    created_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class DocumentUploadResponse(DocumentOut):
    chunking_strategy: str
    retrieval_strategy: str


class UploadFileResult(BaseModel):
    filename: str
    status: str
    message: str
    document: DocumentUploadResponse | None = None
    suggested_domain: CorpusDomain | None = None
    rejection_reason: str | None = None


class BatchUploadSummary(BaseModel):
    total_files: int
    indexed_count: int
    duplicate_count: int
    rejected_count: int
    items: list[UploadFileResult]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    domain: CorpusDomain | None = None
    top_k: int | None = Field(default=None, ge=1, le=10)
    session_id: str | None = None


class SourceChunk(BaseModel):
    citation_id: str
    content: str
    chunk_index: int
    document_id: str
    document_filename: str
    domain: CorpusDomain
    page_number: int | None = None
    section_title: str | None = None
    semantic_score: float | None = None
    lexical_score: float | None = None
    fusion_score: float | None = None
    rerank_score: float | None = None


class AnswerTelemetry(BaseModel):
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    semantic_candidates: int
    lexical_candidates: int
    fused_candidates: int
    reranked_candidates: int
    citation_valid: bool


class ChatResponse(BaseModel):
    answer: str
    domain: CorpusDomain | None = None
    grounded: bool
    citations: list[str]
    sources: list[SourceChunk]
    follow_up_questions: list[str] = Field(default_factory=list)
    telemetry: AnswerTelemetry
    session_id: str


class ObservabilitySummary(BaseModel):
    total_requests: int
    grounded_rate: float
    citation_valid_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    average_cost_usd: float
    latest_updated_at: datetime | None = None


class DomainMetricOut(BaseModel):
    domain: CorpusDomain
    requests: int
    p50_latency_ms: float
    p95_latency_ms: float
    average_cost_usd: float
    grounded_rate: float


class ObservabilityResponse(BaseModel):
    summary: ObservabilitySummary
    by_domain: list[DomainMetricOut]


class FeedbackRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    answer: str = Field(min_length=1, max_length=20000)
    rating: int = Field(ge=-1, le=1)
    session_id: str | None = Field(default=None, max_length=64)
    domain: CorpusDomain | None = None
    comment: str | None = Field(default=None, max_length=2000)
    citations: list[str] = Field(default_factory=list)


class FeedbackAck(BaseModel):
    id: uuid.UUID
    created_at: datetime


class FeedbackSummary(BaseModel):
    total: int
    positive: int
    negative: int
    neutral: int
    positive_rate: float
    negative_rate: float
    by_domain: dict[str, dict[str, int]] = Field(default_factory=dict)


class AnomalyOut(BaseModel):
    trace_id: str
    domain: CorpusDomain | None
    created_at: datetime
    metric: str
    value: float
    z_score: float
    baseline_mean: float
    baseline_std: float


class AnomalyResponse(BaseModel):
    threshold: float
    sample_size: int
    anomalies: list[AnomalyOut]
