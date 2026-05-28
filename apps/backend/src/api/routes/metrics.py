"""Prometheus scrape endpoint.

Kept on a dedicated router so the scrape target (`/metrics`) doesn't collide
with the API-prefixed observability routes and so a scraper-only NetworkPolicy
can match it precisely.
"""

from fastapi import APIRouter, Response

from core.metrics import render_latest

router = APIRouter()


@router.get("/metrics", include_in_schema=False)
async def metrics_endpoint() -> Response:
    body, content_type = render_latest()
    return Response(content=body, media_type=content_type)
