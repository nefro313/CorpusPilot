from sqlalchemy.ext.asyncio import AsyncSession

from schemas.api import AnswerTelemetry, AskRequest, ChatResponse
from storage.models import QueryTrace


async def record_query_trace(
    db: AsyncSession,
    *,
    request: AskRequest,
    response: ChatResponse,
    telemetry: AnswerTelemetry,
) -> None:
    db.add(
        QueryTrace(
            domain=request.domain,
            question=request.question,
            answer=response.answer,
            prompt_tokens=telemetry.prompt_tokens,
            completion_tokens=telemetry.completion_tokens,
            total_tokens=telemetry.total_tokens,
            total_cost_usd=telemetry.estimated_cost_usd,
            latency_ms=telemetry.latency_ms,
            retrieval_count=telemetry.fused_candidates,
            citation_count=len(response.citations),
            citation_valid=telemetry.citation_valid,
            grounded=response.grounded,
            metadata_json={
                "semantic_candidates": telemetry.semantic_candidates,
                "lexical_candidates": telemetry.lexical_candidates,
                "reranked_candidates": telemetry.reranked_candidates,
            },
        )
    )
    await db.commit()
