from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

RAG_REQUESTS_TOTAL = Counter(
    "rag_requests_total",
    "Number of /api/chat requests, grouped by domain, citation validity, and grounded flag.",
    labelnames=("domain", "citation_valid", "grounded"),
)

RAG_REQUEST_LATENCY_SECONDS = Histogram(
    "rag_request_latency_seconds",
    "Wall-clock latency of the full RAG pipeline.",
    labelnames=("domain",),
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0),
)

RAG_NODE_LATENCY_SECONDS = Histogram(
    "rag_node_latency_seconds",
    "Wall-clock latency per LangGraph node.",
    labelnames=("domain", "node"),
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)

LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Token usage broken out by direction.",
    labelnames=("domain", "kind"),  # kind in {prompt, completion}
)

LLM_COST_USD_TOTAL = Counter(
    "llm_cost_usd_total",
    "Cumulative estimated USD cost of LLM calls.",
    labelnames=("domain",),
)

RETRIEVAL_CANDIDATES = Histogram(
    "retrieval_candidates",
    "Candidates emitted at each retrieval stage.",
    labelnames=("domain", "stage"),  # stage in {semantic, lexical, fused, reranked}
    buckets=(0, 1, 2, 4, 6, 8, 10, 15, 20, 30, 50),
)

SQL_RAG_ATTEMPTS_TOTAL = Counter(
    "sql_rag_attempts_total",
    "SQL-RAG path outcomes for financial documents.",
    labelnames=("outcome",),
    # outcome: structured, prose, no_tables, safety_rejected, error
)

PARENT_HYDRATIONS_TOTAL = Counter(
    "parent_hydrations_total",
    "Parent-section hydration outcomes after rerank.",
    labelnames=("domain", "outcome"),
    # outcome: swapped, no_parent, skipped
)

DOCUMENT_INGESTIONS_TOTAL = Counter(
    "document_ingestions_total",
    "Documents indexed by outcome, domain, and pipeline stage.",
    labelnames=("domain", "status", "stage"),
    # status: indexed, duplicate, rejected
    # stage:  classify, parse, dedup, embed, store, pipeline
)

BM25_CACHE_EVENTS = Counter(
    "bm25_cache_events_total",
    "BM25 retriever cache hits, misses, and invalidations.",
    labelnames=("domain", "event"),
    # event: hit, miss, invalidate
)

AGENTIC_RETRIES_TOTAL = Counter(
    "agentic_retries_total",
    "Number of retrieval retry loops triggered by the agentic self-correction mechanism.",
    labelnames=("domain", "trigger"),
    # trigger: grade_retrieval (grader said chunks irrelevant)
    #          validate_citation (validate_node found no valid citations)
)

RETRIEVAL_GRADE_OUTCOMES = Counter(
    "retrieval_grade_outcomes_total",
    "Outcomes from the LLM-based retrieval grader node.",
    labelnames=("domain", "outcome"),
    # outcome: relevant, not_relevant, skipped
)

APP_INFO = Gauge(
    "app_info",
    "Static labels describing the running build.",
    labelnames=("version", "env"),
)


def render_latest() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
