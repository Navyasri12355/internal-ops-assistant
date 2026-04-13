"""
Shared pytest fixtures for KnowledgeAgent tests.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch


# ── Env defaults ──────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLM_MODEL", "gemma4")
    monkeypatch.setenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/test_chroma")
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_collection")
    monkeypatch.setenv("CHUNK_SIZE", "500")
    monkeypatch.setenv("CHUNK_OVERLAP", "50")
    monkeypatch.setenv("TOP_K_RESULTS", "5")


# ── Sample document fixtures ──────────────────────────────────────────────────
@pytest.fixture
def sample_txt_file():
    content = (
        "Remote Work Policy\n\n"
        "Employees may work remotely up to 3 days per week. "
        "Full remote arrangements require VP approval. "
        "All remote employees must be available during core hours (10am–4pm IST)."
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def sample_md_file():
    content = (
        "# Leave Policy\n\n"
        "Employees receive 24 days of paid leave per year.\n"
        "Leave must be requested at least 5 business days in advance via the HR portal."
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def sample_chunks():
    return [
        {
            "content": "Employees may work remotely up to 3 days per week.",
            "metadata": {"source": "policy.pdf", "page": 1, "filetype": "pdf", "chunk_index": 0},
            "score": 0.92,
        },
        {
            "content": "Full remote arrangements require VP approval and are reviewed quarterly.",
            "metadata": {"source": "policy.pdf", "page": 1, "filetype": "pdf", "chunk_index": 1},
            "score": 0.85,
        },
        {
            "content": "All remote employees must be available during core hours (10am–4pm IST).",
            "metadata": {"source": "policy.pdf", "page": 2, "filetype": "pdf", "chunk_index": 2},
            "score": 0.78,
        },
    ]


@pytest.fixture
def mock_embedder():
    embedder = MagicMock()
    embedder.embed.return_value = [[0.1] * 384]
    embedder.embed_one.return_value = [0.1] * 384
    return embedder


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.count.return_value = 42
    store.list_sources.return_value = ["policy.pdf", "handbook.md"]
    return store