"""Add answer_feedback table for the user feedback loop.

Revision ID: 0002_answer_feedback
Revises: 0001_baseline
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_answer_feedback"
down_revision: str | Sequence[str] | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "answer_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("domain", sa.String(length=64), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("citations", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "idx_answer_feedback_created_at",
        "answer_feedback",
        ["created_at"],
        unique=False,
        postgresql_using="btree",
        postgresql_ops={"created_at": "DESC"},
    )
    op.create_index(
        "idx_answer_feedback_domain_rating",
        "answer_feedback",
        ["domain", "rating"],
    )


def downgrade() -> None:
    op.drop_index("idx_answer_feedback_domain_rating", table_name="answer_feedback")
    op.drop_index("idx_answer_feedback_created_at", table_name="answer_feedback")
    op.drop_table("answer_feedback")
