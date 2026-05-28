"""Z-score based anomaly detection over query_traces.

Why a hand-rolled detector instead of pulling in scikit-learn:
- Z-score is the right model for the question we ask ("is *this* request unusual
  compared to recent traffic for the same domain"), and it's transparent enough
  to defend in a code review.
- A 5-line detector keeps the AIOps endpoint dependency-free, which matters for
  CI cold-start and for the read-only review surface auditors expect.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from domain.profiles import CorpusDomain
from storage.models import QueryTrace

DEFAULT_THRESHOLD = 2.5
MIN_SAMPLES_PER_DOMAIN = 8


@dataclass(slots=True)
class AnomalyRecord:
    trace_id: str
    domain: CorpusDomain | None
    created_at: datetime
    metric: str
    value: float
    z_score: float
    baseline_mean: float
    baseline_std: float

    def to_dict(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "domain": self.domain.value if self.domain else None,
            "created_at": self.created_at.isoformat(),
            "metric": self.metric,
            "value": round(self.value, 6),
            "z_score": round(self.z_score, 3),
            "baseline_mean": round(self.baseline_mean, 6),
            "baseline_std": round(self.baseline_std, 6),
        }


def _zscores_for_metric(
    rows: list[QueryTrace],
    metric_attr: str,
    metric_label: str,
    threshold: float,
) -> list[AnomalyRecord]:
    values = [float(getattr(row, metric_attr) or 0.0) for row in rows]
    if len(values) < MIN_SAMPLES_PER_DOMAIN:
        return []

    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)
    if std == 0:
        return []

    anomalies: list[AnomalyRecord] = []
    for row, value in zip(rows, values, strict=True):
        z = (value - mean) / std
        if abs(z) >= threshold:
            anomalies.append(
                AnomalyRecord(
                    trace_id=str(row.id),
                    domain=row.domain,
                    created_at=row.created_at,
                    metric=metric_label,
                    value=value,
                    z_score=z,
                    baseline_mean=mean,
                    baseline_std=std,
                )
            )
    return anomalies


def detect_anomalies(
    rows: Iterable[QueryTrace],
    *,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[AnomalyRecord]:
    """Group rows by domain and flag latency / cost outliers per domain.

    Cross-domain comparison would mask real domain-specific behaviour
    (legal answers are routinely slower than technical ones), so the
    baseline is computed per-domain.
    """
    rows_list = list(rows)
    if not rows_list:
        return []

    by_domain: dict[CorpusDomain | None, list[QueryTrace]] = {}
    for row in rows_list:
        by_domain.setdefault(row.domain, []).append(row)

    anomalies: list[AnomalyRecord] = []
    for domain_rows in by_domain.values():
        anomalies.extend(_zscores_for_metric(domain_rows, "latency_ms", "latency_ms", threshold))
        anomalies.extend(
            _zscores_for_metric(domain_rows, "total_cost_usd", "total_cost_usd", threshold)
        )

    anomalies.sort(key=lambda a: abs(a.z_score), reverse=True)
    return anomalies
