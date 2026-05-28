"""Pytest bootstrap.

Tests run without OpenAI / Cohere / Milvus / Postgres reachable. We pin a
deterministic Settings object so the lazy LLM factories never try to call out,
and so importing `app` is safe even when no .env is present.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make `src/` importable without an editable install
BACKEND_SRC = Path(__file__).resolve().parents[1] / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

# Force-defaults so pydantic-settings doesn't try to load a real .env.
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test",
)
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("ZILLIZCLOUD_ENDPOINT", "")
os.environ.setdefault("ZILLIZCLOUD_API_KEY", "")
os.environ.setdefault("COHERE_API_KEY", "")
os.environ.setdefault("LANGSMITH_TRACING", "false")
