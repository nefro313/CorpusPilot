"""Session lifecycle helpers for the chat pipeline.

A "session" here owns two pieces of in-process state:
  1. The conversation history (`memory._session_history`) — used to build
     the rewrite prompt and the system message context.
  2. The LangGraph checkpoint thread keyed on the same id — used by
     `MemorySaver` so the graph can resume mid-flow if needed.

Both must be cleared together when the frontend drops a session (e.g. when
the user starts a new chat or switches the active corpus domain).
"""

from __future__ import annotations

import logging

from services.rag.graph import get_checkpointer
from services.rag.memory import clear_session

logger = logging.getLogger(__name__)


def end_session(session_id: str) -> bool:
    """Clear in-memory chat history AND the LangGraph thread for a session.

    Returns True if either side actually removed something.
    """
    history_dropped = clear_session(session_id)
    thread_dropped = False
    try:
        get_checkpointer().delete_thread(session_id)
        thread_dropped = True
    except Exception as exc:
        # delete_thread raises only on backend errors; an unknown thread id
        # is fine. Log at debug so missing-thread cleanup doesn't spam.
        logger.debug("checkpointer delete_thread(%s) failed: %s", session_id, exc)

    return history_dropped or thread_dropped
