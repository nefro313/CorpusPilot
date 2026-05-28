import logging
import re
import time
import uuid

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from storage.models import DocumentChunk, DocumentTableRow

from core.config import get_settings
from core.metrics import (
    AGENTIC_RETRIES_TOTAL,
    PARENT_HYDRATIONS_TOTAL,
    RAG_NODE_LATENCY_SECONDS,
    RETRIEVAL_GRADE_OUTCOMES,
    SQL_RAG_ATTEMPTS_TOTAL,
)
from domain.profiles import CorpusDomain, DomainProfile, get_domain_profile
from services.llm import get_answer_llm, get_guard_llm, get_reranker, get_rewrite_llm
from services.rag.memory import HISTORY_TURNS_FOR_PROMPT
from services.rag.prompts import (
    MULTI_QUERY_SYSTEM_PROMPT,
    RETRIEVAL_GRADE_SYSTEM_PROMPT,
    REWRITE_SYSTEM_PROMPT,
    SQL_CLASSIFY_SYSTEM_PROMPT,
    SQL_GENERATE_SYSTEM_PROMPT,
    STEPBACK_SYSTEM_PROMPT,
    attach_history,
    build_answer_prompt,
)
from services.rag.state import RAGState
from services.rag.telemetry import estimate_cost, extract_usage
from services.retrieval import HybridRetrievalResult, RetrievedChunk, hybrid_search
from services.retrieval.fusion import reciprocal_rank_fusion

settings = get_settings()
logger = logging.getLogger(__name__)

_citation_pattern = re.compile(r"\[(C\d+|CSQL)\]")

_MAX_RETRIES = 2


class RewrittenQuery(BaseModel):
    query: str = Field(default="", max_length=600)


def _profile_from_state(domain_value: str | None) -> DomainProfile | None:
    if not domain_value:
        return None
    return get_domain_profile(CorpusDomain(domain_value))


async def rewrite_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        history = state.get("history") or []
        question = state["question"]
        if not history:
            return {"rewritten_question": question}
        if not settings.openai_api_key:
            logger.info("rewrite skipped: no OpenAI key configured")
            return {"rewritten_question": question}
        try:
            recent = history[-HISTORY_TURNS_FOR_PROMPT:]
            transcript = "\n".join(
                f"User: {turn['question']}\nAssistant: {turn['answer'][:600]}" for turn in recent
            )
            structured_llm = get_rewrite_llm().with_structured_output(RewrittenQuery)
            decision = await structured_llm.ainvoke(
                [
                    SystemMessage(content=REWRITE_SYSTEM_PROMPT),
                    HumanMessage(
                        content=f"Prior turns:\n{transcript}\n\nLatest user question:\n{question}"
                    ),
                ]
            )
            rewritten = (decision.query or "").strip()
            if rewritten and rewritten != question:
                logger.info(
                    "rewrite ok: %d prior turns -> standalone query (orig=%d chars, new=%d chars)",
                    len(recent),
                    len(question),
                    len(rewritten),
                )
                return {"rewritten_question": rewritten}
            return {"rewritten_question": question}
        except Exception as exc:
            logger.warning(
                "rewrite failed (%s: %s); using original question",
                type(exc).__name__,
                exc,
            )
            return {"rewritten_question": question}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="rewrite").observe(
            time.monotonic() - _t
        )


class QueryVariants(BaseModel):
    queries: list[str] = Field(default_factory=list)


class StepBackQuery(BaseModel):
    query: str = Field(default="", max_length=400)


_SAFE_SQL_PATTERN = re.compile(
    r"^\s*select\b[\s\S]+?from\s+document_table_rows\b[\s\S]*$",
    re.IGNORECASE,
)
_SQL_FORBIDDEN = re.compile(
    r";|--|\b(insert|update|delete|drop|alter|create|grant|truncate|copy|attach)\b",
    re.IGNORECASE,
)


class StructuredVerdict(BaseModel):
    verdict: str = Field(default="prose", max_length=12)


class GeneratedSQL(BaseModel):
    sql: str = Field(default="", max_length=2000)


