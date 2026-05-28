from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from domain.profiles import CorpusDomain
from services.observability.anomalies import (
    MIN_SAMPLES_PER_DOMAIN,
    detect_anomalies,
)


def _trace(
    *,
    latency_ms: float,
    cost: float = 0.001,
    domain: CorpusDomain | None = CorpusDomain.TECHNICAL_DOCUMENT,
    when: datetime | None = None,
    trace_id: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=trace_id or f"t-{latency_ms}-{cost}",
        domain=domain,
        latency_ms=latency_ms,
        total_cost_usd=cost,
        created_at=when or datetime.now(UTC),
    )


def test_empty_input_returns_no_anomalies() -> None:
    assert detect_anomalies([]) == []


def test_below_min_samples_returns_no_anomalies() -> None:
    rows = [_trace(latency_ms=100.0) for _ in range(MIN_SAMPLES_PER_DOMAIN - 2)]
    rows.append(_trace(latency_ms=10000.0))
    assert len(rows) < MIN_SAMPLES_PER_DOMAIN
    assert detect_anomalies(rows) == []


def test_obvious_latency_outlier_is_flagged() -> None:
    rows = [
        _trace(latency_ms=120.0 + i, when=datetime.now(UTC) + timedelta(seconds=i))
        for i in range(MIN_SAMPLES_PER_DOMAIN)
    ]
    rows.append(_trace(latency_ms=5000.0, when=datetime.now(UTC) + timedelta(minutes=1)))
    anomalies = detect_anomalies(rows, threshold=2.0)
    latency_hits = [a for a in anomalies if a.metric == "latency_ms"]
    assert latency_hits, "expected the 5000ms outlier to be flagged"
    assert latency_hits[0].value == 5000.0
    assert latency_hits[0].z_score > 2.0


def test_each_domain_gets_its_own_baseline() -> None:
    tech = [
        _trace(latency_ms=100.0 + i, domain=CorpusDomain.TECHNICAL_DOCUMENT)
        for i in range(MIN_SAMPLES_PER_DOMAIN)
    ]
    legal = [
        _trace(latency_ms=2000.0 + i, domain=CorpusDomain.LEGAL_CONTRACT)
        for i in range(MIN_SAMPLES_PER_DOMAIN)
    ]
    # A 2000ms request is normal in legal, an outlier in technical.
    anomalies = detect_anomalies([*tech, *legal], threshold=2.0)
    assert all(a.domain != CorpusDomain.LEGAL_CONTRACT for a in anomalies)
