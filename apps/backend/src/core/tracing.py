"""OpenTelemetry bootstrap.

The exporter is opt-in: when `OTEL_EXPORTER_OTLP_ENDPOINT` is unset we register
the SDK with a no-op exporter so spans/metrics are created but discarded. That
keeps local dev silent and CI cheap while preserving the instrumentation
surface for production.

Auto-instrumentation is intentionally narrow:
- FastAPI gives us HTTP span timing without manual wrapping per route.
- SQLAlchemy gives us per-query spans, which is where most of our tail
  latency actually lives.
- httpx covers the OpenAI/Cohere outbound calls.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import Settings

logger = logging.getLogger(__name__)
_initialised = False


def configure_tracing(app: FastAPI, settings: Settings) -> None:
    """Wire OpenTelemetry into the FastAPI app.

    Safe to call once at startup. Subsequent calls short-circuit so test
    harnesses can re-create the app object without re-instrumenting and
    triggering the "already instrumented" warning.
    """
    global _initialised
    if _initialised:
        return
    _initialised = True

    resource = Resource.create(
        {
            "service.name": settings.app_name.lower().replace(" ", "-"),
            "service.version": "2.0.0",
            "deployment.environment": settings.app_env,
        }
    )

    provider = TracerProvider(resource=resource)
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        logger.info("OpenTelemetry tracing enabled, exporting to %s", endpoint)
    else:
        logger.info(
            "OpenTelemetry SDK initialised without an exporter (set OTEL_EXPORTER_OTLP_ENDPOINT to ship spans)"
        )

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics,api/health")
    HTTPXClientInstrumentor().instrument()


def instrument_sqlalchemy(engine) -> None:
    """Instrument the SQLAlchemy engine. Separate hook because the engine is
    created lazily relative to the FastAPI app."""
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
