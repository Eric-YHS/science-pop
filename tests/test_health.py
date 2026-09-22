"""The app object must import and expose a working health probe.

The database engine is created at import time but never connects until a
request runs a query, so the probe can be exercised without PostgreSQL.
"""

import asyncio

import pytest

httpx = pytest.importorskip("httpx")
pytest.importorskip("apscheduler")
pytest.importorskip("asyncpg")

from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


def test_health_probe_reports_ok():
    async def call():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/health")

    response = asyncio.run(call())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_builds():
    schema = app.openapi()
    assert schema["info"]["title"]
    assert "/health" in schema["paths"]


def test_documented_routes_exist():
    paths = set(app.openapi()["paths"])
    for expected in (
        "/api/papers",
        "/api/papers/disciplines",
        "/api/contents",
        "/api/workflow/convert",
        "/api/crawl/trigger",
    ):
        assert expected in paths, f"{expected} is no longer exposed"
