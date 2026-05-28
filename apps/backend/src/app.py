from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api.routes import chat, documents, metrics, observability
from core.config import apply_langsmith_env, get_settings
from core.logging import configure_logging
from core.metrics import APP_INFO
from core.tracing import configure_tracing, instrument_sqlalchemy
from storage.database import engine, get_db, init_db
from vectorstores.milvus import vector_store

settings = get_settings()
configure_logging(settings)
apply_langsmith_env(settings)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, version="2.0.0", lifespan=lifespan)

configure_tracing(app, settings)
instrument_sqlalchemy(engine)
APP_INFO.labels(version="2.0.0", env=settings.app_env).set(1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(observability.router)
app.include_router(metrics.router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "langsmith_tracing": settings.langsmith_tracing,
    }


@app.get("/api/ready")
async def readiness():
    checks: dict[str, str] = {}

    async for db in get_db():
        try:
            await db.execute(text("SELECT 1"))
            checks["postgres"] = "ok"
        except Exception as exc:
            checks["postgres"] = f"error: {exc}"
        break

    try:
        await vector_store.ensure_ready()
        checks["milvus"] = "ok"
    except Exception as exc:
        checks["milvus"] = f"error: {exc}"

    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
        status_code=200 if all_ok else 503,
    )
