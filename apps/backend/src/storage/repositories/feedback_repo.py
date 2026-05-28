import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.api import FeedbackRequest
from storage.models import AnswerFeedback


async def record_feedback(db: AsyncSession, payload: FeedbackRequest) -> AnswerFeedback:
    row = AnswerFeedback(
        id=uuid.uuid4(),
        session_id=payload.session_id,
        domain=payload.domain,
        question=payload.question,
        answer=payload.answer,
        rating=payload.rating,
        comment=payload.comment,
        citations=payload.citations,
        created_at=datetime.now(UTC),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def recent_feedback(db: AsyncSession, *, limit: int) -> list[AnswerFeedback]:
    stmt = select(AnswerFeedback).order_by(AnswerFeedback.created_at.desc()).limit(limit)
    return list((await db.scalars(stmt)).all())
