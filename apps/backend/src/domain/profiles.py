from dataclasses import dataclass
from enum import StrEnum


class CorpusDomain(StrEnum):
    TECHNICAL_DOCUMENT = "technical_document"
    RESEARCH_PAPER = "research_paper"
    LEGAL_CONTRACT = "legal_contract"
    HEALTHCARE_DOCUMENT = "healthcare_document"
    FINANCIAL_DOCUMENT = "financial_document"


@dataclass(frozen=True)
class DomainProfile:
    value: CorpusDomain
    label: str
    description: str
    chunk_size: int
    chunk_overlap: int
    separators: tuple[str, ...]
    retrieval_k: int
    rerank_k: int
    answer_style: str
    chunking_strategy: str
    retrieval_strategy: str


DOMAIN_PROFILES: dict[CorpusDomain, DomainProfile] = {
    CorpusDomain.TECHNICAL_DOCUMENT: DomainProfile(
        value=CorpusDomain.TECHNICAL_DOCUMENT,
        label="Technical Document",
        description="API docs, runbooks, architecture notes, product specs.",
        chunk_size=1100,
        chunk_overlap=180,
        separators=("\n### ", "\n## ", "\n# ", "\n\n", "\n", ". ", " "),
        retrieval_k=8,
        rerank_k=5,
        answer_style="Prefer implementation details, constraints, steps, and cited factual guidance.",
        chunking_strategy="Heading-aware recursive chunks with emphasis on code-adjacent paragraphs.",
        retrieval_strategy="Hybrid vector + BM25 with section-preserving rerank.",
    ),
    CorpusDomain.RESEARCH_PAPER: DomainProfile(
        value=CorpusDomain.RESEARCH_PAPER,
        label="Research Paper",
        description="Papers, whitepapers, benchmark reports, experiment summaries.",
        chunk_size=1300,
        chunk_overlap=220,
        separators=(
            "\nAbstract",
            "\nIntroduction",
            "\nMethods",
            "\nResults",
            "\nConclusion",
            "\n\n",
            "\n",
            ". ",
        ),
        retrieval_k=8,
        rerank_k=5,
        answer_style="Focus on claims, methodology, datasets, metrics, and limitations.",
        chunking_strategy="Section-aware chunks tuned for abstract, methods, results, and conclusion blocks.",
        retrieval_strategy="Hybrid retrieval with claim-focused rerank.",
    ),
    CorpusDomain.LEGAL_CONTRACT: DomainProfile(
        value=CorpusDomain.LEGAL_CONTRACT,
        label="Legal Contract",
        description="Contracts, agreements, NDAs, policies, clauses, annexes.",
        chunk_size=900,
        chunk_overlap=100,
        separators=(
            "\nSection ",
            "\nSECTION ",
            "\nArticle ",
            "\nARTICLE ",
            "\n\n",
            "\n",
            "; ",
            ". ",
        ),
        retrieval_k=10,
        rerank_k=6,
        answer_style="Be precise. Quote obligations, dates, parties, and clause relationships with citations only.",
        chunking_strategy="Clause-first segmentation with conservative overlap to keep legal boundaries intact.",
        retrieval_strategy="Hybrid retrieval optimized for clause numbering and lexical precision.",
    ),
    CorpusDomain.HEALTHCARE_DOCUMENT: DomainProfile(
        value=CorpusDomain.HEALTHCARE_DOCUMENT,
        label="Healthcare Document",
        description="Clinical notes, discharge summaries, care plans, protocols, medical guidance.",
        chunk_size=850,
        chunk_overlap=120,
        separators=("\nASSESSMENT", "\nPLAN", "\nHISTORY", "\nMEDICATION", "\n\n", "\n", ". "),
        retrieval_k=8,
        rerank_k=5,
        answer_style="Stay evidence-bound. Summarize findings from the uploaded material without adding medical advice.",
        chunking_strategy="Section-aware sentence-preserving chunks for short factual retrieval.",
        retrieval_strategy="Hybrid retrieval with safety-first grounding checks.",
    ),
    CorpusDomain.FINANCIAL_DOCUMENT: DomainProfile(
        value=CorpusDomain.FINANCIAL_DOCUMENT,
        label="Financial Document",
        description="10-K / 10-Q filings, annual reports, earnings releases, investor decks, financial statements.",
        chunk_size=950,
        chunk_overlap=160,
        separators=(
            "\nItem ",
            "\nITEM ",
            "\nPart ",
            "\nPART ",
            "\nNote ",
            "\nNOTE ",
            "\nBalance Sheet",
            "\nIncome Statement",
            "\nStatements of Operations",
            "\nCash Flow",
            "\nRisk Factors",
            "\nManagement's Discussion",
            "\n\n",
            "\n",
            ". ",
            " ",
        ),
        retrieval_k=10,
        rerank_k=6,
        answer_style=(
            "Quote figures, currencies, periods, and units precisely. "
            "Distinguish GAAP vs non-GAAP if the source does, and never extrapolate beyond the cited evidence."
        ),
        chunking_strategy=(
            "Statement- and Item-aware chunks tuned to keep line items, footnotes, and MD&A paragraphs "
            "intact with conservative overlap to preserve numerical context."
        ),
        retrieval_strategy=(
            "Hybrid retrieval weighted toward lexical precision on numerals, "
            "named line items, and item/note identifiers."
        ),
    ),
}


def get_domain_profile(domain: CorpusDomain) -> DomainProfile:
    return DOMAIN_PROFILES[domain]


def list_domain_profiles() -> list[DomainProfile]:
    return [DOMAIN_PROFILES[domain] for domain in CorpusDomain]