def _is_safe_select(sql: str) -> bool:
    if not sql or not _SAFE_SQL_PATTERN.match(sql):
        return False
    if _SQL_FORBIDDEN.search(sql):
        return False
    return True


async def sql_table_node(db: AsyncSession, state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        if state.get("domain") != CorpusDomain.FINANCIAL_DOCUMENT.value:
            return {}
        if not settings.openai_api_key:
            return {}

        from storage.models import Document as DocModel
        user_id = state.get("user_id") or ""
        has_tables = await db.scalar(
            select(DocumentTableRow.id)
            .join(DocModel, DocModel.id == DocumentTableRow.document_id)
            .where(DocModel.user_id == user_id)
            .limit(1)
        )
        if not has_tables:
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="no_tables").inc()
            return {}

        base_query = state.get("rewritten_question") or state["question"]
        try:
            classifier = get_rewrite_llm().with_structured_output(StructuredVerdict)
            verdict = await classifier.ainvoke(
                [
                    SystemMessage(content=SQL_CLASSIFY_SYSTEM_PROMPT),
                    HumanMessage(content=f"Question:\n{base_query}"),
                ]
            )
            if (verdict.verdict or "").strip().lower() != "structured":
                SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="prose").inc()
                return {}
        except Exception as exc:
            logger.warning("sql classify failed (%s: %s)", type(exc).__name__, exc)
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="error").inc()
            return {}

        try:
            generator = get_rewrite_llm().with_structured_output(GeneratedSQL)
            generated = await generator.ainvoke(
                [
                    SystemMessage(content=SQL_GENERATE_SYSTEM_PROMPT),
                    HumanMessage(content=f"Question:\n{base_query}"),
                ]
            )
            sql = (generated.sql or "").strip().rstrip(";")
        except Exception as exc:
            logger.warning("sql generation failed (%s: %s)", type(exc).__name__, exc)
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="error").inc()
            return {}

        if not _is_safe_select(sql):
            logger.info("sql rejected by safety filter; skipping table answer")
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="safety_rejected").inc()
            return {}

        try:
            # Wrap in a subquery that restricts to the requesting user's documents
            scoped_sql = (
                "SELECT _q.* FROM (" + sql + ") _q"
                " WHERE _q.document_id IN"
                " (SELECT id FROM documents WHERE user_id = :_uid)"
            )
            rows = (await db.execute(text(scoped_sql), {"_uid": user_id})).mappings().all()
        except Exception as exc:
            logger.warning("sql execution failed (%s: %s)", type(exc).__name__, exc)
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="error").inc()
            return {}

        if not rows:
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="no_rows").inc()
            return {}

        lines = []
        for row in rows[:50]:
            column = row.get("column_name")
            value = row.get("cell_value")
            page = row.get("page_number")
            page_str = f" (p.{page})" if page else ""
            if column is not None and value is not None:
                lines.append(f"- {column}: {value}{page_str}")
        if not lines:
            SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="no_rows").inc()
            return {}

        sql_context = (
            "Structured table query result (queried directly against parsed tables):\n"
            + "\n".join(lines)
        )
        logger.info("sql table query returned %d rows; injecting as [CSQL] context", len(rows))
        SQL_RAG_ATTEMPTS_TOTAL.labels(outcome="structured").inc()
        return {"sql_context": sql_context}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="sql_tables").observe(
            time.monotonic() - _t
        )


