from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from domain.profiles import CorpusDomain
from schemas.api import (
    AnomalyOut,
    AnomalyResponse,
    DomainMetricOut,
    FeedbackSummary,
    ObservabilityResponse,
    ObservabilitySummary,
)
from services.observability.anomalies import DEFAULT_THRESHOLD, detect_anomalies
from services.observability.feedback import summarise_feedback
from storage.database import get_db
from storage.models import QueryTrace
from storage.repositories.feedback_repo import recent_feedback

router = APIRouter(prefix="/api/observability", tags=["observability"])
settings = get_settings()


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 2)
    index = (len(values) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    fraction = index - lower
    value = values[lower] + (values[upper] - values[lower]) * fraction
    return round(value, 2)


def build_domain_metric(domain: CorpusDomain, rows: list[QueryTrace]) -> DomainMetricOut:
    latencies = sorted(row.latency_ms for row in rows)
    return DomainMetricOut(
        domain=domain,
        requests=len(rows),
        p50_latency_ms=percentile(latencies, 0.5),
        p95_latency_ms=percentile(latencies, 0.95),
        average_cost_usd=round(sum(row.total_cost_usd for row in rows) / len(rows), 6),
        grounded_rate=round(sum(1 for row in rows if row.grounded) / len(rows), 4),
    )


async def _recent_traces(db: AsyncSession, limit: int) -> list[QueryTrace]:
    stmt = select(QueryTrace).order_by(QueryTrace.created_at.desc()).limit(limit)
    return list((await db.scalars(stmt)).all())


@router.get("/summary", response_model=ObservabilityResponse)
async def observability_summary(db: AsyncSession = Depends(get_db)) -> ObservabilityResponse:
    rows = await _recent_traces(db, settings.observability_recent_runs)
    latencies = sorted(row.latency_ms for row in rows)
    latest_updated_at = rows[0].created_at if rows else None

    summary = ObservabilitySummary(
        total_requests=len(rows),
        grounded_rate=round(sum(1 for row in rows if row.grounded) / len(rows), 4) if rows else 0.0,
        citation_valid_rate=(
            round(sum(1 for row in rows if row.citation_valid) / len(rows), 4) if rows else 0.0
        ),
        p50_latency_ms=percentile(latencies, 0.5),
        p95_latency_ms=percentile(latencies, 0.95),
        average_cost_usd=(
            round(sum(row.total_cost_usd for row in rows) / len(rows), 6) if rows else 0.0
        ),
        latest_updated_at=latest_updated_at,
    )

    by_domain: list[DomainMetricOut] = []
    for domain in CorpusDomain:
        domain_rows = [row for row in rows if row.domain == domain]
        if domain_rows:
            by_domain.append(build_domain_metric(domain, domain_rows))

    return ObservabilityResponse(summary=summary, by_domain=by_domain)


@router.get("/anomalies", response_model=AnomalyResponse)
async def observability_anomalies(
    threshold: float = Query(default=DEFAULT_THRESHOLD, ge=1.0, le=6.0),
    db: AsyncSession = Depends(get_db),
) -> AnomalyResponse:
    rows = await _recent_traces(db, settings.observability_recent_runs)
    anomalies = detect_anomalies(rows, threshold=threshold)
    return AnomalyResponse(
        threshold=threshold,
        sample_size=len(rows),
        anomalies=[AnomalyOut(**anomaly.to_dict()) for anomaly in anomalies],
    )


@router.get("/feedback", response_model=FeedbackSummary)
async def observability_feedback(db: AsyncSession = Depends(get_db)) -> FeedbackSummary:
    rows = await recent_feedback(db, limit=settings.observability_recent_runs)
    return summarise_feedback(rows)
