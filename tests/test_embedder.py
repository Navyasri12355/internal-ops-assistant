"""Tests for the Embedder class."""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np


class TestEmbedder:
    """Unit tests for the vector embedder."""

    def test_embed_returns_list_of_vectors(self):
        """embed() should return one float vector per input text."""
        with patch("backend.vector_store.embedder.SentenceTransformer") as MockST:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384])
            MockST.return_value = mock_model

            from backend.vector_store.embedder import Embedder
            embedder = Embedder("all-MiniLM-L6-v2")
            result = embedder.embed(["hello", "world"])

            assert len(result) == 2
            assert len(result[0]) == 384
            assert isinstance(result[0][0], float)

    def test_embed_one_returns_single_vector(self):
        """embed_one() should return a single float list, not nested."""
        with patch("backend.vector_store.embedder.SentenceTransformer") as MockST:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.5] * 384])
            MockST.return_value = mock_model

            from backend.vector_store.embedder import Embedder
            embedder = Embedder()
            result = embedder.embed_one("single query")

            assert isinstance(result, list)
            assert len(result) == 384
            assert not isinstance(result[0], list)

    def test_embed_empty_list(self):
        """embed() with an empty list should return an empty list."""
        with patch("backend.vector_store.embedder.SentenceTransformer") as MockST:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([]).reshape(0, 384)
            MockST.return_value = mock_model

            from backend.vector_store.embedder import Embedder
            embedder = Embedder()
            result = embedder.embed([])
            assert result == []

    def test_model_name_stored(self):
        """The model name should be accessible after init."""
        with patch("backend.vector_store.embedder.SentenceTransformer"):
            from backend.vector_store.embedder import Embedder
            embedder = Embedder("custom-model")
            assert embedder.model_name == "custom-model"

    def test_default_model_name(self):
        """Default model should be all-MiniLM-L6-v2."""
        with patch("backend.vector_store.embedder.SentenceTransformer") as MockST:
            from backend.vector_store.embedder import Embedder
            embedder = Embedder()
            MockST.assert_called_once_with("all-MiniLM-L6-v2")

    def test_embed_batch_size_passed(self):
        """encode() should be called with the batch_size parameter."""
        with patch("backend.vector_store.embedder.SentenceTransformer") as MockST:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.1] * 384])
            MockST.return_value = mock_model

            from backend.vector_store.embedder import Embedder
            embedder = Embedder()
            embedder.embed(["text"], batch_size=32)

            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs["batch_size"] == 32

    def test_embed_normalized(self):
        """Embeddings should be normalized (normalize_embeddings=True)."""
        with patch("backend.vector_store.embedder.SentenceTransformer") as MockST:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.1] * 384])
            MockST.return_value = mock_model

            from backend.vector_store.embedder import Embedder
            embedder = Embedder()
            embedder.embed(["text"])

            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs["normalize_embeddings"] is True