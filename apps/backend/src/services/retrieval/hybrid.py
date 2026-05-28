import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from domain.profiles import CorpusDomain, DomainProfile
from services.retrieval.fusion import reciprocal_rank_fusion
from services.retrieval.lexical import lexical_search
from services.retrieval.semantic import semantic_search
from services.retrieval.types import HybridRetrievalResult

settings = get_settings()


async def hybrid_search(
    db: AsyncSession,
    query: str,
    domain: CorpusDomain | None,
    profile: DomainProfile | None,
    top_k: int | None = None,
    user_id: str = "",
) -> HybridRetrievalResult:
    semantic_k = settings.retrieval_semantic_k
    lexical_k = settings.retrieval_lexical_k
    fusion_k = (top_k or profile.retrieval_k) if profile else settings.retrieval_fusion_k
    semantic_hits, lexical_hits = await asyncio.gather(
        semantic_search(db, query, domain, semantic_k, user_id),
        lexical_search(db, query, domain, lexical_k, user_id),
    )
    fused_hits = reciprocal_rank_fusion(semantic_hits, lexical_hits, fusion_k, domain=domain)
    return HybridRetrievalResult(
        semantic_hits=semantic_hits,
        lexical_hits=lexical_hits,
        fused_hits=fused_hits,
    )
