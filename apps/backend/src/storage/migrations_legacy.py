"""In-process DDL "migrations" carried over from earlier revisions.

Until Alembic is wired in (tracked in the roadmap), `init_db()` calls these
helpers at startup so older databases pick up the columns and indexes added
since v0.1. Each function is idempotent: it checks `information_schema` before
issuing ALTER/CREATE statements, so running it twice is a no-op.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def _column_exists(conn: AsyncConnection, table_name: str, column_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is not None


async def _table_exists(conn: AsyncConnection, table_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is not None


async def migrate_documents_table(conn: AsyncConnection) -> None:
    if not await _table_exists(conn, "documents"):
        return

    if not await _column_exists(conn, "documents", "title"):
        await conn.execute(text("ALTER TABLE documents ADD COLUMN title VARCHAR(255)"))
        await conn.execute(
            text("UPDATE documents SET title = COALESCE(filename, 'Untitled') WHERE title IS NULL")
        )

    if not await _column_exists(conn, "documents", "domain"):
        await conn.execute(text("ALTER TABLE documents ADD COLUMN domain VARCHAR(64)"))
        await conn.execute(
            text(
                "UPDATE documents SET domain = 'technical_document' "
                "WHERE domain IS NULL OR domain = ''"
            )
        )

    if not await _column_exists(conn, "documents", "mime_type"):
        await conn.execute(text("ALTER TABLE documents ADD COLUMN mime_type VARCHAR(120)"))
        await conn.execute(
            text(
                "UPDATE documents SET mime_type = 'text/plain' "
                "WHERE mime_type IS NULL OR mime_type = ''"
            )
        )

    if not await _column_exists(conn, "documents", "checksum"):
        await conn.execute(text("ALTER TABLE documents ADD COLUMN checksum VARCHAR(64)"))
        await conn.execute(
            text(
                """
                UPDATE documents
                SET checksum = md5(
                    COALESCE(filename, '') || ':' || COALESCE(content, '') || ':' || id::text
                )
                WHERE checksum IS NULL OR checksum = ''
                """
            )
        )

    if not await _column_exists(conn, "documents", "metadata_json"):
        await conn.execute(text("ALTER TABLE documents ADD COLUMN metadata_json JSONB"))
        await conn.execute(
            text("UPDATE documents SET metadata_json = '{}'::jsonb WHERE metadata_json IS NULL")
        )

    if not await _column_exists(conn, "documents", "total_chunks"):
        await conn.execute(text("ALTER TABLE documents ADD COLUMN total_chunks INTEGER"))
        await conn.execute(
            text(
                """
                UPDATE documents d
                SET total_chunks = sub.chunk_count
                FROM (
                    SELECT document_id, COUNT(*)::int AS chunk_count
                    FROM document_chunks
                    GROUP BY document_id
                ) AS sub
                WHERE d.id = sub.document_id
                """
            )
        )
        await conn.execute(text("UPDATE documents SET total_chunks = 0 WHERE total_chunks IS NULL"))

    await conn.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_checksum_unique "
            "ON documents (checksum)"
        )
    )


async def migrate_document_chunks_table(conn: AsyncConnection) -> None:
    if not await _table_exists(conn, "document_chunks"):
        return

    if not await _column_exists(conn, "document_chunks", "page_number"):
        await conn.execute(text("ALTER TABLE document_chunks ADD COLUMN page_number INTEGER"))

    if not await _column_exists(conn, "document_chunks", "section_title"):
        await conn.execute(
            text("ALTER TABLE document_chunks ADD COLUMN section_title VARCHAR(255)")
        )

    if not await _column_exists(conn, "document_chunks", "token_count"):
        await conn.execute(text("ALTER TABLE document_chunks ADD COLUMN token_count INTEGER"))
        await conn.execute(
            text("UPDATE document_chunks SET token_count = 0 WHERE token_count IS NULL")
        )

    if not await _column_exists(conn, "document_chunks", "metadata_json"):
        await conn.execute(text("ALTER TABLE document_chunks ADD COLUMN metadata_json JSONB"))
        await conn.execute(
            text(
                "UPDATE document_chunks SET metadata_json = '{}'::jsonb WHERE metadata_json IS NULL"
            )
        )

    if not await _column_exists(conn, "document_chunks", "parent_chunk_id"):
        await conn.execute(
            text(
                "ALTER TABLE document_chunks ADD COLUMN parent_chunk_id UUID "
                "REFERENCES document_chunks(id) ON DELETE CASCADE"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_document_chunks_parent "
                "ON document_chunks (parent_chunk_id)"
            )
        )


async def migrate_query_traces_table(conn: AsyncConnection) -> None:
    if not await _table_exists(conn, "query_traces"):
        return

    migrations = [
        ("domain", "ALTER TABLE query_traces ADD COLUMN domain VARCHAR(64)"),
        ("prompt_tokens", "ALTER TABLE query_traces ADD COLUMN prompt_tokens INTEGER"),
        ("completion_tokens", "ALTER TABLE query_traces ADD COLUMN completion_tokens INTEGER"),
        ("total_tokens", "ALTER TABLE query_traces ADD COLUMN total_tokens INTEGER"),
        ("total_cost_usd", "ALTER TABLE query_traces ADD COLUMN total_cost_usd DOUBLE PRECISION"),
        ("latency_ms", "ALTER TABLE query_traces ADD COLUMN latency_ms DOUBLE PRECISION"),
        ("retrieval_count", "ALTER TABLE query_traces ADD COLUMN retrieval_count INTEGER"),
        ("citation_count", "ALTER TABLE query_traces ADD COLUMN citation_count INTEGER"),
        ("citation_valid", "ALTER TABLE query_traces ADD COLUMN citation_valid BOOLEAN"),
        ("grounded", "ALTER TABLE query_traces ADD COLUMN grounded BOOLEAN"),
        ("metadata_json", "ALTER TABLE query_traces ADD COLUMN metadata_json JSONB"),
    ]
    for column_name, ddl in migrations:
        if not await _column_exists(conn, "query_traces", column_name):
            await conn.execute(text(ddl))

    backfills = [
        "UPDATE query_traces SET prompt_tokens = 0 WHERE prompt_tokens IS NULL",
        "UPDATE query_traces SET completion_tokens = 0 WHERE completion_tokens IS NULL",
        "UPDATE query_traces SET total_tokens = 0 WHERE total_tokens IS NULL",
        "UPDATE query_traces SET total_cost_usd = 0 WHERE total_cost_usd IS NULL",
        "UPDATE query_traces SET latency_ms = 0 WHERE latency_ms IS NULL",
        "UPDATE query_traces SET retrieval_count = 0 WHERE retrieval_count IS NULL",
        "UPDATE query_traces SET citation_count = 0 WHERE citation_count IS NULL",
        "UPDATE query_traces SET citation_valid = false WHERE citation_valid IS NULL",
        "UPDATE query_traces SET grounded = false WHERE grounded IS NULL",
        "UPDATE query_traces SET metadata_json = '{}'::jsonb WHERE metadata_json IS NULL",
    ]
    for stmt in backfills:
        await conn.execute(text(stmt))


async def create_runtime_indexes(conn: AsyncConnection) -> None:
    statements = [
        "CREATE INDEX IF NOT EXISTS idx_documents_domain_created_at "
        "ON documents (domain, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_document_chunks_document_chunk "
        "ON document_chunks (document_id, chunk_index)",
        "CREATE INDEX IF NOT EXISTS idx_document_chunks_fts "
        "ON document_chunks USING GIN (to_tsvector('english', content))",
        "CREATE INDEX IF NOT EXISTS idx_query_traces_created_at ON query_traces (created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_answer_feedback_created_at "
        "ON answer_feedback (created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_answer_feedback_domain_rating "
        "ON answer_feedback (domain, rating)",
        "CREATE INDEX IF NOT EXISTS idx_document_table_rows_document "
        "ON document_table_rows (document_id, table_index, row_index)",
        "CREATE INDEX IF NOT EXISTS idx_document_table_rows_column "
        "ON document_table_rows (lower(column_name))",
    ]
    for stmt in statements:
        await conn.execute(text(stmt))
