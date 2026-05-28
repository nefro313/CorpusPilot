# CorpusPilot

[![GitHub stars](https://img.shields.io/github/stars/nefro313/CorpusPilot?style=social)](https://github.com/nefro313/CorpusPilot)

A multi-domain Retrieval-Augmented Generation (RAG) application. Users upload documents tagged with one of five corpus domains and ask questions whose answers are grounded in the retrieved chunks with mandatory inline citations.

The system pairs **PostgreSQL** (relational state + BM25 lexical retrieval) with **Zilliz Cloud Milvus** (semantic vectors). Retrieval is hybrid (semantic + lexical), fused via Reciprocal Rank Fusion (RRF) with domain-aware weights, reranked with Cohere, and answered by ChatOpenAI under hard citation enforcement.

## Quick Start

### Installation

```bash
git clone https://github.com/nefro313/CorpusPilot.git
cd CorpusPilot
```

The project is split into a Python backend (managed with [uv](https://docs.astral.sh/uv/)) and a React frontend (managed with npm). Install both:

```bash
# backend
cd apps/backend
uv sync --dev

# frontend
cd ../frontend
npm install
```

Create an environment file at `apps/backend/.env`:

```bash
cp .env.example apps/backend/.env
```

Required keys:

```bash
OPENAI_API_KEY=<your-openai-api-key>
ZILLIZCLOUD_ENDPOINT=<your-zilliz-cluster-endpoint>
ZILLIZCLOUD_API_KEY=<your-zilliz-api-key>
LLAMA_CLOUD_API_KEY=<your-llamaparse-api-key>   # PDF/DOCX/PPTX/XLSX/HTML parsing
```

Optional keys:

```bash
COHERE_API_KEY=<your-cohere-api-key>            # enables Cohere rerank-v3.5
LANGSMITH_TRACING=true                          # enable LangSmith tracing
LANGSMITH_API_KEY=<your-langsmith-key>
LANGSMITH_PROJECT=ask-my-docs
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ask_my_docs
```

### Usage

Start Postgres:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres
```

Start the backend (FastAPI on `http://localhost:8000`):

```bash
cd apps/backend
uv run fastapi dev src/app.py
```

Start the frontend (Vite on `http://localhost:5173`):

```bash
cd apps/frontend
npm run dev
```

Open the frontend at `http://localhost:5173`. The backend interactive docs are at `http://localhost:8000/docs`.

Full stack with Docker:

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d --build
# frontend: http://localhost:3000
# backend docs: http://localhost:8000/docs
```

Observability sidecar stack (Prometheus + Grafana + Tempo):

```bash
docker compose \
  -f infrastructure/docker/docker-compose.yml \
  -f infrastructure/docker/docker-compose.observability.yml \
  up -d
```

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (admin / admin) — pre-loads `rag.json`
- Tempo: OTLP gRPC on `tempo:4317`

## Supported Domains

Each upload is tagged with exactly one domain. The pipeline then applies domain-aware chunking, retrieval weighting, query expansion, and safety guards on top.

| Domain                | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `technical_document`  | API docs, runbooks, architecture, product specs       |
| `research_paper`      | Papers, whitepapers, benchmark reports                |
| `legal_contract`      | Contracts, agreements, NDAs, policies, clauses        |
| `healthcare_document` | Clinical notes, discharge summaries, care plans       |
| `financial_document`  | 10-K/10-Q filings, earnings releases, financial decks |

## Architecture

### Component Overview

```text
                       ┌──────────────────────────┐
                       │ Browser (React + Vite)   │
                       │  - Upload (5 domains)    │
                       │  - Chat (SSE stream)     │
                       │  - Observability panel   │
                       └────────────┬─────────────┘
                                    │ HTTPS / SSE
                                    ▼
                       ┌──────────────────────────┐
                       │ FastAPI (async)          │
                       │  /api/documents/*        │
                       │  /api/chat/*             │
                       │  /api/observability/*    │
                       │  /metrics  (Prometheus)  │
                       └────┬───────────┬─────────┘
                            │           │
            ┌───────────────┘           └────────────────┐
            ▼                                            ▼
   ┌─────────────────────────┐               ┌──────────────────────────┐
   │  Ingestion path         │               │  Query path (LangGraph)  │
   │  validate → parse →     │               │  rewrite → sql_tables →  │
   │  chunk (parent+child) → │               │  expand_query →          │
   │  extract tables →       │               │  retrieve → rerank →     │
   │  embed → persist        │               │  hydrate_parents →       │
   │                         │               │  generate → validate →   │
   │                         │               │  safety_validate         │
   └───┬──────────┬──────────┘               └────┬─────────────┬───────┘
       ▼          ▼                               ▼             ▼
 ┌──────────┐ ┌────────────┐                ┌───────────┐ ┌────────────┐
 │ Postgres │ │ Milvus     │                │ Postgres  │ │ Milvus     │
 │ docs +   │ │ vectors    │                │ BM25 +    │ │ semantic   │
 │ chunks + │ │ (children) │                │ tables +  │ │ search     │
 │ tables + │ │            │                │ traces    │ │            │
 │ traces   │ │            │                │           │ │            │
 └──────────┘ └────────────┘                └───────────┘ └────────────┘

   External services used at runtime:
     - OpenAI:    embeddings (text-embedding-3-small)
                  chat       (gpt-4o-mini for answer + guard)
     - Cohere:    reranker   (rerank-v3.5)
     - LlamaParse: cloud PDF/DOCX/PPTX/XLSX/HTML parser
     - LangSmith: optional tracing
```

### Repository Layout

```text
ask_my_docs/
├── README.md                  # This file
├── PROJECT_STATE.md           # Snapshot of the current implementation
├── AGENTS.md                  # Working rules for AI agents in this repo
├── Makefile                   # Common dev commands
├── .pre-commit-config.yaml
├── .github/workflows/         # CI (includes rag-quality.yml eval gate)
├── apps/
│   ├── backend/               # FastAPI service (see Backend section)
│   └── frontend/              # React + Vite SPA (see Frontend section)
├── infrastructure/
│   ├── docker/                # docker-compose for Postgres + observability
│   ├── grafana/dashboards/    # rag.json
│   ├── prometheus/
│   └── tempo/
├── docs/runbooks/             # Operational runbooks
├── sample_docs/               # Sample inputs across domains
└── scripts/                   # Top-level helper scripts
```

## Backend

### Tech stack

- FastAPI (async) + Uvicorn
- SQLAlchemy 2.x async + asyncpg
- PostgreSQL 16
- Zilliz Cloud Milvus (via pymilvus + LlamaIndex bridge)
- LangChain + LangGraph (RAG workflow with `MemorySaver` checkpointer)
- LangSmith-compatible tracing
- LlamaParse (cloud) + pypdf (local fallback / first-page peek)
- OpenAI + Cohere SDKs
- RAGAS (eval)
- Prometheus client + OTLP exporter (Tempo)

### Source tree

```text
apps/backend/
├── pyproject.toml             # uv-managed deps
├── alembic.ini
├── migrations/                # Alembic versions
├── evals/
│   ├── fixtures/              # CI fixture corpus
│   └── experiments/latest.json
├── scripts/run_evals.py
├── tests/                     # pytest suite
└── src/
    ├── app.py                 # FastAPI app + lifespan + router registration
    ├── core/
    │   ├── config.py          # Pydantic Settings, env-driven config
    │   ├── logging.py
    │   ├── metrics.py         # Prometheus counter/histogram families
    │   └── tracing.py
    ├── domain/
    │   └── profiles.py        # CorpusDomain enum + DomainProfile registry
    ├── schemas/
    │   └── api.py             # Request/response Pydantic models
    ├── api/
    │   ├── sse.py             # SSE framing helpers
    │   └── routes/
    │       ├── documents.py   # /api/documents/*
    │       ├── chat.py        # /api/chat/* (incl. session DELETE)
    │       ├── observability.py
    │       └── metrics.py     # /metrics
    ├── services/
    │   ├── documents.py       # Upload orchestration
    │   ├── embeddings.py
    │   ├── llm.py             # Cached ChatOpenAI / Cohere factories
    │   ├── ingestion/
    │   │   ├── classification.py  # First-page LLM domain gate
    │   │   ├── parsing.py         # LlamaParse + pypdf fallback
    │   │   ├── chunking.py        # Section split + parent-child for legal/financial
    │   │   ├── tables.py          # Markdown-table extraction (financial)
    │   │   └── pipeline.py        # prepare_document helper
    │   ├── retrieval/
    │   │   ├── semantic.py    # Milvus ANN search
    │   │   ├── lexical.py     # BM25 over Postgres chunks (excludes parents)
    │   │   ├── fusion.py      # Domain-aware RRF weights
    │   │   ├── hybrid.py
    │   │   ├── cache.py       # Per-domain BM25 retriever cache
    │   │   └── types.py
    │   ├── rag/
    │   │   ├── graph.py       # LangGraph state graph + checkpointer accessor
    │   │   ├── nodes.py       # rewrite / sql_tables / expand_query / retrieve /
    │   │   │                  # rerank / hydrate_parents / generate / validate /
    │   │   │                  # safety_validate
    │   │   ├── pipeline.py    # run_rag_pipeline / stream_rag_response
    │   │   ├── prompts.py     # Citation-enforcing + expansion prompts
    │   │   ├── memory.py      # Bounded in-process session history (LRU)
    │   │   ├── sessions.py    # end_session: clears history + LangGraph thread
    │   │   ├── telemetry.py   # Token/cost accounting
    │   │   ├── followups.py
    │   │   └── state.py       # RAGState TypedDict
    │   └── observability/
    │       ├── anomalies.py
    │       └── feedback.py
    ├── storage/
    │   ├── database.py        # Async engine + init_db + get_db
    │   ├── models.py          # ORM
    │   ├── migrations_legacy.py
    │   └── repositories/
    └── vectorstores/
        ├── base.py
        ├── milvus.py          # pymilvus authoritative writer
        ├── llamaindex_milvus.py
        └── sync.py            # Embedding backfill (skips parent rows)
```

### Data model (Postgres)

```text
documents
  id            uuid PK
  user_id       text  (browser-local UUID; scopes every query and delete)
  filename      text
  title         text
  domain        enum (CorpusDomain)
  mime_type     text
  checksum      text  (dedup key; unique per user via uq_documents_user_checksum)
  content       text  (full normalized text)
  metadata_json jsonb (chunking_strategy + retrieval_strategy)
  total_chunks  int   (children only)
  created_at    timestamptz

document_chunks  ─── stores BOTH children (searchable) and parents (Postgres-only)
  id              uuid PK
  document_id     uuid FK → documents.id ON DELETE CASCADE
  parent_chunk_id uuid FK → document_chunks.id ON DELETE CASCADE  (NULL = leaf)
  chunk_index     int  (children positive; parents use negative sentinel)
  page_number     int  nullable
  section_title   text nullable
  token_count     int
  content         text
  metadata_json   jsonb
  created_at      timestamptz

document_table_rows  ─── EAV/long format, one row per table cell (financial only)
  id             uuid PK
  document_id    uuid FK → documents.id ON DELETE CASCADE
  table_index    int
  row_index      int
  column_name    text
  cell_value     text
  page_number    int  nullable
  section_title  text nullable
  created_at     timestamptz

query_traces
  id, domain, question, answer, citations(jsonb),
  grounded, citation_valid, latency_ms,
  prompt_tokens, completion_tokens, total_tokens, total_cost_usd,
  retrieval_count, citation_count, metadata_json, created_at

answer_feedback
  id, question, answer, rating (-1|0|1),
  domain, session_id, comment, citations(jsonb), created_at
```

Parents are leaves' "full-section context" — they are filtered out of BM25 (lexical SQL excludes any row that appears as another row's `parent_chunk_id`) and skipped by the vector backfill, so only children are indexed in Milvus.

### Vector store (Milvus)

- **Collection**: `document_chunks` (configurable)
- **Primary key**: `chunk_id` (string, mirrors Postgres `document_chunks.id` of leaf chunks)
- **Vector field**: `embedding` (1536-dim, `text-embedding-3-small`)
- **Scalar fields**: `document_id`, `document_filename`, `domain`, `user_id`, `chunk_index`, `page_number`, `section_title`, `content`
- **Metric**: COSINE (configurable)
- **Writer**: `pymilvus` is authoritative; LlamaIndex `.add()` runs as a best-effort dual-write

### Settings

Loaded once via `get_settings()` (`lru_cache`) in `core/config.py`.

| Variable                            | Default                  | Purpose                                       |
| ----------------------------------- | ------------------------ | --------------------------------------------- |
| `DATABASE_URL`                      | local Postgres           | Async SQLAlchemy URL                          |
| `OPENAI_API_KEY`                    | —                        | Embeddings + chat + guard LLM                 |
| `OPENAI_EMBEDDING_MODEL`            | `text-embedding-3-small` | 1536-dim                                      |
| `OPENAI_CHAT_MODEL`                 | `gpt-4o-mini`            | Answer generation                             |
| `OPENAI_GUARD_MODEL`                | `gpt-4o-mini`            | Domain classifier, rewrite, expansion, guard  |
| `ZILLIZCLOUD_ENDPOINT` / `_API_KEY` | —                        | Milvus Cloud auth                             |
| `COHERE_API_KEY`                    | —                        | Cohere rerank                                 |
| `LLAMA_CLOUD_API_KEY`               | —                        | LlamaParse; pypdf fallback kicks in if absent |
| `RETRIEVAL_SEMANTIC_K`              | `10`                     | Semantic top-K                                |
| `RETRIEVAL_LEXICAL_K`               | `10`                     | BM25 top-K                                    |
| `RETRIEVAL_FUSION_K`                | `8`                      | Fused output size                             |
| `RETRIEVAL_RRF_K`                   | `60`                     | RRF dampener                                  |
| `CITATION_MIN_SOURCES`              | `2`                      | Min unique citations to call grounded         |
| `UPLOAD_MAX_BYTES`                  | `15 * 1024 * 1024`       | Per-file upload size cap                      |
| `EVAL_MIN_*`                        | thresholds               | RAGAS gate (faithfulness / FC / recall)       |

LangSmith vars (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`) opt in to tracing.

### API surface

| Method | Path                             | Purpose                                                  |
| ------ | -------------------------------- | -------------------------------------------------------- |
| GET    | `/api/health`                    | Liveness                                                 |
| GET    | `/api/documents/domains`         | Domain profile catalogue                                 |
| POST   | `/api/documents/upload`          | Single-file upload (JSON)                                |
| POST   | `/api/documents/upload/stream`   | Multi-file upload, SSE progress                          |
| GET    | `/api/documents/`                | List indexed documents                                   |
| DELETE | `/api/documents/{document_id}`   | Delete + invalidate vector + lexical caches              |
| POST   | `/api/chat/`                     | Synchronous Q&A                                          |
| POST   | `/api/chat/stream`               | Streaming Q&A (SSE)                                      |
| POST   | `/api/chat/feedback`             | Record thumbs feedback                                   |
| DELETE | `/api/chat/session/{session_id}` | Drop history + LangGraph thread for an abandoned session |
| GET    | `/api/observability/summary`     | P50/P95 latency, grounded rate, cost                     |
| GET    | `/api/observability/anomalies`   | Per-domain z-score outliers                              |
| GET    | `/api/observability/feedback`    | Thumbs aggregate                                         |
| GET    | `/metrics`                       | Prometheus scrape (not under `/api`)                     |

## Frontend

### Frontend tech stack

React 18 · TypeScript · Vite · Vitest · React Query · custom animated UI.

### Layout

The workspace splits in two columns:

- **Sidebar (left)**: `DocumentUpload` (domain dropdown + drop zone + upload progress) followed by `TelemetryTabs` (Anomalies + Feedback).
- **Right column**: `ChatPanel` (with the per-domain accented current-domain banner) and `IndexedCorpus` filtered to the active domain.

Both columns share the lifted `selectedDomain` state in `App.tsx`. Changing the domain from either the sidebar dropdown or any caller automatically:

1. Re-labels the upload button.
2. Filters the indexed-corpus list to that domain.
3. Resets the chat: clears messages, mints a fresh `session_id`, and `DELETE`s the abandoned session on the backend.

### Frontend source tree

```text
apps/frontend/src/
├── main.tsx
├── App.tsx                     # Two-column layout, lifted domain state + session banner
├── index.css                   # Theme + component styles (incl. per-domain banner accents)
├── types.ts                    # Mirrors backend Pydantic schemas
├── api/client.ts               # Typed fetch wrapper; injects X-User-ID header
├── hooks/
│   ├── queries.ts              # React Query hooks
│   ├── useChatStream.ts        # SSE consumer for /api/chat/stream
│   └── useUserId.ts            # Generates/reads browser UUID from localStorage
├── test/setup.ts
└── components/
    ├── DocumentUpload.tsx      # Sidebar upload UI
    ├── DomainDropdown.tsx
    ├── GitHubStarButton.tsx    # Header GitHub star button
    ├── IndexedCorpus.tsx       # Filters by selectedDomain
    ├── ChatPanel.tsx           # Resets session on domain change
    ├── ErrorBoundary.tsx
    ├── icons.tsx
    ├── chat/
    │   ├── ChatComposer.tsx
    │   ├── MessageList.tsx / MessageCard.tsx / AnswerMarkdown.tsx
    │   ├── CitationChip.tsx / SourceCard.tsx
    │   ├── TelemetryStrip.tsx / FeedbackBar.tsx / FollowUpChips.tsx
    │   ├── CorpusBanner.tsx    # Per-domain accent + pulse dot
    │   ├── ThinkingState.tsx
    │   ├── citations.ts / sse.ts (+ tests)
    │   ├── domain.ts           # Icons / labels / newSessionId
    │   └── types.ts
    └── observability/
        ├── TelemetryTabs.tsx
        ├── AnomaliesPanel.tsx
        └── FeedbackPanel.tsx
```

### Build / dev / test

```bash
cd apps/frontend
npm install          # one-time
npm run dev          # http://localhost:5173
npm run build        # static bundle into dist/
npm run typecheck    # tsc --noEmit
npm test -- --run    # vitest
```

## Ingestion Workflow

```text
┌────────────────────────────────────────────────────────────────────┐
│ Client: DocumentUpload.tsx                                         │
│   Pre-flight: extension allowlist, size > 0, size ≤ 15 MB.         │
│   POST multipart → /api/documents/upload/stream (SSE)              │
└──────────────────────────┬─────────────────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│ services/documents.py :: _index_with_progress  (per file)          │
│                                                                    │
│   queued     → server-side size check (UPLOAD_MAX_BYTES)           │
│   validating → classification.classify_first_page                  │
│                  matches / mismatch (+suggested) / out_of_scope /  │
│                  unknown (fail-open)                               │
│   parsing    → LlamaParse cloud parse; pypdf fallback if missing   │
│                key or empty text; UTF-8 decode for plain text      │
│   chunking   → per-domain section split + RecursiveCharSplitter    │
│                For legal_contract & financial_document, also emit  │
│                PARENT rows (full sections) alongside child chunks. │
│                For financial_document, extract markdown tables →   │
│                document_table_rows (EAV cells).                    │
│   dedup      → checksum match → status="duplicate"                 │
│   embedding  → OpenAI text-embedding-3-small on CHILDREN only      │
│   storing    → INSERT documents + chunks (parents+children) +      │
│                table rows; upsert children into Milvus; commit;    │
│                invalidate_retrieval_cache(domain)                  │
│   done       → UploadFileResult(status="indexed")                  │
│                                                                    │
│ SSE events: batch_started → file_progress*N → file_result →        │
│             batch_complete                                         │
└────────────────────────────────────────────────────────────────────┘
```

### Edge cases

- Unsupported extension / empty / oversize → skipped client-side with explanation.
- Domain mismatch → result card shows reason + "Switch to suggested" CTA.
- Out-of-scope → result card lists supported domains.
- Duplicate checksum → "duplicate" status, reuses existing entry.
- Parse-empty (image-only PDF, both paths empty) → suggests OCR or key check.
- Per-file failure inside a batch does not block the rest.

## Query Workflow (RAG)

The RAG flow is a compiled LangGraph (`services/rag/graph.py`) over a single `RAGState`. Each `session_id` keys both the in-process history and a `MemorySaver` checkpoint thread; abandoning a session (`DELETE /api/chat/session/{id}`) drops both.

```text
                     ┌────────┐
                     │ START  │
                     └───┬────┘
                         ▼
                  ┌──────────────┐
                  │  rewrite     │  guard LLM resolves coreferences from
                  └───────┬──────┘  the last N turns
                          ▼
                  ┌──────────────┐
                  │  sql_tables  │  financial only: classify structured-vs-prose;
                  └───────┬──────┘  if structured, generate constrained SELECT
                          │         over document_table_rows, run through a
                          │         regex safety filter, stash sql_context
                          ▼
                  ┌──────────────┐
                  │ expand_query │  research_paper → 3 angle-targeted paraphrases
                  └───────┬──────┘  technical_document → 1 step-back broader query
                          │         others → no expansion
                          ▼
                  ┌──────────────┐
                  │  retrieve    │  hybrid_search per variant SEQUENTIALLY
                  └───────┬──────┘  (AsyncSession is not concurrent-safe).
                          │         Dedupes hits across variants then re-fuses
                          │         via domain-aware RRF.
                          ▼
                  ┌──────────────┐
                  │   rerank     │  Cohere rerank-v3.5; falls back to fusion_score
                  └───────┬──────┘  on Cohere errors
                          ▼
                  ┌──────────────────┐
                  │ hydrate_parents  │  for legal/financial, replace each child's
                  └───────┬──────────┘  content with its full parent-section text
                          ▼               (citation_id / page / section unchanged)
                  ┌──────────────┐
                  │  generate    │  ChatOpenAI streams; every paragraph must
                  └───────┬──────┘  include [C#] (or [CSQL]) citation tags.
                          ▼               If sql_context is present it is injected
                          ▼               as [CSQL] and preferred for figures.
                  ┌──────────────┐
                  │  validate    │  Citation tags must reference real hits.
                  └───────┬──────┘  Sets grounded / citations / citation_valid.
                          ▼
                  ┌────────────────┐
                  │ safety_validate│  healthcare_document only: guard LLM checks
                  └───────┬────────┘ for ungrounded medical recommendations;
                          ▼            appends review notice and flips grounded
                        ┌───┐          to false if unsafe.
                        │END│
                        └───┘
```

### Retrieve in detail

```text
                  ┌─────────────────────┐
                  │ AskRequest          │
                  └──────────┬──────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
      ┌──────────────────┐     ┌──────────────────────┐
      │ semantic_search  │     │ lexical_search       │
      │ Milvus ANN       │     │ BM25 over Postgres   │
      │ domain filter    │     │ (parents excluded)   │
      │ k = 10           │     │ k = 10               │
      └────────┬─────────┘     └──────────┬───────────┘
               │                          │
               └──────────────┬───────────┘
                              ▼
                ┌────────────────────────────┐
                │ Domain-aware RRF           │
                │  legal:    (sem 0.30, lex 0.70)
                │  financial:(sem 0.35, lex 0.65)
                │  technical:(sem 0.60, lex 0.40)
                │  research: (sem 0.75, lex 0.25)
                │  health:   (sem 0.50, lex 0.50)
                │  rrf_k = 60                │
                └────────────┬───────────────┘
                             ▼
                ┌────────────────────────────┐
                │ Cohere rerank-v3.5         │
                └────────────────────────────┘
```

### Stream events (`/api/chat/stream`)

| SSE event    | Payload                                       |
| ------------ | --------------------------------------------- |
| `text_delta` | `{"delta": "next answer chunk"}`              |
| `response`   | Full `ChatResponse` once generation completes |
| `sources`    | `{"sources": [SourceChunk...]}`               |
| `done`       | `{}`                                          |
| `error`      | `{"message": "..."}`                          |

## RAG Strategies

The pipeline applies several retrieval and generation strategies, each conditioned on the active domain.

### Hybrid retrieval (all domains)

Every query runs through both semantic ANN (Milvus, cosine over 1536-dim OpenAI embeddings) and lexical BM25 (Postgres). The two ranked lists are merged via Reciprocal Rank Fusion with **domain-aware weights** — legal/financial documents lean heavily on lexical (clause text, dollar amounts, defined terms), research papers lean on semantic (concept matching across paraphrases), and technical docs sit in between.

### Parent–child chunking (legal, financial)

Ingestion emits two kinds of rows:

- **Children** — small, retrieval-sized chunks. Embedded into Milvus, indexed in BM25.
- **Parents** — full-section context. Stored in Postgres only, excluded from both indexes.

At query time, after rerank, the `hydrate_parents` node swaps each surviving child's content for its parent section. The model sees the full section while citation IDs, page numbers, and section titles continue to point at the matched child. This avoids "snippet too narrow" hallucinations on contracts and 10-Ks without polluting the index with redundant large chunks.

### SQL-RAG over extracted tables (financial)

During ingestion, markdown tables in financial documents are flattened into an EAV row store (`document_table_rows`). At query time the `sql_tables` node:

1. Classifies the question as **structured** (asks for a figure / a value from a table) or **prose**.
2. For structured queries, generates a constrained `SELECT ... FROM document_table_rows ...` and runs it through a regex safety filter (rejects semicolons, comments, DDL, DML — only `SELECT` is permitted).
3. Stashes the result as `sql_context`. The generator injects it as a `[CSQL]` citation that the LLM must prefer for figures over prose-extracted numbers.

### Multi-query expansion (research papers)

`expand_query_node` produces three angle-targeted paraphrases for research queries (e.g. methodology focus, results focus, comparison focus). Each variant runs through full hybrid retrieval **sequentially** (the SQLAlchemy `AsyncSession` is not concurrency-safe). Variants are deduplicated then re-fused with RRF, yielding broader coverage than a single query.

### Step-back prompting (technical documents)

For technical queries, the same `expand_query_node` produces **one** broader "step-back" reformulation alongside the literal query. This recovers context when users ask about a leaf API but the answer lives in a parent concept page.

### Citation enforcement (all domains)

The generator prompt requires every paragraph to end with `[C#]` (or `[CSQL]`) tags pointing at the retrieved sources. The `validate` node verifies that every cited tag maps to a real hit. If fewer than `CITATION_MIN_SOURCES` distinct sources are cited, or any tag is invented, `grounded` is set to `false`.

### Healthcare safety guard

For `healthcare_document` queries, an additional `safety_validate` node runs after `validate`. A guard LLM scans the answer for ungrounded medical recommendations. If unsafe, it appends a clinician-review notice and flips `grounded` to `false` — independently of whether citation enforcement passed.

### Session memory

In-process session history is an LRU-capped `OrderedDict` (max 200 sessions) keyed by `session_id`. LangGraph's `MemorySaver` holds checkpoints for the same key. `end_session()` drops both. The frontend calls `DELETE /api/chat/session/{id}` on every "New chat" and on every domain change so that history never crosses domains.

## Observability

### Prometheus families exposed at `/metrics`

| Family                        | Type      | Labels           |
| ----------------------------- | --------- | ---------------- |
| `rag_requests_total`          | counter   | domain, grounded |
| `rag_request_latency_seconds` | histogram | domain           |
| `llm_tokens_total`            | counter   | domain, kind     |
| `llm_cost_usd_total`          | counter   | domain           |
| `retrieval_candidates`        | histogram | domain, stage    |
| `document_ingestions_total`   | counter   | domain, status   |
| `app_info`                    | gauge     | version, env     |

### Trace and feedback APIs

- `GET /api/observability/summary` — aggregates `query_traces` (rolling window) into total/grounded rate, citation-valid rate, P50/P95 latency, average cost, and per-domain breakdown.
- `GET /api/observability/anomalies?threshold=2.5` — per-domain z-score over latency and cost.
- `GET /api/observability/feedback` — thumbs counts overall and per domain.

### LangSmith (optional)

Set `LANGSMITH_TRACING=true` plus `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` to forward every LangGraph node call to LangSmith.

## Evaluation Gate

`scripts/run_evals.py` seeds the fixture corpus, runs the chat pipeline against canned questions, scores with RAGAS, writes `evals/experiments/latest.json`, and exits non-zero if **faithfulness**, **factual correctness**, or **context recall** drop below their configured thresholds.

CI: `.github/workflows/rag-quality.yml` runs the eval gate on PRs.

Run locally:

```bash
cd apps/backend
uv run python scripts/run_evals.py --seed-fixtures
```

Thresholds are env-driven (`EVAL_MIN_FAITHFULNESS`, `EVAL_MIN_FACTUAL_CORRECTNESS`, `EVAL_MIN_CONTEXT_RECALL`).

## Tests

| Suite           | Command                                 |
| --------------- | --------------------------------------- |
| Backend pytest  | `cd apps/backend && uv run pytest -q`   |
| Frontend vitest | `cd apps/frontend && npm test -- --run` |
| Frontend types  | `cd apps/frontend && npm run typecheck` |

Tests intentionally avoid real OpenAI / Cohere / Milvus / Postgres reachability. `tests/conftest.py` defaults all API keys to empty strings so lazy LLM factories never call out.

## Development

### Pre-commit checks

Run the linters before every commit:

```bash
# backend
cd apps/backend
uv run ruff check .
uv run ruff format --check .
uv run mypy src

# frontend
cd apps/frontend
npm run typecheck
npm test -- --run
```

If `ruff format --check` fails, run `uv run ruff format .` and re-run the checks before committing.

### Adding a new corpus domain

1. Add a new value to `CorpusDomain` in `apps/backend/src/domain/profiles.py` and register a `DomainProfile` describing its chunking and retrieval-strategy hints.
2. Add a corresponding RRF weight tuple in `apps/backend/src/services/retrieval/fusion.py`.
3. If the domain needs query expansion or a guard node, extend `apps/backend/src/services/rag/nodes.py` and wire the conditional edge in `graph.py`.
4. Mirror the domain in the frontend: `apps/frontend/src/components/chat/domain.ts` (icon + label) and `apps/frontend/src/types.ts`.

### Adding a new RAG node

1. Implement the async node function in `apps/backend/src/services/rag/nodes.py`, taking and returning a partial `RAGState`.
2. Register the node and its edges in `apps/backend/src/services/rag/graph.py`.
3. Expose any new state fields in `state.py` as `TypedDict` entries.

### Database migrations

```bash
cd apps/backend
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

## Known constraints

- No sign-in — identity is a browser-local UUID stored in `localStorage` as `ask-my-docs-user-id`. A user who clears storage or switches browsers gets a fresh identity and loses access to their prior documents (re-upload required).
- Per-user document and chat isolation is implemented. Observability dashboards (`/api/observability/*`) remain global (all users' traces are aggregated).
- Session memory and the LangGraph `MemorySaver` are in-process only; restarts wipe history. The LRU cap (200 sessions) bounds growth but is per-process.
- LlamaIndex dual-write is best-effort: failures are swallowed because `pymilvus` is the source of truth.
- Domain classifier failures fail **open** (continue indexing).
- Object storage for raw uploads is not implemented — only normalized text is persisted.
- No background job queue — uploads run inline on the request worker.
- SQL-RAG runs raw text against Postgres; the regex safety filter is the only barrier between the LLM-generated `SELECT` and the database. Locked to `SELECT ... FROM document_table_rows`, rejects semicolons / comments / DDL / DML.

## License

This project is released under the [MIT License](LICENSE).
