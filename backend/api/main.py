"""
FastAPI Application
-------------------
Exposes REST endpoints for the RAG agent.
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import shutil

from vector_store.chroma_client import ChromaStore
from vector_store.embedder import Embedder
from data_pipeline.ingestor import load_document, chunk_documents, ingest_directory
from rag_engine.chain import RAGChain


# --- App State ---
store: Optional[ChromaStore] = None
embedder: Optional[Embedder] = None
rag_chain: Optional[RAGChain] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store, embedder, rag_chain
    print("Initializing KnowledgeAgent...")
    embedder = Embedder(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    store = ChromaStore(
        persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
        collection_name=os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base"),
    )
    rag_chain = RAGChain()

    # Auto-ingest documents from ./docs/ if the store is empty
    if store.count() == 0:
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "docs")
        docs_dir = os.path.abspath(docs_dir)
        if os.path.isdir(docs_dir):
            print(f"\nIngesting documents from: {docs_dir}")
            chunk_size = int(os.getenv("CHUNK_SIZE", 500))
            chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
            all_chunks = ingest_directory(docs_dir, chunk_size, chunk_overlap)
            print(f"\nTotal chunks created: {len(all_chunks)}")

            if all_chunks:
                embeddings = embedder.embed([c["content"] for c in all_chunks])
                count = store.upsert(all_chunks, embeddings)
                print(f"Done. Stored {count} chunks.")
            else:
                print("No chunks created from documents.")
        else:
            print(f"Docs directory not found at {docs_dir}, skipping auto-ingest.")

    print(f"Ready. Vector store has {store.count()} chunks.")
    yield
    print("Shutting down.")


app = FastAPI(title="KnowledgeAgent API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class ChunkResult(BaseModel):
    content: str
    source: str
    page: int
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[ChunkResult]
    question: str


class StatusResponse(BaseModel):
    chunk_count: int
    sources: List[str]


# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status", response_model=StatusResponse)
def status():
    return StatusResponse(
        chunk_count=store.count(),
        sources=store.list_sources(),
    )


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if store.count() == 0:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Upload documents first.")

    query_embedding = embedder.embed_one(req.question)
    top_k = int(os.getenv("TOP_K_RESULTS", req.top_k))
    chunks = store.query(query_embedding, top_k=top_k)

    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")

    answer = rag_chain.generate(req.question, chunks)

    sources = [
        ChunkResult(
            content=c["content"],
            source=c["metadata"].get("source", "Unknown"),
            page=c["metadata"].get("page", 0),
            score=c["score"],
        )
        for c in chunks
    ]

    return QueryResponse(answer=answer, sources=sources, question=req.question)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    allowed_exts = {".pdf", ".md", ".markdown", ".docx", ".txt"}
    ext = "." + file.filename.split(".")[-1].lower()

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
        docs = load_document(tmp_path)
        # Preserve original filename in metadata
        for doc in docs:
            doc["metadata"]["source"] = file.filename
        chunks = chunk_documents(docs, chunk_size, chunk_overlap)
        embeddings = embedder.embed([c["content"] for c in chunks])
        count = store.upsert(chunks, embeddings)
        return {"message": f"Ingested {count} chunks from {file.filename}"}
    finally:
        import os as _os
        _os.unlink(tmp_path)
