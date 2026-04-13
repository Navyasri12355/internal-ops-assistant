"""Tests for the ChromaStore vector store wrapper."""

import pytest
from unittest.mock import MagicMock, patch, call


@pytest.fixture
def mock_chroma_client():
    with patch("backend.vector_store.chroma_client.chromadb.PersistentClient") as MockClient:
        mock_collection = MagicMock()
        MockClient.return_value.get_or_create_collection.return_value = mock_collection
        yield MockClient, mock_collection


class TestChromaStore:
    def test_init_creates_collection(self, mock_chroma_client):
        MockClient, mock_collection = mock_chroma_client
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore(persist_dir="/tmp/chroma", collection_name="test")
        MockClient.return_value.get_or_create_collection.assert_called_once_with(
            name="test",
            metadata={"hnsw:space": "cosine"},
        )

    def test_upsert_returns_chunk_count(self, mock_chroma_client):
        _, mock_collection = mock_chroma_client
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore("/tmp/chroma", "test")
        chunks = [
            {"content": "text1", "metadata": {"source": "a.pdf", "page": 1}},
            {"content": "text2", "metadata": {"source": "a.pdf", "page": 2}},
        ]
        embeddings = [[0.1] * 384, [0.2] * 384]
        count = store.upsert(chunks, embeddings)
        assert count == 2

    def test_upsert_calls_collection_upsert(self, mock_chroma_client):
        _, mock_collection = mock_chroma_client
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore("/tmp/chroma", "test")
        chunks = [{"content": "hello", "metadata": {"source": "doc.pdf", "page": 1}}]
        embeddings = [[0.1] * 384]
        store.upsert(chunks, embeddings)

        mock_collection.upsert.assert_called_once()
        kwargs = mock_collection.upsert.call_args[1]
        assert kwargs["documents"] == ["hello"]
        assert kwargs["metadatas"] == [{"source": "doc.pdf", "page": 1}]
        assert len(kwargs["ids"]) == 1

    def test_query_returns_formatted_results(self, mock_chroma_client):
        _, mock_collection = mock_chroma_client
        from backend.vector_store.chroma_client import ChromaStore

        mock_collection.query.return_value = {
            "documents": [["chunk text"]],
            "metadatas": [[{"source": "doc.pdf", "page": 1}]],
            "distances": [[0.15]],  # cosine distance → score = 1 - 0.15 = 0.85
        }

        store = ChromaStore("/tmp/chroma", "test")
        results = store.query([0.1] * 384, top_k=1)

        assert len(results) == 1
        assert results[0]["content"] == "chunk text"
        assert results[0]["score"] == pytest.approx(0.85)
        assert results[0]["metadata"]["source"] == "doc.pdf"

    def test_query_score_is_cosine_similarity(self, mock_chroma_client):
        """Score = 1 - cosine_distance, so distance 0 → score 1.0."""
        _, mock_collection = mock_chroma_client
        from backend.vector_store.chroma_client import ChromaStore

        mock_collection.query.return_value = {
            "documents": [["text"]],
            "metadatas": [[{"source": "x"}]],
            "distances": [[0.0]],
        }
        store = ChromaStore("/tmp/chroma", "test")
        results = store.query([0.1] * 384)
        assert results[0]["score"] == 1.0

    def test_count_delegates_to_collection(self, mock_chroma_client):
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 99
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore("/tmp/chroma", "test")
        assert store.count() == 99

    def test_list_sources_deduplicates(self, mock_chroma_client):
        _, mock_collection = mock_chroma_client
        mock_collection.get.return_value = {
            "metadatas": [
                {"source": "b.pdf"},
                {"source": "a.pdf"},
                {"source": "b.pdf"},  # duplicate
            ]
        }
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore("/tmp/chroma", "test")
        sources = store.list_sources()
        assert sources == ["a.pdf", "b.pdf"]  # sorted, deduplicated

    def test_list_sources_handles_missing_source_key(self, mock_chroma_client):
        _, mock_collection = mock_chroma_client
        mock_collection.get.return_value = {
            "metadatas": [{"source": "doc.pdf"}, {"page": 1}]  # second has no "source"
        }
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore("/tmp/chroma", "test")
        sources = store.list_sources()
        assert sources == ["doc.pdf"]

    def test_delete_collection_called(self, mock_chroma_client):
        MockClient, mock_collection = mock_chroma_client
        from backend.vector_store.chroma_client import ChromaStore

        store = ChromaStore("/tmp/chroma", "test")
        store.delete_collection()
        MockClient.return_value.delete_collection.assert_called_once()