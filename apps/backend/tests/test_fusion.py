from domain.profiles import CorpusDomain
from services.retrieval.fusion import reciprocal_rank_fusion
from services.retrieval.types import RetrievedChunk


def _chunk(
    chunk_id: str, *, semantic: float | None = None, lexical: float | None = None
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc",
        document_filename="doc.pdf",
        domain=CorpusDomain.TECHNICAL_DOCUMENT,
        content=f"content for {chunk_id}",
        chunk_index=int(chunk_id[1:]) if chunk_id[1:].isdigit() else 0,
        page_number=1,
        section_title=None,
        semantic_score=semantic,
        lexical_score=lexical,
    )


def test_rrf_assigns_citation_ids_in_order() -> None:
    semantic = [_chunk("c1", semantic=0.9), _chunk("c2", semantic=0.8)]
    lexical = [_chunk("c2", lexical=0.7), _chunk("c3", lexical=0.6)]

    fused = reciprocal_rank_fusion(semantic, lexical, top_k=3)

    assert [hit.chunk_id for hit in fused][:3] == ["c2", "c1", "c3"]
    assert [hit.citation_id for hit in fused] == ["C1", "C2", "C3"]


def test_rrf_top_k_clamps_result_length() -> None:
    semantic = [_chunk(f"c{i}", semantic=1.0 - i * 0.1) for i in range(5)]
    lexical = [_chunk(f"c{i}", lexical=1.0 - i * 0.1) for i in range(5)]

    fused = reciprocal_rank_fusion(semantic, lexical, top_k=2)
    assert len(fused) == 2
    assert all(hit.citation_id in {"C1", "C2"} for hit in fused)


def test_rrf_merges_overlapping_chunks_and_keeps_both_scores() -> None:
    semantic = [_chunk("c1", semantic=0.9)]
    lexical = [_chunk("c1", lexical=0.5)]

    fused = reciprocal_rank_fusion(semantic, lexical, top_k=1)
    assert len(fused) == 1
    merged = fused[0]
    assert merged.chunk_id == "c1"
    assert merged.semantic_score == 0.9
    assert merged.lexical_score == 0.5
    assert merged.fusion_score is not None and merged.fusion_score > 0
