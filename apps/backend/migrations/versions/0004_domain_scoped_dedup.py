"""Scope document dedup to (user_id, domain, checksum).

The same file may be indexed into different domains (e.g. after first
uploading it under the wrong domain). The previous uniqueness rules — the
legacy global index on checksum alone and the per-user constraint from
0003 — both blocked that, surfacing as an IntegrityError during indexing.

Revision ID: 0004_domain_scoped_dedup
Revises: 0003_user_isolation
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0004_domain_scoped_dedup"
down_revision: str | Sequence[str] | None = "0003_user_isolation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Legacy global unique index on checksum alone (created by the pre-Alembic
    # in-process migrations); 0003 missed it.
    op.execute("DROP INDEX IF EXISTS idx_documents_checksum_unique")

    # Per-user constraint from 0003 — still blocks cross-domain re-uploads.
    op.execute(
        "ALTER TABLE documents DROP CONSTRAINT IF EXISTS uq_documents_user_checksum"
    )

    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_documents_user_domain_checksum "
        "ON documents (user_id, domain, checksum)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_documents_user_domain_checksum")
    op.create_unique_constraint(
        "uq_documents_user_checksum", "documents", ["user_id", "checksum"]
    )