async def expand_query_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        domain_value = state.get("domain")
        base_query = state.get("rewritten_question") or state["question"]
        variants: list[str] = []
        is_retry = bool(state.get("needs_broader_query"))

        if not settings.openai_api_key:
            return {"query_variants": variants, "needs_broader_query": False}

        if is_retry:
            retry_count = state.get("retry_count") or 0
            logger.info(
                "expand_query RETRY pass (attempt %d): forcing step-back broadening for domain=%s",
                retry_count,
                domain,
            )
            try:
                structured_llm = get_rewrite_llm().with_structured_output(StepBackQuery)
                decision = await structured_llm.ainvoke(
                    [
                        SystemMessage(content=STEPBACK_SYSTEM_PROMPT),
                        HumanMessage(content=f"Question:\n{base_query}"),
                    ]
                )
                stepback = (decision.query or "").strip()
                if stepback and stepback != base_query:
                    variants = [stepback]
                    logger.info("retry step-back produced broader query: %r", stepback)
            except Exception as exc:
                logger.warning(
                    "retry step-back expansion failed (%s: %s); proceeding with base query",
                    type(exc).__name__,
                    exc,
                )
            return {"query_variants": variants, "needs_broader_query": False}

        if not domain_value:
            return {"query_variants": variants}

        try:
            if domain_value == CorpusDomain.RESEARCH_PAPER.value:
                structured_llm = get_rewrite_llm().with_structured_output(QueryVariants)
                decision = await structured_llm.ainvoke(
                    [
                        SystemMessage(content=MULTI_QUERY_SYSTEM_PROMPT),
                        HumanMessage(content=f"Question:\n{base_query}"),
                    ]
                )
                variants = [
                    q.strip()
                    for q in (decision.queries or [])
                    if q and q.strip() and q.strip() != base_query
                ][:3]
                logger.info("multi-query expansion produced %d variants", len(variants))
            elif domain_value == CorpusDomain.TECHNICAL_DOCUMENT.value:
                structured_llm = get_rewrite_llm().with_structured_output(StepBackQuery)
                decision = await structured_llm.ainvoke(
                    [
                        SystemMessage(content=STEPBACK_SYSTEM_PROMPT),
                        HumanMessage(content=f"Question:\n{base_query}"),
                    ]
                )
                stepback = (decision.query or "").strip()
                if stepback and stepback != base_query:
                    variants = [stepback]
                    logger.info("step-back expansion produced broader query")
        except Exception as exc:
            logger.warning(
                "query expansion failed (%s: %s); proceeding with base query only",
                type(exc).__name__,
                exc,
            )

        return {"query_variants": variants}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="expand_query").observe(
            time.monotonic() - _t
        )


async def retrieve_node(db: AsyncSession, state: RAGState) -> RAGState:  # noqa: C901
    _t = time.monotonic()
    domain_label = state.get("domain") or "all"
    try:
        profile = _profile_from_state(state.get("domain"))
        domain = CorpusDomain(state["domain"]) if state.get("domain") else None
        base_query = state.get("rewritten_question") or state["question"]
        variants = state.get("query_variants") or []
        queries = [base_query, *variants]

        user_id = state.get("user_id") or ""
        if len(queries) == 1:
            retrieval = await hybrid_search(
                db=db,
                query=base_query,
                domain=domain,
                profile=profile,
                top_k=state.get("top_k"),
                user_id=user_id,
            )
            return {"retrieval": retrieval}

        # Variants must run sequentially: hybrid_search calls lexical_search,
        # which executes SQL on the shared AsyncSession. AsyncSession is NOT
        # concurrency-safe — running variants in parallel triggers
        # IllegalStateChangeError. The BM25 retriever is cached after the first
        # call, so subsequent variants are essentially "free" on the lexical
        # side; only the semantic Milvus round-trip is repeated.
        results: list[HybridRetrievalResult] = []
        for q in queries:
            results.append(
                await hybrid_search(
                    db=db,
                    query=q,
                    domain=domain,
                    profile=profile,
                    top_k=state.get("top_k"),
                    user_id=user_id,
                )
            )

        semantic_dedup: dict[str, RetrievedChunk] = {}
        lexical_dedup: dict[str, RetrievedChunk] = {}
        for retrieval in results:
            for hit in retrieval.semantic_hits:
                existing = semantic_dedup.get(hit.chunk_id)
                if existing is None or (hit.semantic_score or 0.0) > (existing.semantic_score or 0.0):
                    semantic_dedup[hit.chunk_id] = hit
            for hit in retrieval.lexical_hits:
                existing = lexical_dedup.get(hit.chunk_id)
                if existing is None or (hit.lexical_score or 0.0) > (existing.lexical_score or 0.0):
                    lexical_dedup[hit.chunk_id] = hit

        semantic_merged = sorted(
            semantic_dedup.values(),
            key=lambda h: h.semantic_score or 0.0,
            reverse=True,
        )
        lexical_merged = sorted(
            lexical_dedup.values(),
            key=lambda h: h.lexical_score or 0.0,
            reverse=True,
        )
        fusion_k = (state.get("top_k") or profile.retrieval_k) if profile else settings.retrieval_fusion_k
        fused_hits = reciprocal_rank_fusion(
            semantic_merged, lexical_merged, fusion_k, domain=domain
        )
        merged = HybridRetrievalResult(
            semantic_hits=semantic_merged,
            lexical_hits=lexical_merged,
            fused_hits=fused_hits,
        )
        logger.info(
            "merged retrieval across %d query variants -> sem=%d lex=%d fused=%d",
            len(queries),
            len(semantic_merged),
            len(lexical_merged),
            len(fused_hits),
        )
        return {"retrieval": merged}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain_label, node="retrieve").observe(
            time.monotonic() - _t
        )


