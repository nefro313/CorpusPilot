# syntax=docker/dockerfile:1.7
#
# Multi-stage build:
#   1. `deps` resolves the project + its wheels into /app/.venv using uv.
#   2. `runtime` copies that venv into a fresh python:3.12-slim image with
#      no uv binary, no build cache, and no apt layers from the build side.
#
# Same dependencies as a single-stage build — the win is layering and a
# smaller, faster final image because runtime stays free of build tooling.

FROM python:3.12-slim AS deps

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Resolve and install deps first, before src/, so editing application code
# doesn't bust the heavy uv-sync cache layer.
COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen --no-install-project

COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen


FROM python:3.12-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
COPY --from=deps /app/src /app/src

EXPOSE 8000

CMD ["fastapi", "run", "src/app.py", "--host", "0.0.0.0", "--port", "8000"]
