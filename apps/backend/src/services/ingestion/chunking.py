import re
from dataclasses import dataclass
from typing import Any

from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from domain.profiles import CorpusDomain, DomainProfile, get_domain_profile
from services.embeddings import estimate_tokens
from services.ingestion.parsing import normalize_text

_SECTION_PATTERNS: dict[CorpusDomain, str] = {
    CorpusDomain.TECHNICAL_DOCUMENT: r"(?mi)^(#{1,3}\s+.+|[A-Z][A-Za-z0-9 /_-]{4,}:)$",
    CorpusDomain.RESEARCH_PAPER: (
        r"(?mi)^(abstract|introduction|background|methods?|methodology|"
        r"results?|discussion|conclusion|references)\s*$"
    ),
    CorpusDomain.LEGAL_CONTRACT: (
        r"(?mi)^((section|article|clause)\s+[A-Z0-9.\-]+.*|\d+(\.\d+)*\s+.+)$"
    ),
    CorpusDomain.HEALTHCARE_DOCUMENT: (
        r"(?mi)^(history|assessment|plan|medications?|allergies|impression|"
        r"diagnosis|follow-up)\s*:?\s*$"
    ),
    CorpusDomain.FINANCIAL_DOCUMENT: (
        r"(?mi)^((item|part)\s+\d+[a-z]?\.?\s+.+|note\s+\d+\b.*|"
        r"(balance sheet|income statement|statements? of operations|"
        r"statements? of cash flows?|cash flow|risk factors|"
        r"management.?s discussion(?: and analysis)?|"
        r"liquidity and capital resources|results of operations).*)$"
    ),
}

# Domains that emit parent-section records alongside child chunks. Parents
# stay in Postgres only (never embedded); retrieval finds the child, then
# hydrates the parent for the LLM prompt.
PARENT_CHILD_DOMAINS: frozenset[CorpusDomain] = frozenset(
    {CorpusDomain.LEGAL_CONTRACT, CorpusDomain.FINANCIAL_DOCUMENT}
)


@dataclass(frozen=True)
class PreparedParent:
    parent_index: int
    content: str
    page_number: int | None
    section_title: str | None
    token_count: int
    metadata_json: dict[str, Any]


@dataclass(frozen=True)
class PreparedChunk:
    chunk_index: int
    content: str
    page_number: int | None
    section_title: str | None
    token_count: int
    metadata_json: dict[str, Any]
    parent_index: int | None = None


def split_into_sections(text: str, domain: CorpusDomain) -> list[tuple[str | None, str]]:
    if not text:
        return [(None, "")]

    matcher = re.compile(_SECTION_PATTERNS[domain])
    matches = list(matcher.finditer(text))
    if not matches:
        return [(None, text)]

    sections: list[tuple[str | None, str]] = []
    for idx, match in enumerate(matches):
        heading = match.group(0).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            sections.append((heading, body))
    return sections or [(None, text)]


def build_splitter(profile: DomainProfile) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=profile.chunk_size,
        chunk_overlap=profile.chunk_overlap,
        separators=list(profile.separators),
        keep_separator=True,
    )


def chunk_units(
    units: list[dict[str, Any]], domain: CorpusDomain
) -> tuple[list[PreparedParent], list[PreparedChunk], str]:
    profile = get_domain_profile(domain)
    splitter = build_splitter(profile)
    parents: list[PreparedParent] = []
    chunks: list[PreparedChunk] = []
    full_text_parts: list[str] = []
    chunk_index = 0
    use_parents = domain in PARENT_CHILD_DOMAINS

    for unit in units:
        unit_text = unit["text"]
        if not unit_text:
            continue
        full_text_parts.append(unit_text)
        sections = split_into_sections(unit_text, domain)
        for section_title, section_body in sections:
            parent_index: int | None = None
            if use_parents:
                normalized_parent = normalize_text(section_body)
                if normalized_parent:
                    parent_index = len(parents)
                    parents.append(
                        PreparedParent(
                            parent_index=parent_index,
                            content=normalized_parent,
                            page_number=unit["page_number"],
                            section_title=section_title,
                            token_count=estimate_tokens(normalized_parent),
                            metadata_json={
                                "domain": domain.value,
                                "page_number": unit["page_number"],
                                "section_title": section_title,
                                "is_parent": True,
                            },
                        )
                    )
            base_doc = LCDocument(
                page_content=section_body,
                metadata={
                    "page_number": unit["page_number"],
                    "section_title": section_title,
                    "domain": domain.value,
                },
            )
            for piece in splitter.split_documents([base_doc]):
                content = normalize_text(piece.page_content)
                if not content:
                    continue
                chunks.append(
                    PreparedChunk(
                        chunk_index=chunk_index,
                        content=content,
                        page_number=piece.metadata.get("page_number"),
                        section_title=piece.metadata.get("section_title"),
                        token_count=estimate_tokens(content),
                        metadata_json={
                            "domain": domain.value,
                            "page_number": piece.metadata.get("page_number"),
                            "section_title": piece.metadata.get("section_title"),
                        },
                        parent_index=parent_index,
                    )
                )
                chunk_index += 1

    return parents, chunks, "\n\n".join(full_text_parts).strip()
