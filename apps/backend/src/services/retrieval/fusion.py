from core.config import get_settings
from domain.profiles import CorpusDomain
from services.retrieval.types import RetrievedChunk

settings = get_settings()

DEFAULT_WEIGHTS = (0.65, 0.35)

# (semantic_weight, lexical_weight) per domain.
# Legal/financial flip toward lexical because exact clause numbers, line items
# and identifiers must match by token. Research papers stay semantic-heavy.
DOMAIN_WEIGHTS: dict[CorpusDomain, tuple[float, float]] = {
    CorpusDomain.LEGAL_CONTRACT: (0.30, 0.70),
    CorpusDomain.FINANCIAL_DOCUMENT: (0.35, 0.65),
    CorpusDomain.TECHNICAL_DOCUMENT: (0.60, 0.40),
    CorpusDomain.RESEARCH_PAPER: (0.75, 0.25),
    CorpusDomain.HEALTHCARE_DOCUMENT: (0.50, 0.50),
}


def reciprocal_rank_fusion(
    semantic_hits: list[RetrievedChunk],
    lexical_hits: list[RetrievedChunk],
    top_k: int,
    domain: CorpusDomain | None = None,
) -> list[RetrievedChunk]:
    rrf_k = settings.retrieval_rrf_k
    sem_w, lex_w = DOMAIN_WEIGHTS.get(domain, DEFAULT_WEIGHTS) if domain else DEFAULT_WEIGHTS
    combined: dict[str, RetrievedChunk] = {}
    for weight, ranked_hits in ((sem_w, semantic_hits), (lex_w, lexical_hits)):
        for rank, hit in enumerate(ranked_hits):
            existing = combined.get(hit.chunk_id)
            score_boost = weight / (rrf_k + rank + 1)
            if existing is None:
                hit.fusion_score = round(score_boost, 6)
                combined[hit.chunk_id] = hit
                continue
            existing.fusion_score = round((existing.fusion_score or 0.0) + score_boost, 6)
            existing.semantic_score = existing.semantic_score or hit.semantic_score
            existing.lexical_score = existing.lexical_score or hit.lexical_score

    fused = sorted(combined.values(), key=lambda item: item.fusion_score or 0.0, reverse=True)
    for index, hit in enumerate(fused[:top_k], start=1):
        hit.citation_id = f"C{index}"
    return fused[:top_k]