async def rerank_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        candidates = state["retrieval"].fused_hits
        if not candidates:
            logger.info("rerank skipped: no candidates from retrieval")
            return {"reranked_hits": []}
        try:
            docs = [
                Document(page_content=hit.content, metadata={"_idx": idx})
                for idx, hit in enumerate(candidates)
            ]
            reranked = await get_reranker().acompress_documents(
                documents=docs,
                query=state["question"],
            )
            ordered: list[RetrievedChunk] = []
            for doc in reranked:
                hit = candidates[doc.metadata["_idx"]]
                hit.rerank_score = round(float(doc.metadata.get("relevance_score", 0.0)), 6)
                ordered.append(hit)
            logger.info(
                "rerank ok: provider=cohere model=%s candidates=%d reranked=%d",
                settings.cohere_rerank_model,
                len(candidates),
                len(ordered),
            )
            return {"reranked_hits": ordered}
        except Exception as exc:
            logger.warning(
                "rerank fallback: cohere call failed (%s: %s); using fusion_score for %d candidates",
                type(exc).__name__,
                exc,
                len(candidates),
            )
            for hit in candidates:
                hit.rerank_score = hit.fusion_score
            return {"reranked_hits": candidates}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="rerank").observe(
            time.monotonic() - _t
        )


async def hydrate_parents_node(db: AsyncSession, state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        hits = state.get("reranked_hits") or []
        if not hits:
            PARENT_HYDRATIONS_TOTAL.labels(domain=domain, outcome="skipped").inc()
            return {}

        chunk_ids: list[uuid.UUID] = []
        for hit in hits:
            try:
                chunk_ids.append(uuid.UUID(hit.chunk_id))
            except (ValueError, TypeError):
                continue
        if not chunk_ids:
            PARENT_HYDRATIONS_TOTAL.labels(domain=domain, outcome="skipped").inc()
            return {}

        rows = (
            await db.execute(
                select(DocumentChunk.id, DocumentChunk.parent_chunk_id).where(
                    DocumentChunk.id.in_(chunk_ids)
                )
            )
        ).all()
        parent_lookup: dict[str, str] = {
            str(row.id): str(row.parent_chunk_id) for row in rows if row.parent_chunk_id is not None
        }
        if not parent_lookup:
            PARENT_HYDRATIONS_TOTAL.labels(domain=domain, outcome="no_parent").inc(len(hits))
            return {}

        parent_uuids = list({uuid.UUID(pid) for pid in parent_lookup.values()})
        parent_rows = (
            await db.execute(
                select(DocumentChunk.id, DocumentChunk.content).where(
                    DocumentChunk.id.in_(parent_uuids)
                )
            )
        ).all()
        parent_content: dict[str, str] = {str(row.id): row.content for row in parent_rows}

        swapped = 0
        for hit in hits:
            parent_id = parent_lookup.get(hit.chunk_id)
            if not parent_id:
                PARENT_HYDRATIONS_TOTAL.labels(domain=domain, outcome="no_parent").inc()
                continue
            content = parent_content.get(parent_id)
            if content:
                hit.content = content
                swapped += 1
                PARENT_HYDRATIONS_TOTAL.labels(domain=domain, outcome="swapped").inc()
            else:
                PARENT_HYDRATIONS_TOTAL.labels(domain=domain, outcome="no_parent").inc()
        if swapped:
            logger.info("hydrated %d/%d hits with parent-section text", swapped, len(hits))
        return {"reranked_hits": hits}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="hydrate_parents").observe(
            time.monotonic() - _t
        )


