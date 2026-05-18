---
title: MultiSense RAG
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# MultiSense RAG - Multimodal Document Intelligence Platform

A production-grade Retrieval-Augmented Generation (RAG) system with multi-agent orchestration, self-critique loops, and an automated evaluation harness.

Built to go beyond basic RAG demos----> this system knows when its answers are bad and retries automatically.

---

## Benchmark Results

Evaluated on 3 questions from the "Attention Is All You Need" paper using RAGAS:

| Metric | Score |
|---|---|
| Faithfulness | 0.89 |
| Answer Relevancy | 0.84 |
| Context Recall | 1.00 |

---

## Architecture

```
Question
   │
   ▼
[Router Agent]     — classifies intent (factual / summary / comparison)
   │
   ▼
[Retrieval Agent]  — vector search via Chroma + sentence-transformers
   │
   ▼
[Synthesis Agent]  — generates grounded answer using retrieved chunks
   │
   ▼
[Critique Agent]   — scores answer quality, retries if verdict is RETRY
   │
   ▼
Answer
```

---

## Key Features

- Multi-agent orchestration via LangGraph stateful graph
- Self-critique loop - automatically retries poor answers up to 2 times
- Intent-aware retrieval - summary queries fetch more chunks than factual ones
- RAGAS eval harness - faithfulness, answer relevancy, context recall scored automatically
- FastAPI service - typed endpoints for ingestion and querying
- 100% free stack - Groq LLM, local embeddings, Chroma vector store

---

## Tech Stack

| Component | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Groq (llama-3.3-70b-versatile) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector store | Chroma (local) |
| Evaluation | RAGAS |
| API | FastAPI |
| Tracing | LangSmith |

---

## Project Structure

```
multisense-rag/
├── src/
│   ├── ingestion/       # PDF loading, chunking, embedding
│   ├── agents/          # LangGraph multi-agent graph
│   ├── retrieval/       # Vector store + similarity search
│   └── api/             # FastAPI endpoints
├── evals/               # RAGAS evaluation suite
├── tests/
└── README.md
```

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/multisense-rag
cd multisense-rag
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Add environment variables
cp .env.example .env
# Fill in GROQ_API_KEY and LANGCHAIN_API_KEY

# 3. Ingest a document
python -m src.ingestion.pipeline

# 4. Run the API
uvicorn src.api.main:app --reload

# 5. Run evals
pytest evals/ -s
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/ingest` | Upload and index a PDF |
| POST | `/query` | Ask a question, get a grounded answer |

---

## What This Demonstrates

- Production RAG patterns beyond basic retrieval
- Multi-agent system design with LangGraph
- LLM evaluation methodology (RAGAS metrics)
- FastAPI service design with typed request/response models
- LLMOps observability with LangSmith tracing
