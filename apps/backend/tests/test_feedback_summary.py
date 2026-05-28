from types import SimpleNamespace

from domain.profiles import CorpusDomain
from services.observability.feedback import summarise_feedback


def _row(
    rating: int, domain: CorpusDomain | None = CorpusDomain.TECHNICAL_DOCUMENT
) -> SimpleNamespace:
    return SimpleNamespace(rating=rating, domain=domain)


def test_summarise_empty_feedback() -> None:
    summary = summarise_feedback([])
    assert summary.total == 0
    assert summary.positive_rate == 0.0
    assert summary.negative_rate == 0.0
    assert summary.by_domain == {}


def test_summarise_counts_positive_negative_neutral() -> None:
    rows = [_row(1), _row(1), _row(-1), _row(0)]
    summary = summarise_feedback(rows)
    assert summary.total == 4
    assert summary.positive == 2
    assert summary.negative == 1
    assert summary.neutral == 1
    assert summary.positive_rate == 0.5
    assert summary.negative_rate == 0.25


def test_summarise_groups_by_domain() -> None:
    rows = [
        _row(1, CorpusDomain.TECHNICAL_DOCUMENT),
        _row(-1, CorpusDomain.TECHNICAL_DOCUMENT),
        _row(1, CorpusDomain.LEGAL_CONTRACT),
        _row(0, None),
    ]
    summary = summarise_feedback(rows)
    tech = summary.by_domain[CorpusDomain.TECHNICAL_DOCUMENT.value]
    assert tech == {"total": 2, "positive": 1, "negative": 1, "neutral": 0}
    assert summary.by_domain[CorpusDomain.LEGAL_CONTRACT.value]["positive"] == 1
    assert summary.by_domain["unknown"]["neutral"] == 1
