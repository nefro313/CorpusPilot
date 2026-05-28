from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings
from storage.migrations_legacy import (
    create_runtime_indexes,
    migrate_document_chunks_table,
    migrate_documents_table,
    migrate_query_traces_table,
)
from vectorstores import vector_store
from vectorstores.sync import backfill_missing_vectors

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    from storage.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await migrate_documents_table(conn)
        await migrate_document_chunks_table(conn)
        await migrate_query_traces_table(conn)
        await create_runtime_indexes(conn)

    await vector_store.ensure_ready()
    await backfill_missing_vectors(async_session)