class RelevanceVerdict(BaseModel):
    relevant: bool = Field(default=False)
    reason: str = Field(default="", max_length=200)


async def grade_retrieval_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        hits = state.get("reranked_hits") or []
        retry_count = state.get("retry_count") or 0

        if not hits:
            RETRIEVAL_GRADE_OUTCOMES.labels(domain=domain, outcome="skipped").inc()
            return {}

        if not settings.openai_api_key or retry_count >= _MAX_RETRIES:
            RETRIEVAL_GRADE_OUTCOMES.labels(domain=domain, outcome="skipped").inc()
            return {}

        question = state.get("rewritten_question") or state["question"]
        snippet = "\n\n".join(
            f"[{h.citation_id}] {h.content[:400]}"
            for h in hits[:4]
            if h.citation_id
        )

        try:
            grader = get_rewrite_llm().with_structured_output(RelevanceVerdict)
            verdict = await grader.ainvoke(
                [
                    SystemMessage(content=RETRIEVAL_GRADE_SYSTEM_PROMPT),
                    HumanMessage(
                        content=(
                            f"Question:\n{question}\n\n"
                            f"Retrieved chunks:\n{snippet}\n\n"
                            "Are these chunks sufficient to answer the question?"
                        )
                    ),
                ]
            )
            reason = (verdict.reason or "").strip()

            if not verdict.relevant:
                logger.info(
                    "grade_retrieval: chunks NOT relevant (attempt %d/%d) — reason: %s",
                    retry_count + 1,
                    _MAX_RETRIES,
                    reason,
                )
                RETRIEVAL_GRADE_OUTCOMES.labels(domain=domain, outcome="not_relevant").inc()
                AGENTIC_RETRIES_TOTAL.labels(domain=domain, trigger="grade_retrieval").inc()
                return {
                    "needs_broader_query": True,
                    "retry_count": retry_count + 1,
                    "retrieval_grade_reason": reason,
                }

            logger.info("grade_retrieval: chunks relevant — reason: %s", reason)
            RETRIEVAL_GRADE_OUTCOMES.labels(domain=domain, outcome="relevant").inc()
            return {"retrieval_grade_reason": reason}

        except Exception as exc:
            logger.warning(
                "grade_retrieval failed (%s: %s); proceeding to generate",
                type(exc).__name__,
                exc,
            )
            RETRIEVAL_GRADE_OUTCOMES.labels(domain=domain, outcome="skipped").inc()
            return {}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="grade_retrieval").observe(
            time.monotonic() - _t
        )


async def generate_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        profile = _profile_from_state(state.get("domain"))
        hits = state.get("reranked_hits") or []
        sql_context = state.get("sql_context")
        if not hits and not sql_context:
            return {
                "answer": "I could not find enough grounded evidence in the uploaded corpus to answer this question.",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
            }

        top_hits = hits[: (5 if profile is None else profile.rerank_k)]
        prompt_messages = build_answer_prompt(
            state["question"], top_hits, profile, sql_context=sql_context
        )
        prompt_messages = attach_history(
            prompt_messages, state.get("history") or [], HISTORY_TURNS_FOR_PROMPT
        )
        response = await get_answer_llm().ainvoke(
            prompt_messages,
            config={
                "run_name": "generate_grounded_answer",
                "tags": ["answer", state.get("domain") or "all-domains"],
                "metadata": {"pipeline": "hybrid-rag"},
            },
        )
        prompt_tokens, completion_tokens, total_tokens = extract_usage(response)
        return {
            "answer": str(response.content),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimate_cost(prompt_tokens, completion_tokens),
        }
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="generate").observe(
            time.monotonic() - _t
        )


