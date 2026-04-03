"""Integration tests for the FastAPI endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
async def test_health():
    with patch("backend.vector_store.chroma_client.ChromaStore"), \
         patch("backend.vector_store.embedder.Embedder"), \
         patch("backend.rag_engine.chain.RAGChain"):
        from backend.api.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
