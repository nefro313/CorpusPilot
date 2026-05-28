from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from domain.profiles import DomainProfile
from services.retrieval import RetrievedChunk


def build_answer_prompt(
    question: str,
    hits: list[RetrievedChunk],
    profile: DomainProfile | None,
    sql_context: str | None = None,
) -> list[Any]:
    domain_style = profile.answer_style if profile else "Answer only from the retrieved evidence."
    chunks = [
        (
            f"[{hit.citation_id}] file={hit.document_filename}; page={hit.page_number or '-'}; "
            f"section={hit.section_title or '-'}\n{hit.content}"
        )
        for hit in hits
    ]
    if sql_context:
        chunks.insert(0, f"[CSQL] source=structured-tables\n{sql_context}")
    context = "\n\n".join(chunks)
    return [
        SystemMessage(
            content=(
                "You are a domain-specific RAG assistant for a production 'Ask My Docs' system. "
                f"{domain_style} "
                "Only use facts present in the retrieved context. "
                "Every substantive paragraph or bullet must include one or more citation tags like [C1]. "
                "If a structured-tables snippet [CSQL] is present, prefer its precise figures and cite [CSQL]. "
                "If the context is insufficient, say that clearly and do not invent details."
            )
        ),
        HumanMessage(
            content=(
                f"Question:\n{question}\n\nRetrieved context:\n{context}\n\n"
                "Write a concise grounded answer with inline citations."
            )
        ),
    ]


def attach_history(
    prompt_messages: list[Any],
    history: list[dict[str, str]],
    turns: int,
) -> list[Any]:
    if not history:
        return prompt_messages
    history_messages: list[Any] = []
    for turn in history[-turns:]:
        prior_q = turn.get("question", "").strip()
        prior_a = turn.get("answer", "").strip()
        if prior_q:
            history_messages.append(HumanMessage(content=prior_q))
        if prior_a:
            history_messages.append(AIMessage(content=prior_a[:1200]))
    if not history_messages:
        return prompt_messages
    return [prompt_messages[0], *history_messages, prompt_messages[1]]


REWRITE_SYSTEM_PROMPT = (
    "Rewrite the user's latest follow-up into a single self-contained query "
    "suitable for hybrid retrieval over a document corpus. "
    "Resolve pronouns and references using the prior turns. "
    "Keep the rewrite concise and do not invent details that are not in the conversation. "
    "If the latest question is already self-contained, return it unchanged."
)


FOLLOWUP_SYSTEM_PROMPT = (
    "You write concise follow-up questions for a grounded RAG chat UI. "
    "Return exactly three short questions that naturally continue the user's investigation. "
    "Do not repeat the original question. Keep each question answerable from documents."
)


MULTI_QUERY_SYSTEM_PROMPT = (
    "Generate three retrieval-optimized paraphrases of the user's research question. "
    "Each paraphrase should target a different angle (methodology, comparison baseline, "
    "results/metrics, definitions). Keep each paraphrase under 25 words. "
    "Do not include the original question."
)


STEPBACK_SYSTEM_PROMPT = (
    "Given a specific technical question, generate a single broader version "
    "that would retrieve the underlying concepts, configuration, or architecture context. "
    "Keep the step-back question under 25 words. Return only the broader question."
)


SQL_CLASSIFY_SYSTEM_PROMPT = (
    "Decide whether the user question is best answered by querying structured tables "
    "extracted from a financial document (numerical line items, metrics, periods, "
    "financial figures) or by reading prose. Reply with one token: structured or prose."
)


SQL_GENERATE_SYSTEM_PROMPT = (
    "You write a single SQLite SELECT statement against this schema:\n"
    "  document_table_rows(document_id TEXT, table_index INTEGER, row_index INTEGER, "
    "column_name TEXT, cell_value TEXT)\n"
    "Each table cell is one row. Match column_name and cell_value with case-insensitive "
    "LIKE patterns. Always SELECT document_id, table_index, row_index, column_name, "
    "cell_value. Limit results to 50 rows. Return only the SQL — no commentary."
)

RETRIEVAL_GRADE_SYSTEM_PROMPT = (
    "You are a strict retrieval quality judge for a RAG system. "
    "Given a user question and a set of retrieved document chunks, decide whether the chunks "
    "contain sufficient grounded evidence to answer the question. "
    "Be strict: partial matches, tangentially related text, or generic background without "
    "direct relevance to the question all count as NOT relevant. "
    "Return relevant=true only if at least one chunk directly addresses the question with "
    "specific facts, figures, or statements the answer can cite. "
    "Also return a brief reason (≤ 20 words) explaining your decision."
)