async def validate_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        answer = state.get("answer", "").strip()
        hits = state.get("reranked_hits") or []
        sql_context = state.get("sql_context")
        valid_ids = {hit.citation_id for hit in hits if hit.citation_id}
        if sql_context:
            valid_ids.add("CSQL")
        cited_ids = [match for match in _citation_pattern.findall(answer) if match in valid_ids]
        citation_valid = bool(cited_ids)
        retry_count = state.get("retry_count") or 0

        if (hits or sql_context) and not citation_valid and retry_count < _MAX_RETRIES:
            logger.info(
                "validate_node: no valid citations (attempt %d/%d) — triggering retrieval retry",
                retry_count + 1,
                _MAX_RETRIES,
            )
            AGENTIC_RETRIES_TOTAL.labels(domain=domain, trigger="validate_citation").inc()
            return {
                "answer": answer,
                "citations": [],
                "citation_valid": False,
                "grounded": False,
                "retry_count": retry_count + 1,
                "needs_broader_query": True,
            }

        if (hits or sql_context) and not citation_valid:
            logger.info(
                "validate_node: no valid citations after %d retries — returning fallback",
                retry_count,
            )
            answer = (
                "I could not produce a citation-valid answer from the retrieved context "
                f"after {retry_count} retrieval attempt(s). "
                "Try rephrasing your question or uploading more relevant documents."
            )

        return {
            "answer": answer,
            "citations": sorted(set(cited_ids)),
            "citation_valid": citation_valid,
            "grounded": citation_valid,
            "needs_broader_query": False,
        }
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="validate").observe(
            time.monotonic() - _t
        )


_HEALTHCARE_GUARD_PROMPT = (
    "You are a clinical safety reviewer. The assistant produced an answer "
    "from retrieved healthcare documents. Decide if the answer makes any "
    "medical recommendations, diagnoses, or treatment guidance that are NOT "
    "directly supported by quoted text in the retrieved context. "
    "Reply with exactly one token: safe or unsafe."
)

_HEALTHCARE_SAFETY_NOTICE = (
    "\n\n⚠️ Review: this answer may contain content beyond the uploaded document."
)


class SafetyVerdict(BaseModel):
    verdict: str = Field(default="safe", max_length=10)


async def safety_validate_node(state: RAGState) -> RAGState:
    _t = time.monotonic()
    domain = state.get("domain") or "all"
    try:
        if state.get("domain") != CorpusDomain.HEALTHCARE_DOCUMENT.value:
            return {}
        answer = (state.get("answer") or "").strip()
        hits = state.get("reranked_hits") or []
        if not answer or not hits:
            return {}
        if not settings.openai_api_key:
            return {}
        try:
            context = "\n\n".join(
                f"[{hit.citation_id}] {hit.content}" for hit in hits if hit.citation_id
            )
            structured_llm = get_guard_llm().with_structured_output(SafetyVerdict)
            decision = await structured_llm.ainvoke(
                [
                    SystemMessage(content=_HEALTHCARE_GUARD_PROMPT),
                    HumanMessage(
                        content=(
                            f"Retrieved context:\n{context}\n\n"
                            f"Assistant answer:\n{answer}\n\n"
                            "Respond with safe or unsafe."
                        )
                    ),
                ]
            )
            verdict = (decision.verdict or "safe").strip().lower()
            if verdict == "unsafe" and not answer.endswith(_HEALTHCARE_SAFETY_NOTICE.strip()):
                logger.info("healthcare safety guard flagged answer as unsafe; appending notice")
                return {"answer": answer + _HEALTHCARE_SAFETY_NOTICE, "grounded": False}
            return {}
        except Exception as exc:
            logger.warning(
                "healthcare safety guard failed (%s: %s); leaving answer unchanged",
                type(exc).__name__,
                exc,
            )
            return {}
    finally:
        RAG_NODE_LATENCY_SECONDS.labels(domain=domain, node="safety_validate").observe(
            time.monotonic() - _t
        )


__all__ = [
    "expand_query_node",
    "generate_node",
    "grade_retrieval_node",
    "hydrate_parents_node",
    "rerank_node",
    "retrieve_node",
    "rewrite_node",
    "safety_validate_node",
    "sql_table_node",
    "validate_node",
]
