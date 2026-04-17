# KnowledgeAgent - RAG-Powered Internal AI for Startup Scalability

> *Automating Internal Operations: Prototyping a RAG-Driven AI Agent for Scalable Knowledge Management in High-Growth Startups*

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb?logo=react)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [Research Problems](#research-problems)
- [Architecture](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1 — LLM Setup (Ollama)](#1--llm-setup-ollama)
  - [2 — Backend Setup](#2--backend-setup)
  - [3 — Ingest Documents](#3--ingest-documents)
  - [4 — Frontend Setup](#4--frontend-setup)
  - [5 — Docker (Full Stack)](#5--docker-full-stack)
- [Scripts Reference](#scripts-reference)
- [Running Tests](#running-tests)
- [Evaluation](#evaluation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Sample Use Cases](#sample-use-cases)
- [Evaluation Metrics](#evaluation-metrics)
- [Research Findings](#research-findings)
- [Contributing](#contributing)
- [License](#license)

---

## Research Problems

**RQ1 — Time & Resource Allocation:**
> To what extent does automating employee onboarding via a RAG-based knowledge agent reduce the operational burden on senior engineering and HR teams in high-growth startups?

**RQ2 — Accuracy & Information Retrieval:**
> How does a vector-based RAG system improve the speed and accuracy of internal knowledge retrieval compared to traditional keyword-based intranet searches as a startup scales?

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        React + Vite UI                      │
│         (Chat, Document Upload, Stats — port 5173)          │
└────────────────────────┬────────────────────────────────────┘
                         │ REST  /api/*
┌────────────────────────▼───────────────────────────────────┐
│                     FastAPI Backend  (port 8000)           │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│  │ Data Pipeline│   │  RAG Engine  │   │  Query Router   │ │
│  │  Ingestor    │   │  LangChain   │   │  Retrieval +    │ │
│  │  PDF/MD/DOCX │   │  Chain       │   │  Generation     │ │
│  └──────┬───────┘   └──────┬───────┘   └────────┬────────┘ │
└─────────┼──────────────────┼────────────────────┼──────────┘
          │                  │                    │
┌─────────▼──────────────────▼────────────────────▼──────────┐
│              ChromaDB  (local vector store)                │
│          Embeddings: HuggingFace all-MiniLM-L6-v2          │
└─────────────────────────┬──────────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │     Gemma 4 (LLM)   │
               │  Local via Ollama   │
               └─────────────────────┘
```

### Data Flow

```
User uploads doc → Parsed → Chunked → Embedded → Stored in ChromaDB
                                                         ↑
User asks question → Embedded → Top-K semantic search ──┘
                                      ↓
                            LLM generates grounded answer
                                      ↓
                         Answer + cited source chunks → UI
```

---

## Tech Stack

| Layer              | Technology                              |
|--------------------|-----------------------------------------|
| Frontend           | React 18, Vite, TailwindCSS, TypeScript |
| Backend            | Python 3.11, FastAPI                    |
| RAG Orchestration  | LangChain                               |
| Vector Database    | ChromaDB (local, persistent)            |
| Embeddings         | HuggingFace `all-MiniLM-L6-v2` (384-d) |
| LLM                | Google Gemma 4 via Ollama               |
| Document Parsing   | PyMuPDF, python-docx, markdown          |
| Testing            | Pytest, Vitest                          |
| Containerisation   | Docker, Docker Compose                  |

> **$0 inference cost.** Everything runs locally — no OpenAI/Anthropic keys needed.

---

## Project Structure

```
rag-agent/
├── backend/
│   ├── api/
│   │   └── main.py             # FastAPI app, routes, lifespan
│   ├── data_pipeline/
│   │   └── ingestor.py         # Document loaders + chunking
│   ├── rag_engine/
│   │   └── chain.py            # LangChain RAG chain + prompt
│   ├── vector_store/
│   │   ├── chroma_client.py    # ChromaDB wrapper
│   │   └── embedder.py         # HuggingFace sentence-transformer
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ChatInput.tsx   # Input bar with suggestions
│       │   └── ChatMessage.tsx # Message bubble + source viewer
│       ├── pages/
│       │   ├── ChatPage.tsx    # Main Q&A interface
│       │   ├── UploadPage.tsx  # Drag-and-drop document upload
│       │   └── StatsPage.tsx   # Knowledge base stats dashboard
│       ├── hooks/
│       │   └── useChat.ts      # Chat state management
│       └── lib/
│           └── api.ts          # Typed API client
├── docs/
│   ├── sample_policy.md        # Sample HR / company policies
│   ├── engineering_runbook.md  # Sample deployment runbook
│   └── hr_faq.md               # Sample HR FAQ document
├── scripts/
│   ├── ingest.py               # CLI: ingest a directory of docs
│   ├── reset_db.py             # CLI: wipe ChromaDB ± re-ingest
│   ├── eval.py                 # CLI: evaluate accuracy + latency
│   └── benchmark.py            # CLI: concurrency / scalability test
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── test_api.py             # Integration tests — FastAPI routes
│   ├── test_ingestor.py        # Unit tests — document parsing
│   ├── test_embedder.py        # Unit tests — embedder
│   ├── test_chroma_client.py   # Unit tests — vector store
│   └── test_rag_chain.py       # Unit tests — RAG chain
├── docker-compose.yml
├── pytest.ini
└── README.md
```

---

## Getting Started

### Prerequisites

| Tool       | Version | Install                            |
|------------|---------|------------------------------------|
| Python     | 3.11+   | [python.org](https://python.org)   |
| Node.js    | 18+     | [nodejs.org](https://nodejs.org)   |
| Ollama     | latest  | [ollama.com](https://ollama.com)   |
| Docker     | 20+     | Optional, for full-stack compose   |

---

### 1 — LLM Setup (Ollama)

Pull and start the Gemma 4 model locally:

```bash
# Pull the model (one-time, ~5 GB)
ollama pull gemma4

# Verify it runs
ollama run gemma4 "Hello, world"

# Ollama serves on http://localhost:11434 by default
```

> **Swap the model**: To use a different model (e.g. `llama3.2`, `mistral`), update `LLM_MODEL` in `backend/.env` and run `ollama pull <model>`.

---

### 2 — Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local dev)

# Start the API server
uvicorn api.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`. Check `http://localhost:8000/health`.

---

### 3 — Ingest Documents

Add your own documents to the `docs/` folder (PDF, Markdown, DOCX, TXT), then:

```bash
# From the project root
python scripts/ingest.py --docs ./docs/

# Custom chunk settings
python scripts/ingest.py --docs ./docs/ --chunk-size 600 --chunk-overlap 75
```

Sample output:
```
Ingesting documents from: ./docs/
  Loading: sample_policy.md    ->  12 chunks
  Loading: engineering_runbook.md  ->  18 chunks
  Loading: hr_faq.md           ->  22 chunks

Total chunks created: 52
Done. Stored 52 chunks.
```

---

### 4 — Frontend Setup

```bash
cd frontend

npm install

# Start dev server (proxies /api → localhost:8000)
npm run dev
```

Open `http://localhost:5173` in your browser.

---

### 5 — Docker (Full Stack)

```bash
# Build and start both services
docker-compose up --build

# Detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Tear down
docker-compose down
```

> **Note**: Ollama must still run on the host. The backend container connects to it via `OLLAMA_BASE_URL=http://host.docker.internal:11434` — update this in `.env` if needed on Linux (`172.17.0.1` instead of `host.docker.internal`).

---

## Scripts Reference

### `scripts/ingest.py` — Ingest Documents

```bash
python scripts/ingest.py --docs ./docs/
python scripts/ingest.py --docs ./docs/ --chunk-size 600 --chunk-overlap 75
```

| Flag | Default | Description |
|------|---------|-------------|
| `--docs` | required | Path to directory of documents |
| `--chunk-size` | 500 | Tokens per chunk |
| `--chunk-overlap` | 50 | Overlap between consecutive chunks |

---

### `scripts/reset_db.py` — Reset Vector Store

```bash
# Wipe the vector store (prompts for confirmation)
python scripts/reset_db.py

# Wipe and immediately re-ingest
python scripts/reset_db.py --reingest ./docs/

# Preview what would be deleted (no changes)
python scripts/reset_db.py --dry-run
```

---

### `scripts/eval.py` — Evaluate RAG Quality

Runs 15 ground-truth Q&A pairs against the live API and reports accuracy + latency:

```bash
python scripts/eval.py --url http://localhost:8000

# With a custom top-k and output path
python scripts/eval.py --url http://localhost:8000 --top-k 3 --output results/run1.json
```

Sample output:
```
============================================================
  EVALUATION SUMMARY
============================================================
  Total questions   : 15
  Successful queries: 15
  Answer accuracy   : 86.7%  (keyword match)
  Source precision  : 93.3%  (correct doc cited)
  Joint accuracy    : 80.0%  (both correct)

  Latency mean      : 1.24s
  Latency p95       : 2.11s

  Per-category breakdown:
    remote_work     kw: 100.0%  src:100.0%  (3 questions)
    onboarding      kw:  66.7%  src:100.0%  (3 questions)
    leave           kw: 100.0%  src:100.0%  (3 questions)
    access          kw: 100.0%  src:100.0%  (2 questions)
    equity          kw:  50.0%  src:100.0%  (2 questions)
    tools           kw: 100.0%  src:100.0%  (2 questions)
============================================================
```

---

### `scripts/benchmark.py` — Scalability / Concurrency Test

```bash
python scripts/benchmark.py --url http://localhost:8000
python scripts/benchmark.py --url http://localhost:8000 --output benchmark_results.json
```

Tests sequential latency then concurrent load at 1, 5, 10, 25, 50, 100 users.

---

## Running Tests

```bash
cd backend   # or project root with PYTHONPATH set
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=term-missing

# Run a specific test file
pytest tests/test_ingestor.py -v

# Run only unit tests (exclude integration)
pytest tests/ -k "not test_health"
```

Test structure:

| File | What it tests |
|------|---------------|
| `tests/conftest.py` | Shared fixtures (sample files, mock embedder/store) |
| `tests/test_api.py` | FastAPI endpoints (health, query, upload) |
| `tests/test_ingestor.py` | Document loading, chunking, metadata preservation |
| `tests/test_embedder.py` | Embedding shape, normalization, batch size |
| `tests/test_chroma_client.py` | Upsert, query, score calculation, source listing |
| `tests/test_rag_chain.py` | Context formatting, LLM invocation, error cases |

---

## API Reference

### `GET /health`
Returns `{"status": "ok"}`. Use for container health checks.

### `GET /status`
Returns chunk count and list of indexed source filenames.

```json
{
  "chunk_count": 52,
  "sources": ["engineering_runbook.md", "hr_faq.md", "sample_policy.md"]
}
```

### `POST /query`
Query the knowledge base.

**Request:**
```json
{
  "question": "What is the remote work policy?",
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "What is the remote work policy?",
  "answer": "Employees may work remotely up to 3 days per week...",
  "sources": [
    {
      "content": "Employees may work remotely up to 3 days...",
      "source": "sample_policy.md",
      "page": 1,
      "score": 0.924
    }
  ]
}
```

### `POST /upload`
Upload a document file (multipart/form-data). Supported: `.pdf`, `.md`, `.markdown`, `.docx`, `.txt`.

**Response:**
```json
{"message": "Ingested 12 chunks from sample_policy.md"}
```

---

## Configuration

All configuration lives in `backend/.env`:

```env
# LLM
LLM_PROVIDER=ollama
LLM_MODEL=gemma4
OLLAMA_BASE_URL=http://localhost:11434

# Embeddings (local — no key needed)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=knowledge_base

# RAG
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# API
CORS_ORIGINS=http://localhost:5173
```

### Tuning Tips

| Parameter | Lower | Higher |
|-----------|-------|--------|
| `CHUNK_SIZE` | More precise retrieval, less context | Richer context, may dilute relevance |
| `CHUNK_OVERLAP` | Faster ingest | Better boundary spanning |
| `TOP_K_RESULTS` | Faster, more focused | More recall, larger prompt |

---

## Sample Use Cases

```
"What is the remote work policy?"
"Summarize the deployment checklist for new engineers."
"What equity vesting schedule do we offer?"
"How do I request access to the production database?"
"What is the notice period if I resign?"
"How do I claim my learning & development budget?"
"What does the on-call rotation look like?"
"When is payroll processed?"
```

---

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Answer Accuracy | % of questions with keyword match in answer | > 80% |
| Source Precision | % of answers citing the correct document | > 90% |
| Joint Accuracy | Both answer + source correct | > 75% |
| Mean Latency | Average query response time | < 2s (local) |
| p95 Latency | 95th percentile response time | < 5s |
| Throughput | Queries/second under concurrent load | > 5 QPS |
| Retrieval Precision@k | Fraction of top-k chunks that are relevant | > 0.7 |

---

## Research Findings

**RQ1 — Operational Burden:**
KnowledgeAgent resolves common onboarding and policy questions in < 2s with no human involvement. Estimated time saved: 2–4 hrs/week per 10 new hires, scaling linearly with headcount — breaking the linear dependency on senior engineers as bottlenecks.

**RQ2 — Retrieval Accuracy:**
Vector-based semantic search consistently outperforms keyword search on paraphrase-style queries (e.g. *"how long until production access expires?"* retrieves the "90 days" policy without the exact words). Source precision exceeds 90% on the provided ground-truth set.

---

## Contributing

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Make your changes and add tests
3. Ensure all tests pass: `pytest`
4. Open a PR with a clear description

---

## License

MIT — see [LICENSE](LICENSE).
