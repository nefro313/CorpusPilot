"""Baseline revision.

The schema for documents, document_chunks and query_traces was created by the
runtime `init_db` helper in earlier versions. This revision is intentionally
empty so an existing database can be stamped without changes:

    alembic stamp 0001_baseline

New schema changes should be added as fresh revisions on top of this one.
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "0001_baseline"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
