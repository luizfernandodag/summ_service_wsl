import pytest
from httpx import AsyncClient
from ..app.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    # Garante que o AnyIO use o backend apropriado para testes assíncronos
    return "asyncio"

@pytest.fixture(scope="session")
async def client():
    """Fixture para um cliente assíncrono do FastAPI (HTTPX)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client