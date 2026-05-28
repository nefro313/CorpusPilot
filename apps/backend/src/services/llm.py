"""Lazy factories for LLM and embedding clients.

Instantiating clients at import time made the previous codebase slow to load
and hard to test (every test had to monkeypatch module-level singletons).
Each accessor below memoises a single client per process, but only on first
use, so tests can override `core.config.get_settings` before anything is
constructed.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_cohere import CohereRerank
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from core.config import get_settings


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )


@lru_cache(maxsize=1)
def get_answer_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        temperature=0,
    )


@lru_cache(maxsize=1)
def get_followup_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_guard_model,
        temperature=0.2,
    )


@lru_cache(maxsize=1)
def get_rewrite_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_guard_model,
        temperature=0,
    )


@lru_cache(maxsize=1)
def get_guard_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_guard_model,
        temperature=0,
    )


@lru_cache(maxsize=1)
def get_reranker() -> CohereRerank:
    settings = get_settings()
    return CohereRerank(
        cohere_api_key=settings.cohere_api_key,
        model=settings.cohere_rerank_model,
    )
