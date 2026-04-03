# KnowledgeAgent - RAG-Powered Internal AI for Startup Scalability

> *Automating Internal Operations: Prototyping a RAG-Driven AI Agent for Scalable Knowledge Management in High-Growth Startups*

---

## Research Problems

This project investigates two interconnected research problems:

**RQ1 — Time & Resource Allocation:**  
*To what extent does automating employee onboarding via a RAG-based knowledge agent reduce the operational burden on senior engineering and HR teams in high-growth startups?*

**RQ2 — Accuracy & Information Retrieval:**  
*How does the implementation of a vector-based RAG system improve the speed and accuracy of internal knowledge retrieval compared to traditional keyword-based intranet searches as a startup scales its documentation?*

---

## What This Project Does

KnowledgeAgent is a Retrieval-Augmented Generation (RAG) system that allows startup employees to ask natural language questions and receive accurate, cited answers sourced directly from internal documents - PDFs, Notion exports, Markdown wikis, HR policies, and more.

Instead of a new hire pinging a senior engineer on Slack to ask *"what's our deployment process?"* or *"where's the leave policy?"*, they ask the agent. The agent retrieves the exact relevant chunk from your documentation and synthesizes a grounded answer — with a citation pointing back to the source document.

This solves a real, expensive problem: **as startups scale, knowledge retrieval doesn't scale with them.** Human experts become bottlenecks. Onboarding costs grow linearly with headcount. KnowledgeAgent is designed to break that linear dependency while keeping data private and inference costs at $0 using open-weights models.

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                        React + Vite UI                      │
│              (Chat interface, citation viewer)              │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼───────────────────────────────────┐
│                     FastAPI Backend                        │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│  │ Data Pipeline│   │  RAG Engine  │   │  Query Router   │ │
│  │  (Ingestion) │   │  (LangChain) │   │  (Retrieval +   │ │
│  │  PDF / MD /  │   │              │   │   Generation)   │ │
│  │  Notion docs │   │              │   │                 │ │
│  └──────┬───────┘   └──────┬───────┘   └────────┬────────┘ │
└─────────┼──────────────────┼────────────────────┼──────────┘
          │                  │                    │
┌─────────▼──────────────────▼────────────────────▼──────────┐
│                      ChromaDB (Vector Store)               │
│              Embeddings: HuggingFace all-MiniLM-L6-v2      │
└────────────────────────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    LLM (Gemma 4)    │
              │  (Local via Ollama) │
              └─────────────────────┘
```

### Data Flow
- **Ingest** - Documents (PDFs, Markdown, Notion exports) are parsed, cleaned, and chunked  
- **Embed** - Each chunk is converted to a vector embedding and stored in ChromaDB  
- **Retrieve** - On user query, the top-k most semantically similar chunks are fetched  
- **Generate** - The Gemma 4 model synthesizes an answer grounded only in the retrieved context  
- **Cite** - The UI surfaces the source document + page/chunk for every answer  

---

## Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React 18, Vite, TailwindCSS |
| Backend | Python 3.11, FastAPI |
| RAG Orchestration | LangChain |
| Vector Database | ChromaDB (local) |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| LLM | Google Gemma 4 (via Ollama) |
| Document Parsing | PyMuPDF, python-docx, markdown |
| Testing | Pytest, Vitest |

---

## Project Structure

```
rag-agent/
├── backend/
│   ├── data_pipeline/
│   ├── vector_store/
│   ├── rag_engine/
│   └── api/
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── lib/
├── docs/
├── scripts/
├── tests/
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama
- (Optional) Docker

### LLM Setup (Local Inference)

```bash
ollama run gemma4
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

python scripts/ingest.py --docs ../docs/

uvicorn api.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker (Full Stack)

```bash
docker-compose up --build
```

---

## Evaluation Metrics

| Metric | Description |
|-------|-------------|
| Query Resolution Time | RAG agent vs. manual PDF search (seconds) |
| Answer Accuracy | Compared against ground truth Q&A pairs |
| Concurrency Scalability | Latency under 10 / 100 / 500 users |
| Retrieval Precision@k | Fraction of top-k chunks that are relevant |
| Cost Savings vs API | Local Gemma 4 vs managed API per 1k queries |
| HR Time Saved | Estimated hours/week freed |

---

## Sample Use Cases

- "What is our policy on remote work?"
- "Summarize the deployment checklist for new engineers."
- "What equity vesting schedule do we offer?"
- "How do I request access to the production database?"

---

## License

MIT
