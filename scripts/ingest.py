"""
CLI script: ingest a directory of documents into ChromaDB.

Usage:
    python scripts/ingest.py --docs ./docs/
    python scripts/ingest.py --docs ./docs/ --chunk-size 600 --chunk-overlap 75
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from backend.data_pipeline.ingestor import ingest_directory
from backend.vector_store.chroma_client import ChromaStore
from backend.vector_store.embedder import Embedder


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG knowledge base.")
    parser.add_argument("--docs", required=True, help="Path to directory containing documents")
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--chunk-overlap", type=int, default=50)
    args = parser.parse_args()

    print(f"\nIngesting documents from: {args.docs}")
    chunks = ingest_directory(args.docs, args.chunk_size, args.chunk_overlap)
    print(f"\nTotal chunks created: {len(chunks)}")

    print("\nLoading embedding model...")
    embedder = Embedder(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))

    print("Generating embeddings...")
    texts = [c["content"] for c in chunks]
    embeddings = embedder.embed(texts)

    print("Storing in ChromaDB...")
    store = ChromaStore(
        persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
        collection_name=os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base"),
    )
    count = store.upsert(chunks, embeddings)

    print(f"\nDone. Stored {count} chunks.")
    print(f"Total in collection: {store.count()}")
    print(f"Sources: {store.list_sources()}")


if __name__ == "__main__":
    main()
