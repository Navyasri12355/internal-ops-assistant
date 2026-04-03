"""Tests for the document ingestor."""
import os
import tempfile
import pytest
from backend.data_pipeline.ingestor import load_txt, chunk_documents, ingest_directory


def test_load_txt():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello world. This is a test document.")
        path = f.name
    try:
        docs = load_txt(path)
        assert len(docs) == 1
        assert "Hello world" in docs[0]["content"]
        assert docs[0]["metadata"]["filetype"] == "txt"
    finally:
        os.unlink(path)


def test_chunk_documents():
    docs = [{"content": "A " * 600, "metadata": {"source": "test.txt", "page": 1, "filetype": "txt"}}]
    chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=10)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk["metadata"]["chunk_index"] == i
        assert "source" in chunk["metadata"]


def test_chunk_preserves_metadata():
    docs = [{"content": "Sample text.", "metadata": {"source": "doc.pdf", "page": 3, "filetype": "pdf"}}]
    chunks = chunk_documents(docs)
    assert chunks[0]["metadata"]["source"] == "doc.pdf"
    assert chunks[0]["metadata"]["page"] == 3
