from types import SimpleNamespace

from services.rag.telemetry import estimate_cost, extract_usage


def test_extract_usage_from_langchain_message_metadata() -> None:
    message = SimpleNamespace(
        usage_metadata={"input_tokens": 120, "output_tokens": 30, "total_tokens": 150}
    )
    assert extract_usage(message) == (120, 30, 150)


def test_extract_usage_handles_missing_metadata() -> None:
    message = SimpleNamespace()
    assert extract_usage(message) == (0, 0, 0)


def test_extract_usage_fills_total_when_absent() -> None:
    message = SimpleNamespace(usage_metadata={"input_tokens": 10, "output_tokens": 5})
    assert extract_usage(message) == (10, 5, 15)


def test_estimate_cost_returns_six_decimal_usd() -> None:
    cost = estimate_cost(1000, 2000)
    assert isinstance(cost, float)
    assert cost == round(cost, 6)
    assert cost > 0
