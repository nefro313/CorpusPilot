import argparse
import asyncio
import json
import uuid
import warnings
from pathlib import Path
from statistics import mean

warnings.filterwarnings(
    "ignore",
    message=r"Importing .* from 'ragas\.metrics' is deprecated.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r"LangchainEmbeddingsWrapper is deprecated.*",
    category=DeprecationWarning,
)

from langchain_openai import OpenAIEmbeddings as LCOpenAIEmbeddings
from openai import OpenAI
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import llm_factory
from ragas.metrics import (
    ContextRecall,
    FactualCorrectness,
    Faithfulness,
    ResponseRelevancy,
)
from ragas.run_config import RunConfig
from sqlalchemy import select

from core.config import get_settings
from domain.profiles import CorpusDomain
from schemas.api import AskRequest
from services.embeddings import embed_documents
from services.ingestion import prepare_document
from services.rag import run_rag_pipeline
from storage.database import async_session, init_db
from storage.models import Document, DocumentChunk
from vectorstores import vector_store
from vectorstores.base import VectorChunkRecord

DATASET_PATH = Path("evals/dataset.json")
FIXTURES_DIR = Path("evals/fixtures")
EXPERIMENTS_DIR = Path("evals/experiments")


async def seed_fixture_corpus() -> None:
    dataset = json.loads(DATASET_PATH.read_text())
    await init_db()
    async with async_session() as session:
        for item in dataset:
            fixture_path = FIXTURES_DIR / item["fixture"]
            payload = fixture_path.read_bytes()
            domain = CorpusDomain(item["domain"])
            prepared = await prepare_document(fixture_path.name, payload, domain, "text/markdown")
            exists = await session.scalar(
                select(Document).where(Document.checksum == prepared.checksum)
            )
            if exists:
                continue
            embeddings = await embed_documents([chunk.content for chunk in prepared.chunks])
            document = Document(
                id=uuid.uuid4(),
                filename=fixture_path.name,
                title=prepared.title,
                domain=domain,
                mime_type=prepared.mime_type,
                checksum=prepared.checksum,
                content=prepared.content,
                metadata_json={"fixture": True},
                total_chunks=len(prepared.chunks),
            )
            session.add(document)
            chunk_rows: list[DocumentChunk] = []
            for chunk in prepared.chunks:
                chunk_row = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    token_count=chunk.token_count,
                    content=chunk.content,
                    metadata_json=chunk.metadata_json,
                )
                chunk_rows.append(chunk_row)
                session.add(chunk_row)

            await session.flush()
            vector_records = [
                VectorChunkRecord(
                    chunk_id=str(chunk_row.id),
                    document_id=str(document.id),
                    document_filename=fixture_path.name,
                    domain=domain,
                    chunk_index=chunk_row.chunk_index,
                    page_number=chunk_row.page_number,
                    section_title=chunk_row.section_title,
                    content=chunk_row.content,
                    embedding=embedding,
                )
                for chunk_row, embedding in zip(chunk_rows, embeddings)
            ]
            await vector_store.upsert_chunks(vector_records)
        await session.commit()


async def run_dataset() -> dict:
    dataset = json.loads(DATASET_PATH.read_text())
    samples: list[SingleTurnSample] = []
    async with async_session() as session:
        for item in dataset:
            response = await run_rag_pipeline(
                session,
                AskRequest(question=item["question"], domain=CorpusDomain(item["domain"])),
            )
            samples.append(
                SingleTurnSample(
                    user_input=item["question"],
                    response=response.answer,
                    reference=item["reference"],
                    retrieved_contexts=[source.content for source in response.sources],
                )
            )

    settings = get_settings()
    openai_client = OpenAI(api_key=settings.openai_api_key)
    eval_llm = llm_factory(settings.openai_eval_model, client=openai_client)
    eval_embeddings = LangchainEmbeddingsWrapper(
        LCOpenAIEmbeddings(model=settings.openai_embedding_model, api_key=settings.openai_api_key)
    )

    evaluation_dataset = EvaluationDataset(samples=samples)
    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[
            Faithfulness(llm=eval_llm),
            FactualCorrectness(llm=eval_llm),
            ContextRecall(llm=eval_llm),
            ResponseRelevancy(llm=eval_llm, embeddings=eval_embeddings),
        ],
        llm=eval_llm,
        embeddings=eval_embeddings,
        run_config=RunConfig(timeout=180, max_retries=3),
        raise_exceptions=False,
    )
    rows = result.to_pandas().to_dict(orient="records")
    summary = {
        metric: _column_mean(rows, metric)
        for metric in ("faithfulness", "factual_correctness", "context_recall", "answer_relevancy")
    }
    return {"rows": rows, "summary": summary}


def _column_mean(rows: list[dict], metric: str) -> float:
    if not rows:
        return 0.0
    candidates = [
        c for c in rows[0] if c == metric or c.startswith(f"{metric}(") or c.endswith(f"_{metric}")
    ]
    if not candidates:
        raise RuntimeError(
            f"Metric '{metric}' not found in evaluation columns: {sorted(rows[0].keys())}"
        )
    column = candidates[0]
    values = [row.get(column) for row in rows if isinstance(row.get(column), (int, float))]
    return mean(values) if values else 0.0


def enforce_thresholds(summary: dict) -> None:
    settings = get_settings()
    failures: list[str] = []
    if summary["faithfulness"] < settings.eval_min_faithfulness:
        failures.append(
            f"faithfulness {summary['faithfulness']:.3f} < {settings.eval_min_faithfulness:.3f}"
        )
    if summary["factual_correctness"] < settings.eval_min_factual_correctness:
        failures.append(
            f"factual_correctness {summary['factual_correctness']:.3f} < {settings.eval_min_factual_correctness:.3f}"
        )
    if summary["context_recall"] < settings.eval_min_context_recall:
        failures.append(
            f"context_recall {summary['context_recall']:.3f} < {settings.eval_min_context_recall:.3f}"
        )
    if failures:
        raise SystemExit("Evaluation gate failed: " + "; ".join(failures))


async def main(seed: bool) -> None:
    if seed:
        await seed_fixture_corpus()

    results = await run_dataset()
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = EXPERIMENTS_DIR / "latest.json"
    output_path.write_text(json.dumps(results, indent=2))
    enforce_thresholds(results["summary"])
    print(json.dumps(results["summary"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAGAS evals for Ask My Docs")
    parser.add_argument(
        "--seed-fixtures", action="store_true", help="Index eval fixtures before running"
    )
    args = parser.parse_args()
    asyncio.run(main(seed=args.seed_fixtures))
