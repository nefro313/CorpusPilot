import logging

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from core.config import get_settings
from domain.profiles import CorpusDomain
from services.llm import get_followup_llm
from services.rag.prompts import FOLLOWUP_SYSTEM_PROMPT
from services.retrieval import RetrievedChunk

settings = get_settings()
logger = logging.getLogger(__name__)


class FollowUpQuestions(BaseModel):
    questions: list[str] = Field(default_factory=list, max_length=3)


_FALLBACKS: dict[CorpusDomain, list[str]] = {
    CorpusDomain.TECHNICAL_DOCUMENT: [
        "Which implementation details are most important to review next?",
        "What constraints or prerequisites are explicitly documented?",
        "Which cited sections should I compare side by side?",
    ],
    CorpusDomain.RESEARCH_PAPER: [
        "Which result or metric deserves a closer look next?",
        "What limitations or assumptions are stated in the cited sections?",
        "Which experiment setup details are still missing?",
    ],
    CorpusDomain.LEGAL_CONTRACT: [
        "Which obligation or deadline should I review next?",
        "What termination or renewal language is supported by the cited clauses?",
        "Which payment or liability terms need a closer comparison?",
    ],
    CorpusDomain.HEALTHCARE_DOCUMENT: [
        "Which documented finding or plan item should I inspect next?",
        "What follow-up steps are explicitly supported by the record?",
        "Which medication, diagnosis, or assessment details are cited?",
    ],
    CorpusDomain.FINANCIAL_DOCUMENT: [
        "Which line item or period deserves a closer comparison?",
        "What risk factors or MD&A points are explicitly cited?",
        "Which footnote or non-GAAP reconciliation should I review next?",
    ],
}

_GENERIC_FALLBACK = [
    "Which cited source should I inspect next?",
    "What detail is still missing from the current answer?",
    "Which follow-up question would narrow the search best?",
]


def fallback_questions(domain: CorpusDomain | None) -> list[str]:
    if domain is None:
        return list(_GENERIC_FALLBACK)
    return list(_FALLBACKS[domain])


async def generate_follow_up_questions(
    question: str,
    answer: str,
    hits: list[RetrievedChunk],
    domain: CorpusDomain | None,
) -> list[str]:
    if not answer.strip():
        return fallback_questions(domain)
    if not settings.openai_api_key:
        return fallback_questions(domain)

    source_summary = "\n".join(
        f"- {hit.document_filename} | page={hit.page_number or '-'} | section={hit.section_title or '-'}"
        for hit in hits[:3]
    )
    try:
        structured_llm = get_followup_llm().with_structured_output(FollowUpQuestions)
        response = await structured_llm.ainvoke(
            [
                SystemMessage(content=FOLLOWUP_SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        f"User question:\n{question}\n\n"
                        f"Answer:\n{answer}\n\n"
                        f"Likely supporting sources:\n{source_summary}\n\n"
                        f"Active domain: {(domain.value if domain else 'mixed_corpus')}"
                    )
                ),
            ]
        )
        cleaned = [item.strip() for item in response.questions if item.strip()]
        return cleaned[:3] or fallback_questions(domain)
    except Exception as exc:
        logger.warning("follow-up generation failed (%s); using fallback", exc)
        return fallback_questions(domain)
