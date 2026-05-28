"""Add user_id to documents for per-browser session isolation.

Revision ID: 0003_user_isolation
Revises: 0002_answer_feedback
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_user_isolation"
# Placed after fb9c466e539c so the chain is linear and there is a single head.
down_revision: str | Sequence[str] | None = "fb9c466e539c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add nullable user_id column
    op.add_column("documents", sa.Column("user_id", sa.String(128), nullable=True))

    # 2. Back-fill existing rows so they all belong to the "anonymous" bucket
    op.execute("UPDATE documents SET user_id = 'anonymous' WHERE user_id IS NULL")

    # 3. Lock it down as NOT NULL
    op.alter_column("documents", "user_id", nullable=False)

    # 4. Drop the old global-unique constraint on checksum alone.
    #    The constraint name differs depending on how the schema was created
    #    (auto-generated "documents_checksum_key" vs explicit index). Use a
    #    PL/pgSQL block so the migration is idempotent regardless.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'documents_checksum_key'
                  AND conrelid = 'documents'::regclass
            ) THEN
                ALTER TABLE documents DROP CONSTRAINT documents_checksum_key;
            END IF;
        END $$;
        """
    )

    # 5. Add composite unique: one checksum per user (two users can upload the same file)
    op.create_unique_constraint(
        "uq_documents_user_checksum", "documents", ["user_id", "checksum"]
    )

    # 6. Index for fast per-user document listing
    op.create_index("idx_documents_user_id", "documents", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_documents_user_id", table_name="documents")
    op.drop_constraint("uq_documents_user_checksum", "documents", type_="unique")
    op.create_unique_constraint("documents_checksum_key", "documents", ["checksum"])
    op.drop_column("documents", "user_id")
