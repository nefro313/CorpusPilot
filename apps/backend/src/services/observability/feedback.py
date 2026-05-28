"""Summarise raw answer_feedback rows into a UI-friendly shape."""

from collections import defaultdict
from collections.abc import Iterable

from schemas.api import FeedbackSummary
from storage.models import AnswerFeedback


def summarise_feedback(rows: Iterable[AnswerFeedback]) -> FeedbackSummary:
    rows_list = list(rows)
    total = len(rows_list)
    positive = sum(1 for r in rows_list if r.rating > 0)
    negative = sum(1 for r in rows_list if r.rating < 0)
    neutral = total - positive - negative

    by_domain: dict[str, dict[str, int]] = defaultdict(
        lambda: {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
    )
    for row in rows_list:
        domain_key = row.domain.value if row.domain else "unknown"
        bucket = by_domain[domain_key]
        bucket["total"] += 1
        if row.rating > 0:
            bucket["positive"] += 1
        elif row.rating < 0:
            bucket["negative"] += 1
        else:
            bucket["neutral"] += 1

    return FeedbackSummary(
        total=total,
        positive=positive,
        negative=negative,
        neutral=neutral,
        positive_rate=round(positive / total, 4) if total else 0.0,
        negative_rate=round(negative / total, 4) if total else 0.0,
        by_domain=dict(by_domain),
    )
