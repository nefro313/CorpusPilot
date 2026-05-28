"""First-page domain classification.

Cheap pre-flight gate before the full LlamaParse/chunk/embed pipeline: extract
the first page locally, ask the guard LLM which of the supported corpus domains
the document belongs to, and surface a structured verdict.

The result drives three outcomes in the upload pipeline:

- ``matches``     — predicted domain equals the user-selected domain → continue.
- ``mismatch``    — predicted domain is one of the supported five but differs
                    from the selection → reject with a suggested domain.
- ``out_of_scope``— the content does not fit any supported domain → reject.

Failures (LLM error, empty first page, unparseable JSON) intentionally fail
open: callers log a warning and let the upload proceed. This keeps the gate
helpful without becoming a single point of failure for ingestion.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage

from domain.profiles import DOMAIN_PROFILES, CorpusDomain
from services.ingestion.parsing import extract_preview_text
from services.llm import get_guard_llm

logger = logging.getLogger(__name__)

ClassificationVerdict = Literal["matches", "mismatch", "out_of_scope", "unknown"]

_MIN_PREVIEW_CHARS = 60
_PREVIEW_CHAR_LIMIT = 3500


@dataclass(frozen=True)
class ClassificationResult:
    verdict: ClassificationVerdict
    predicted_domain: CorpusDomain | None
    confidence: float
    reason: str

    @property
    def should_reject(self) -> bool:
        return self.verdict in {"mismatch", "out_of_scope"}


def _build_messages(preview: str) -> list[object]:
    catalogue = "\n".join(
        f"- {domain.value}: {profile.description}"
        for domain, profile in DOMAIN_PROFILES.items()
    )
    system = (
        "You classify the domain of a single document for a multi-domain RAG ingestion gate. "
        "You see only the first page. Pick the single best-fitting domain from the catalogue "
        "or declare the document out of scope. Be strict: a marketing brochure, a recipe, "
        "a personal letter, song lyrics, or generic prose with no professional context is "
        "out_of_scope even if a domain feels vaguely related.\n\n"
        f"Supported domains:\n{catalogue}\n\n"
        "Respond with ONLY a JSON object using these keys: "
        '{"predicted_domain": <one of the domain values above or "out_of_scope">, '
        '"confidence": <number between 0 and 1>, '
        '"reason": <one short sentence>}. '
        "No prose, no markdown fences."
    )
    human = f"First page of the uploaded document:\n\n{preview}"
    return [SystemMessage(content=system), HumanMessage(content=human)]


def _parse_llm_payload(raw: str) -> dict[str, object] | None:
    if not raw:
        return None
    text = raw.strip()
    # Strip ```json ... ``` fences if the model ignored the instruction.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict):
        return None
    return data


def _coerce_domain(value: object) -> CorpusDomain | None:
    if not isinstance(value, str):
        return None
    candidate = value.strip().lower()
    try:
        return CorpusDomain(candidate)
    except ValueError:
        return None


def _coerce_confidence(value: object) -> float:
    try:
        score = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, score))


async def classify_first_page(
    *,
    filename: str,
    payload: bytes,
    mime_type: str | None,
    selected_domain: CorpusDomain,
) -> ClassificationResult:
    """Classify the first page of an uploaded file against ``selected_domain``.

    Always returns a ``ClassificationResult``; on any failure path the verdict
    is ``"unknown"`` so callers can fail open.
    """
    _, preview = extract_preview_text(filename, payload, mime_type)
    preview = (preview or "").strip()
    if len(preview) < _MIN_PREVIEW_CHARS:
        return ClassificationResult(
            verdict="unknown",
            predicted_domain=None,
            confidence=0.0,
            reason="First page produced too little readable text for classification.",
        )

    preview = preview[:_PREVIEW_CHAR_LIMIT]
    messages = _build_messages(preview)

    try:
        response = await get_guard_llm().ainvoke(messages)
    except Exception as exc:
        logger.warning("Domain classifier LLM call failed for %s: %s", filename, exc)
        return ClassificationResult(
            verdict="unknown",
            predicted_domain=None,
            confidence=0.0,
            reason="Classifier unavailable; skipping pre-flight check.",
        )

    raw = getattr(response, "content", "")
    if isinstance(raw, list):
        raw = "".join(part for part in raw if isinstance(part, str))
    payload_json = _parse_llm_payload(str(raw))
    if payload_json is None:
        logger.warning("Domain classifier returned unparseable payload for %s: %r", filename, raw)
        return ClassificationResult(
            verdict="unknown",
            predicted_domain=None,
            confidence=0.0,
            reason="Classifier response could not be parsed; skipping pre-flight check.",
        )

    raw_domain = payload_json.get("predicted_domain")
    confidence = _coerce_confidence(payload_json.get("confidence"))
    reason = str(payload_json.get("reason") or "").strip() or "No reason provided."

    if isinstance(raw_domain, str) and raw_domain.strip().lower() == "out_of_scope":
        return ClassificationResult(
            verdict="out_of_scope",
            predicted_domain=None,
            confidence=confidence,
            reason=reason,
        )

    predicted = _coerce_domain(raw_domain)
    if predicted is None:
        return ClassificationResult(
            verdict="unknown",
            predicted_domain=None,
            confidence=confidence,
            reason="Classifier did not return a recognised domain.",
        )

    if predicted == selected_domain:
        return ClassificationResult(
            verdict="matches",
            predicted_domain=predicted,
            confidence=confidence,
            reason=reason,
        )
    return ClassificationResult(
        verdict="mismatch",
        predicted_domain=predicted,
        confidence=confidence,
        reason=reason,
    )
