from typing import TypedDict

from services.retrieval import HybridRetrievalResult, RetrievedChunk


class RAGState(TypedDict, total=False):
    question: str
    rewritten_question: str
    query_variants: list[str]
    history: list[dict[str, str]]
    domain: str | None
    top_k: int | None
    user_id: str
    retrieval: HybridRetrievalResult
    reranked_hits: list[RetrievedChunk]
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    citation_valid: bool
    citations: list[str]
    grounded: bool
    follow_up_questions: list[str]
    sql_context: str | None
    # ── Agentic control fields ────────────────────────────────────────────────
    # retry_count   – how many retrieval-retry loops have fired this request
    # needs_broader_query – signal from grade_retrieval / validate to widen search
    # retrieval_grade_reason – human-readable explanation from the grader LLM
    retry_count: int
    needs_broader_query: bool
    retrieval_grade_reason: str
