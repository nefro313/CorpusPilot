import asyncio
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.metrics import (
    LLM_COST_USD_TOTAL,
    LLM_TOKENS_TOTAL,
    RAG_REQUEST_LATENCY_SECONDS,
    RAG_REQUESTS_TOTAL,
    RETRIEVAL_CANDIDATES,
)
from schemas.api import AnswerTelemetry, AskRequest, ChatResponse, SourceChunk
from services.rag.followups import generate_follow_up_questions
from services.rag.graph import build_graph
from services.rag.memory import append_history, recent_history
from services.retrieval import HybridRetrievalResult, RetrievedChunk
from storage.repositories.query_trace_repo import record_query_trace

settings = get_settings()


def _to_source_chunks(hits: list[RetrievedChunk], citations: list[str]) -> list[SourceChunk]:
    citation_filter = set(citations)
    selected = [hit for hit in hits if not citation_filter or hit.citation_id in citation_filter]
    if not selected:
        selected = hits[:3]
    return [
        SourceChunk(
            citation_id=hit.citation_id or f"C{index + 1}",
            content=hit.content,
            chunk_index=hit.chunk_index,
            document_id=hit.document_id,
            document_filename=hit.document_filename,
            domain=hit.domain,
            page_number=hit.page_number,
            section_title=hit.section_title,
            semantic_score=hit.semantic_score,
            lexical_score=hit.lexical_score,
            fusion_score=hit.fusion_score,
            rerank_score=hit.rerank_score,
        )
        for index, hit in enumerate(selected)
    ]


async def run_rag_pipeline(
    db: AsyncSession, request: AskRequest, user_id: str = ""
) -> ChatResponse:
    started = time.perf_counter()
    session_id = request.session_id or str(uuid.uuid4())
    history = recent_history(session_id)

    graph = build_graph(db)
    state = await graph.ainvoke(
        {
            "question": request.question,
            "domain": request.domain.value if request.domain else None,
            "top_k": request.top_k,
            "history": history,
            "user_id": user_id,
        },
        config={
            "configurable": {"thread_id": session_id},
            "run_name": "ask_my_docs_request",
            "tags": ["production-rag", request.domain.value if request.domain else "all-domains"],
            "metadata": {
                "pipeline": "hybrid-rag",
                "langsmith_project": settings.langsmith_project,
                "session_id": session_id,
            },
        },
    )

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    retrieval = state.get("retrieval", HybridRetrievalResult([], [], []))
    hits = state.get("reranked_hits") or retrieval.fused_hits

    telemetry = AnswerTelemetry(
        latency_ms=latency_ms,
        prompt_tokens=state.get("prompt_tokens", 0),
        completion_tokens=state.get("completion_tokens", 0),
        total_tokens=state.get("total_tokens", 0),
        estimated_cost_usd=state.get("estimated_cost_usd", 0.0),
        semantic_candidates=len(retrieval.semantic_hits),
        lexical_candidates=len(retrieval.lexical_hits),
        fused_candidates=len(retrieval.fused_hits),
        reranked_candidates=len(hits),
        citation_valid=state.get("citation_valid", False),
    )
    response = ChatResponse(
        answer=state.get("answer", ""),
        domain=request.domain,
        grounded=state.get("grounded", False),
        citations=state.get("citations", []),
        sources=_to_source_chunks(hits, state.get("citations", [])),
        follow_up_questions=await generate_follow_up_questions(
            request.question,
            state.get("answer", ""),
            hits,
            request.domain,
        ),
        telemetry=telemetry,
        session_id=session_id,
    )

    await record_query_trace(db, request=request, response=response, telemetry=telemetry)
    append_history(session_id, request.question, response.answer)
    _record_metrics(
        domain_label=request.domain.value if request.domain else "all",
        telemetry=telemetry,
        grounded=response.grounded,
    )
    return response


def _record_metrics(*, domain_label: str, telemetry: AnswerTelemetry, grounded: bool) -> None:
    RAG_REQUESTS_TOTAL.labels(
        domain=domain_label,
        citation_valid=str(telemetry.citation_valid).lower(),
        grounded=str(grounded).lower(),
    ).inc()
    RAG_REQUEST_LATENCY_SECONDS.labels(domain=domain_label).observe(telemetry.latency_ms / 1000.0)
    LLM_TOKENS_TOTAL.labels(domain=domain_label, kind="prompt").inc(telemetry.prompt_tokens)
    LLM_TOKENS_TOTAL.labels(domain=domain_label, kind="completion").inc(telemetry.completion_tokens)
    LLM_COST_USD_TOTAL.labels(domain=domain_label).inc(telemetry.estimated_cost_usd)
    RETRIEVAL_CANDIDATES.labels(domain=domain_label, stage="semantic").observe(
        telemetry.semantic_candidates
    )
    RETRIEVAL_CANDIDATES.labels(domain=domain_label, stage="lexical").observe(
        telemetry.lexical_candidates
    )
    RETRIEVAL_CANDIDATES.labels(domain=domain_label, stage="fused").observe(
        telemetry.fused_candidates
    )
    RETRIEVAL_CANDIDATES.labels(domain=domain_label, stage="reranked").observe(
        telemetry.reranked_candidates
    )


async def stream_rag_response(
    db: AsyncSession, request: AskRequest, user_id: str = ""
) -> AsyncGenerator[tuple[str, Any], None]:
    response = await run_rag_pipeline(db, request, user_id)
    answer = response.answer or ""
    for index in range(0, len(answer), 40):
        await asyncio.sleep(0)
        yield ("delta", answer[index : index + 40])
    yield ("response", response)
