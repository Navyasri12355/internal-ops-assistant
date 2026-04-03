"""
ChromaDB Client
---------------
Wraps ChromaDB operations: create collection, upsert chunks, query by embedding.
"""

import uuid
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings


class ChromaStore:
    def __init__(self, persist_dir: str, collection_name: str):
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        """Insert or update chunks with their embeddings."""
        ids = [str(uuid.uuid4()) for _ in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(ids)

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k most similar chunks for a query embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "content": doc,
                "metadata": meta,
                "score": round(1 - dist, 4),  # cosine similarity
            })
        return output

    def count(self) -> int:
        return self.collection.count()

    def delete_collection(self):
        self.client.delete_collection(self.collection.name)

    def list_sources(self) -> List[str]:
        """Return unique source filenames in the collection."""
        results = self.collection.get(include=["metadatas"])
        sources = {m["source"] for m in results["metadatas"] if "source" in m}
        return sorted(sources)
