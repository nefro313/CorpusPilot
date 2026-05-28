import pytest

from api.routes.observability import percentile


def test_percentile_empty_returns_zero() -> None:
    assert percentile([], 0.95) == 0.0


def test_percentile_single_value_returns_that_value() -> None:
    assert percentile([42.0], 0.5) == 42.0
    assert percentile([42.0], 0.95) == 42.0


def test_percentile_50_of_sorted_evens_is_median() -> None:
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert percentile(values, 0.5) == pytest.approx(30.0)


def test_percentile_95_interpolates_between_top_values() -> None:
    values = [float(v) for v in range(1, 101)]  # 1..100, already sorted
    p95 = percentile(values, 0.95)
    assert 94.0 < p95 < 96.5
