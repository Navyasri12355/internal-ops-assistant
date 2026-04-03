"""
Embedder
--------
Generates vector embeddings using HuggingFace sentence-transformers.
Runs fully locally — no API key required.
"""

from typing import List
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """Embed a list of strings. Returns list of float vectors."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]
