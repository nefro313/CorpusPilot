import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Ask My Docs"
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pgrag"
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_guard_model: str = "gpt-4o-mini"
    openai_eval_model: str = "gpt-4o-mini"
    embedding_dimensions: int = 1536
    zillizcloud_endpoint: str = ""
    zillizcloud_api_key: str = ""
    cohere_api_key: str = ""
    cohere_rerank_model: str = "rerank-v3.5"
    llama_cloud_api_key: str = ""
    llamaparse_result_type: str = "markdown"
    llamaparse_num_workers: int = 2
    llamaparse_language: str = "en"
    milvus_collection_name: str = "document_chunks"
    milvus_vector_field_name: str = "embedding"
    milvus_metric_type: str = "COSINE"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    retrieval_semantic_k: int = 10
    retrieval_lexical_k: int = 10
    retrieval_fusion_k: int = 8
    retrieval_rrf_k: int = 60
    citation_min_sources: int = 2

    langsmith_tracing: bool = False
    langsmith_project: str = "ask-my-docs"
    langsmith_api_key: str = ""
    langsmith_endpoint: str = ""
    langsmith_workspace_id: str = ""

    metrics_window_size: int = 200
    chat_input_cost_per_1k: float = 0.00015
    chat_output_cost_per_1k: float = 0.0006

    eval_min_faithfulness: float = 0.8
    eval_min_factual_correctness: float = 0.78
    eval_min_context_recall: float = 0.75

    upload_max_bytes: int = 15 * 1024 * 1024
    observability_recent_runs: int = 200

    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def milvus_search_params(self) -> dict[str, str]:
        return {"metric_type": self.milvus_metric_type}


def apply_langsmith_env(settings: Settings) -> None:
    """Project LangSmith config into the env vars the langsmith SDK reads.

    Called explicitly from application startup. Not invoked at import time so
    test suites can construct Settings without polluting os.environ.
    """
    os.environ["LANGSMITH_TRACING"] = "true" if settings.langsmith_tracing else "false"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    if settings.langsmith_endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    if settings.langsmith_workspace_id:
        os.environ["LANGSMITH_WORKSPACE_ID"] = settings.langsmith_workspace_id


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
