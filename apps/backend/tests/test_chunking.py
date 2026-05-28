from domain.profiles import CorpusDomain
from services.ingestion.chunking import chunk_units, split_into_sections


def test_split_into_sections_returns_whole_text_when_no_match() -> None:
    sections = split_into_sections(
        "Just plain prose, no headings.", CorpusDomain.TECHNICAL_DOCUMENT
    )
    assert sections == [(None, "Just plain prose, no headings.")]


def test_split_into_sections_returns_empty_marker_for_empty_input() -> None:
    sections = split_into_sections("", CorpusDomain.TECHNICAL_DOCUMENT)
    assert sections == [(None, "")]


def test_split_into_sections_picks_up_research_paper_headings() -> None:
    text = "Abstract\nAbstract body.\nMethods\nWe ran experiments.\nResults\nNumbers."
    sections = split_into_sections(text, CorpusDomain.RESEARCH_PAPER)
    headings = [heading for heading, _body in sections]
    assert "Abstract" in headings
    assert any(h.lower() == "methods" for h in headings)
    assert any(h.lower() == "results" for h in headings)


def test_chunk_units_produces_indexed_chunks_with_metadata() -> None:
    units = [
        {
            "text": ("## Overview\n" + "This is a technical document about the system. " * 30),
            "page_number": 1,
        }
    ]
    parents, chunks, content = chunk_units(units, CorpusDomain.TECHNICAL_DOCUMENT)
    assert parents == [], "technical_document does not use parent-child chunking"
    assert chunks, "expected non-empty chunks"
    assert content
    assert chunks[0].chunk_index == 0
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
    for c in chunks:
        assert c.metadata_json["domain"] == CorpusDomain.TECHNICAL_DOCUMENT.value
        assert c.token_count > 0
