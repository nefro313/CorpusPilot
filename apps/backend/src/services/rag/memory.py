"""In-process session history for the RAG chat loop.

This is a deliberate single-process implementation. For multi-replica
deployments swap the module-level dict for a Redis-backed store that exposes
the same `recent_history` / `append_history` / `clear_session` surface.

The dict is bounded by `_SESSION_CAP` to avoid unbounded growth in long-
running dev servers — when capacity is exceeded the oldest session is
evicted (FIFO).
"""

from __future__ import annotations

from collections import OrderedDict

_SESSION_HISTORY_CAP = 8
_SESSION_CAP = 200
HISTORY_TURNS_FOR_PROMPT = 3

_session_history: OrderedDict[str, list[dict[str, str]]] = OrderedDict()


def recent_history(session_id: str | None) -> list[dict[str, str]]:
    if not session_id:
        return []
    bucket = _session_history.get(session_id)
    if bucket is None:
        return []
    _session_history.move_to_end(session_id)
    return list(bucket)


def append_history(session_id: str | None, question: str, answer: str) -> None:
    if not session_id or not answer.strip():
        return
    bucket = _session_history.get(session_id)
    if bucket is None:
        bucket = []
        _session_history[session_id] = bucket
        if len(_session_history) > _SESSION_CAP:
            _session_history.popitem(last=False)
    else:
        _session_history.move_to_end(session_id)
    bucket.append({"question": question, "answer": answer})
    if len(bucket) > _SESSION_HISTORY_CAP:
        del bucket[: len(bucket) - _SESSION_HISTORY_CAP]


def clear_session(session_id: str | None) -> bool:
    """Drop the in-process history for a session. Returns True if removed."""
    if not session_id:
        return False
    return _session_history.pop(session_id, None) is not None


def session_count() -> int:
    return len(_session_history)
