import asyncio
from collections.abc import Iterable
from typing import Any

from pymilvus import DataType, MilvusClient

from core.config import get_settings
from domain.profiles import CorpusDomain
from vectorstores.base import VectorChunkRecord, VectorSearchResult

settings = get_settings()


class MilvusVectorStore:
    def __init__(self) -> None:
        self._client: MilvusClient | None = None
        self._client_lock = asyncio.Lock()
        self._init_lock = asyncio.Lock()
        self.collection_name = settings.milvus_collection_name
        self.vector_field_name = settings.milvus_vector_field_name

    async def ensure_ready(self) -> None:
        async with self._init_lock:
            client = await self._get_client()
            exists = await asyncio.to_thread(
                client.has_collection,
                collection_name=self.collection_name,
            )
            if exists and not await asyncio.to_thread(self._has_user_id_field, client):
                # Old collection schema is missing user_id — drop and recreate so
                # per-user isolation works. Existing data must be re-uploaded.
                await asyncio.to_thread(
                    client.drop_collection,
                    collection_name=self.collection_name,
                )
                exists = False
            if not exists:
                await asyncio.to_thread(self._create_collection, client)
            await asyncio.to_thread(self._load_collection_if_supported, client)

    def _has_user_id_field(self, client: MilvusClient) -> bool:
        try:
            schema = client.describe_collection(collection_name=self.collection_name)
            fields = schema.get("fields", [])
            return any(f.get("name") == "user_id" for f in fields)
        except Exception:
            return False

    async def upsert_chunks(self, chunks: list[VectorChunkRecord]) -> None:
        if not chunks:
            return
        await self.ensure_ready()
        client = await self._get_client()
        payload = [self._serialize_chunk(chunk) for chunk in chunks]
        await asyncio.to_thread(
            client.upsert,
            collection_name=self.collection_name,
            data=payload,
        )

    async def delete_chunks(self, chunk_ids: Iterable[str]) -> None:
        ids = [chunk_id for chunk_id in chunk_ids if chunk_id]
        if not ids:
            return
        await self.ensure_ready()
        client = await self._get_client()
        await asyncio.to_thread(
            client.delete,
            collection_name=self.collection_name,
            ids=ids,
        )

    async def get_existing_chunk_ids(self, chunk_ids: Iterable[str]) -> set[str]:
        ids = [chunk_id for chunk_id in chunk_ids if chunk_id]
        if not ids:
            return set()
        await self.ensure_ready()
        client = await self._get_client()
        rows = await asyncio.to_thread(
            client.get,
            collection_name=self.collection_name,
            ids=ids,
            output_fields=["chunk_id"],
        )
        return {
            str(row.get("chunk_id") or row.get("id"))
            for row in rows
            if isinstance(row, dict) and (row.get("chunk_id") or row.get("id"))
        }

    async def count_chunks(self) -> int:
        await self.ensure_ready()
        client = await self._get_client()
        rows = await asyncio.to_thread(
            client.query,
            collection_name=self.collection_name,
            filter='chunk_id != ""',
            output_fields=["count(*)"],
        )
        if not rows:
            return 0
        return int(rows[0].get("count(*)", 0))

    async def search(
        self,
        *,
        embedding: list[float],
        domain: CorpusDomain | None,
        user_id: str = "",
        limit: int,
    ) -> list[VectorSearchResult]:
        await self.ensure_ready()
        client = await self._get_client()
        parts: list[str] = []
        if user_id:
            parts.append(f'user_id == "{user_id}"')
        if domain:
            parts.append(f'domain == "{domain.value}"')
        filter_expr = " && ".join(parts)
        rows = await asyncio.to_thread(
            client.search,
            collection_name=self.collection_name,
            data=[embedding],
            filter=filter_expr,
            limit=limit,
            anns_field=self.vector_field_name,
            output_fields=[
                "chunk_id",
                "document_id",
                "document_filename",
                "domain",
                "chunk_index",
                "page_number",
                "section_title",
                "content",
            ],
            search_params=settings.milvus_search_params,
        )
        hits = rows[0] if rows else []
        return [self._deserialize_hit(hit) for hit in hits]

    async def _get_client(self) -> MilvusClient:
        async with self._client_lock:
            if self._client is None:
                endpoint = settings.zillizcloud_endpoint.strip()
                api_key = settings.zillizcloud_api_key.strip()
                if not endpoint or not api_key:
                    raise RuntimeError(
                        "Zilliz Cloud is not configured. Set ZILLIZCLOUD_ENDPOINT and ZILLIZCLOUD_API_KEY."
                    )
                self._client = MilvusClient(uri=endpoint, token=api_key)
            return self._client

    def _create_collection(self, client: MilvusClient) -> None:
        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=False,
        )
        schema.add_field(
            field_name="chunk_id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            max_length=64,
        )
        schema.add_field(field_name="document_id", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="document_filename", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="domain", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="user_id", datatype=DataType.VARCHAR, max_length=128)
        schema.add_field(field_name="chunk_index", datatype=DataType.INT64)
        schema.add_field(field_name="page_number", datatype=DataType.INT64)
        schema.add_field(field_name="section_title", datatype=DataType.VARCHAR, max_length=512)
        schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(
            field_name=self.vector_field_name,
            datatype=DataType.FLOAT_VECTOR,
            dim=settings.embedding_dimensions,
        )

        index_params = client.prepare_index_params()
        index_params.add_index(field_name="chunk_id", index_type="AUTOINDEX")
        index_params.add_index(field_name="document_id", index_type="AUTOINDEX")
        index_params.add_index(field_name="domain", index_type="AUTOINDEX")
        index_params.add_index(field_name="user_id", index_type="AUTOINDEX")
        index_params.add_index(
            field_name=self.vector_field_name,
            index_type="AUTOINDEX",
            metric_type=settings.milvus_metric_type,
        )
        client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )

    def _load_collection_if_supported(self, client: MilvusClient) -> None:
        load_collection = getattr(client, "load_collection", None)
        if load_collection is None:
            return
        try:
            load_collection(collection_name=self.collection_name)
        except TypeError:
            load_collection(collection_name=self.collection_name, replica_number=1)

    def _serialize_chunk(self, chunk: VectorChunkRecord) -> dict[str, Any]:
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "document_filename": chunk.document_filename,
            "domain": chunk.domain.value,
            "user_id": chunk.user_id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number if chunk.page_number is not None else -1,
            "section_title": chunk.section_title or "",
            "content": chunk.content,
            self.vector_field_name: chunk.embedding,
        }

    def _deserialize_hit(self, hit: Any) -> VectorSearchResult:
        payload = self._normalize_hit(hit)
        distance = payload.get("distance")
        score = payload.get("score")
        semantic_score: float | None = None
        if score is not None:
            semantic_score = round(float(score), 6)
        elif distance is not None:
            semantic_score = round(1 - float(distance), 6)

        page_number = payload.get("page_number")
        if page_number == -1:
            page_number = None
        section_title = payload.get("section_title") or None

        return VectorSearchResult(
            chunk_id=str(payload["chunk_id"]),
            document_id=str(payload["document_id"]),
            document_filename=str(payload["document_filename"]),
            domain=CorpusDomain(str(payload["domain"])),
            content=str(payload["content"]),
            chunk_index=int(payload["chunk_index"]),
            page_number=int(page_number) if page_number is not None else None,
            section_title=section_title,
            semantic_score=semantic_score,
        )

    def _normalize_hit(self, hit: Any) -> dict[str, Any]:
        if isinstance(hit, dict):
            entity = hit.get("entity", {})
            if not isinstance(entity, dict):
                entity = {}
            merged = dict(entity)
            if "id" in hit and "chunk_id" not in merged:
                merged["chunk_id"] = hit["id"]
            if "distance" in hit:
                merged["distance"] = hit["distance"]
            if "score" in hit:
                merged["score"] = hit["score"]
            return merged

        entity = getattr(hit, "entity", None)
        if not isinstance(entity, dict):
            entity = {}
        merged = dict(entity)
        raw_id = getattr(hit, "id", None) or getattr(hit, "pk", None)
        if raw_id is not None and "chunk_id" not in merged:
            merged["chunk_id"] = raw_id
        raw_distance = getattr(hit, "distance", None)
        if raw_distance is not None:
            merged["distance"] = raw_distance
        raw_score = getattr(hit, "score", None)
        if raw_score is not None:
            merged["score"] = raw_score
        return merged


vector_store = MilvusVectorStore()
