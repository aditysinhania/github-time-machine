import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from core.config import settings


def _db_reachable() -> bool:
    """Best-effort check so these tests skip cleanly without a running Postgres,
    instead of failing the whole suite during lifespan startup."""
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine

    async def _ping():
        engine = create_async_engine(settings.DATABASE_URL)
        try:
            async with engine.connect():
                return True
        except Exception:
            return False
        finally:
            await engine.dispose()

    try:
        return asyncio.get_event_loop().run_until_complete(_ping())
    except RuntimeError:
        return asyncio.run(_ping())


pytestmark = pytest.mark.skipif(
    not _db_reachable(),
    reason="Postgres not reachable — run via `make test` (docker compose) for full API tests.",
)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "GitHub Time Machine API"


async def test_ping_endpoint(client):
    response = await client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_analyze_rejects_non_github_url(client):
    response = await client.post(
        "/api/v1/repositories/analyze",
        json={"url": "https://gitlab.com/owner/repo"},
    )
    assert response.status_code == 422


async def test_get_nonexistent_repository_404s(client):
    response = await client.get("/api/v1/repositories/999999")
    assert response.status_code == 404


async def test_docs_available(client):
    response = await client.get("/docs")
    assert response.status_code == 200
