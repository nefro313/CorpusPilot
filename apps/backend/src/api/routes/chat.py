from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_user_id
from api.sse import SSE_HEADERS, SSE_MEDIA_TYPE, format_sse
from schemas.api import AskRequest, ChatResponse, FeedbackAck, FeedbackRequest
from services.rag import end_session, run_rag_pipeline, stream_rag_response
from storage.database import get_db
from storage.repositories.feedback_repo import record_feedback

router = APIRouter(prefix="/api/chat", tags=["chat"])


class SessionDeleted(BaseModel):
    session_id: str
    cleared: bool


@router.post("/", response_model=ChatResponse)
async def chat(
    req: AskRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
) -> ChatResponse:
    return await run_rag_pipeline(db, req, user_id)


@router.post("/stream")
async def chat_stream(
    req: AskRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_user_id),
):
    return _sse_stream(stream_rag_response(db, req, user_id))


@router.post("/feedback", response_model=FeedbackAck, status_code=201)
async def chat_feedback(
    payload: FeedbackRequest, db: AsyncSession = Depends(get_db)
) -> FeedbackAck:
    row = await record_feedback(db, payload)
    return FeedbackAck(id=row.id, created_at=row.created_at)


@router.delete("/session/{session_id}", response_model=SessionDeleted)
async def end_chat_session(
    session_id: str = Path(..., min_length=1, max_length=128),
) -> SessionDeleted:
    """Drop the in-process history and LangGraph thread for a session.

    The frontend calls this when starting a new chat or switching domains
    so that the abandoned thread does not linger in memory.
    """
    cleared = end_session(session_id)
    return SessionDeleted(session_id=session_id, cleared=cleared)


def _sse_stream(source: AsyncGenerator[tuple[str, Any], None]) -> StreamingResponse:
    async def event_generator():
        try:
            async for event_type, data in source:
                if event_type == "delta":
                    yield format_sse("text_delta", {"delta": data})
                elif event_type == "response":
                    yield format_sse("response", data.model_dump())
                    yield format_sse(
                        "sources",
                        {"sources": [source.model_dump() for source in data.sources]},
                    )
            yield format_sse("done", {})
        except Exception as exc:
            yield format_sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type=SSE_MEDIA_TYPE,
        headers=SSE_HEADERS,
    )
