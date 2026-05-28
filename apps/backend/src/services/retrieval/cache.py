import asyncio

from langchain_community.retrievers import BM25Retriever

from core.metrics import BM25_CACHE_EVENTS
from domain.profiles import CorpusDomain

_bm25_cache: dict[str, BM25Retriever] = {}
_bm25_cache_lock = asyncio.Lock()


def cache_key(domain: CorpusDomain | None, user_id: str = "") -> str:
    domain_part = domain.value if domain else "__all__"
    return f"{user_id}:{domain_part}"


async def get_cached_retriever(
    domain: CorpusDomain | None, user_id: str = ""
) -> BM25Retriever | None:
    async with _bm25_cache_lock:
        result = _bm25_cache.get(cache_key(domain, user_id))
        label = domain.value if domain else "__all__"
        if result is not None:
            BM25_CACHE_EVENTS.labels(domain=label, event="hit").inc()
        else:
            BM25_CACHE_EVENTS.labels(domain=label, event="miss").inc()
        return result


async def set_cached_retriever(
    domain: CorpusDomain | None, retriever: BM25Retriever, user_id: str = ""
) -> None:
    async with _bm25_cache_lock:
        _bm25_cache[cache_key(domain, user_id)] = retriever


async def invalidate_retrieval_cache(
    domain: CorpusDomain | None = None, user_id: str = ""
) -> None:
    async with _bm25_cache_lock:
        label = domain.value if domain else "__all__"
        BM25_CACHE_EVENTS.labels(domain=label, event="invalidate").inc()
        if domain is None and not user_id:
            _bm25_cache.clear()
            return
        # Remove the specific (user, domain) entry and the catch-all (user, None)
        _bm25_cache.pop(cache_key(domain, user_id), None)
        _bm25_cache.pop(cache_key(None, user_id), None)
