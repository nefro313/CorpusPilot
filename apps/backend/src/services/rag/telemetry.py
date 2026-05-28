from typing import Any

from core.config import get_settings

settings = get_settings()


def extract_usage(message: Any) -> tuple[int, int, int]:
    usage = getattr(message, "usage_metadata", None) or {}
    prompt_tokens = int(usage.get("input_tokens", 0))
    completion_tokens = int(usage.get("output_tokens", 0))
    total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens))
    return prompt_tokens, completion_tokens, total_tokens


def estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    input_cost = (prompt_tokens / 1000) * settings.chat_input_cost_per_1k
    output_cost = (completion_tokens / 1000) * settings.chat_output_cost_per_1k
    return round(input_cost + output_cost, 6)
