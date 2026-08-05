# AI-Powered Intelligent Chatbot — System Architecture

## 1. Overview

This document describes the architecture for an **AI-Powered Intelligent Chatbot** that answers natural-language questions from organization-specific documents (PDFs, manuals, reports, policies, FAQs) using **Retrieval-Augmented Generation (RAG)**.

The system combines **Large Language Models (LLMs)** with a **vector search pipeline** to:
- Ingest and parse uploaded documents
- Chunk and embed content into a vector index
- Retrieve the most relevant chunks for a user query
- Generate accurate, context-aware answers with conversation history
- Support multilingual interaction and scalable deployment

---

## 2. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Web UI)                         │
│        React + Vite / vanilla JS + Tailwind                       │
│         • Chat window (streaming)                                 │
│         • Document upload manager                                 │
│         • Conversation history sidebar                            │
└───────────────────────────────┬────────────────────────────────────┘
                                │  REST / WebSocket (SSE)
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY / PROXY                        │
│                 Auth (JWT), Rate limiting, Static                  │
└───────────────────────────────┬────────────────────────────────────┘
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Uvicorn)                    │
│                                                                   │
│   ┌──────────────┐   ┌───────────────┐   ┌───────────────────┐    │
│   │  Chat Routes │   │ Document API  │   │  Health / Session │    │
│   │ /api/chat    │   │ /api/docs     │   │  /api/health      │    │
│   └──────┬───────┘   └───────┬───────┘   └───────────────────┘    │
│          │                   │                                    │
│          ▼                   ▼                                    │
│   ┌──────────────────────────────────────────────┐                │
│   │            RAG ORCHESTRATOR                  │                │
│   │  • Builds pipeline per request/session       │                │
│   │  • Coordinates retrieval + generation        │                │
│   └───────┬───────────────────────────┬──────────┘                │
│           │                           │                           │
│           ▼                           ▼                           │
│   ┌──────────────────┐       ┌────────────────────┐               │
│   │  INGESTION       │       │   INFERENCE        │               │
│   │  • Parse         │       │  • Embed query     │               │
│   │  • Chunk         │       │  • Vector search   │               │
│   │  • Embed         │       │  • Re-rank         │               │
│   │  • Index         │       │  • Prompt assembly │               │
│   └──────────────────┘       └────────────────────┘               │
└───────────────┬───────────────────────────┬───────────────────────┘
                │                           │
                ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │  Vector Store   │        │  Document Store │
        │  (ChromaDB)     │        │  (SQLite/Post)  │
        │  chunks+vectors │        │  metadata+files │
        └─────────────────┘        └─────────────────┘
                │                           │
                ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Embedding Model │        │   LLM (local /  │
        │ (sentence-trans │        │  OpenAI / cloud)│
        │  formers/OpenAI)│        │                 │
        └─────────────────┘        └─────────────────┘
```

---

## 3. Component Descriptions

### 3.1 Frontend
- **Stack:** React + Vite, Tailwind CSS (or plain HTML/JS for simplicity)
- **Responsibilities:**
  - Render chat messages with streaming (SSE)
  - Upload documents and show parsing status
  - Manage conversation sessions
  - Multi-language UI toggles

### 3.2 Backend (FastAPI)
- **Stack:** Python 3.11+, FastAPI, Uvicorn
- **Responsibilities:**
  - Expose REST endpoints for chat, documents, health
  - Host the RAG orchestrator
  - Handle authentication and rate limiting
  - Serve static frontend build (in production)

### 3.3 RAG Orchestrator
Coordinates the retrieval and generation pipeline for each query:
1. Take user query + conversation history
2. Embed the query
3. Retrieve top-K relevant chunks from vector store
4. (Optional) Re-rank chunks for precision
5. Assemble prompt with retrieved context + history
6. Call LLM to generate answer
7. Return answer (optionally streamed)

### 3.4 Ingestion Pipeline
Handles document upload → indexed knowledge:
1. **Parse:** Extract raw text from PDF/DOCX/TXT/MD using `pypdf`/`python-docx`
2. **Chunk:** Split text into overlapping chunks (~500 tokens) using a recursive character splitter
3. **Embed:** Convert each chunk to a dense vector via the configured embedding model
4. **Index:** Store vectors + metadata in ChromaDB, store document metadata in the document store

### 3.5 Vector Store
- **ChromaDB** (local, file-based) — stores chunk text, embeddings, and metadata (document id, chunk index, source).
- Alternative/pluggable: FAISS, Qdrant, pgvector.

### 3.6 Document Store
- **SQLite via SQLAlchemy** (default) or PostgreSQL — stores document metadata, status, and conversation messages.
- PostgreSQL recommended for production (better concurrency, JSON support).

### 3.7 LLM & Embeddings
Two modes, configurable via `.env`:

| Mode | LLM | Embeddings | Notes |
|------|-----|-----------|-------|
| **Local (default)** | Ollama (`llama3`) | `sentence-transformers/all-MiniLM-L6-v2` | Free, offline, no API keys |
| **Cloud (optional)** | OpenAI (`gpt-4o`/`gpt-3.5-turbo`) | OpenAI `text-embedding-3-small` | Requires `OPENAI_API_KEY` |

---

## 4. Data Flow Diagrams

### 4.1 Document Ingestion Flow
```
[User uploads file]
        │
        ▼
[POST /api/documents] ──► [Validate type/size]
        │
        ▼
[Save file to disk] ──► [Parse text] ──► [Chunk text]
        │
        ▼
[Embed chunks] ──► [Store in ChromaDB] ──► [Update doc status]
        │
        ▼
[Return document_id + status]
```

### 4.2 Chat Query Flow
```
[User sends message]
        │
        ▼
[POST /api/chat] ──► [Load conversation history]
        │
        ▼
[Embed query] ──► [Vector search top-K] ──► [Re-rank (optional)]
        │
        ▼
[Assemble prompt: system + history + context + query]
        │
        ▼
[LLM generate] ──► [Stream tokens via SSE]
        │
        ▼
[Save user + assistant messages] ──► [Return answer]
```

---

## 5. Data Models

### 5.1 Document
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `filename` | str | Original uploaded filename |
| `filepath` | str | Stored path on disk |
| `filetype` | str | pdf/docx/txt/md |
| `status` | str | pending/processing/ready/failed |
| `chunk_count` | int | Number of chunks indexed |
| `created_at` | datetime | Upload time |

### 5.2 Conversation
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `title` | str | Auto-generated title |
| `created_at` | datetime | Created time |
| `updated_at` | datetime | Last activity |

### 5.3 Message
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `conversation_id` | UUID | FK → conversation |
| `role` | str | user/assistant |
| `content` | str | Message text |
| `created_at` | datetime | Timestamp |

---

## 6. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/documents` | Upload & process a document (multipart) |
| `GET` | `/api/documents` | List uploaded documents |
| `DELETE` | `/api/documents/{id}` | Delete document + its chunks |
| `POST` | `/api/chat` | Send chat message (SSE streaming) |
| `GET` | `/api/conversations` | List conversations |
| `GET` | `/api/conversations/{id}/messages` | Get messages in a conversation |

---

## 7. Security & Scalability

### Security
- **JWT** authentication for API access (optional, configurable)
- **File validation**: restrict extensions, cap file size
- **Input sanitization** of prompts
- **Rate limiting** per IP/user
- **CORS** policy locked to known frontend origins

### Scalability
- **Stateless API** → horizontal scaling behind a load balancer
- **Async ingestion** with a worker queue (Celery/RQ) for large documents
- **PostgreSQL** for shared state in multi-instance deployments
- **Streaming** responses reduce perceived latency
- Multi-instance: embed model + vector store shared via network storage

---

## 8. Deployment

### Docker Compose (recommended)
```
services:
  backend:      # FastAPI app
  frontend:     # static build served by Nginx
  vectorstore:  # ChromaDB (or in-memory within backend)
  db:           # PostgreSQL
  llm:          # Ollama (optional, local mode)
```

### Local Development
```bash
# Backend
cd chatbot/backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 9. Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic |
| RAG | LangChain (or custom) pipelines |
| Parsing | pypdf, python-docx |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | sentence-transformers (local) / OpenAI (cloud) |
| Vector DB | ChromaDB |
| Document/History Store | SQLite (dev) / PostgreSQL (prod), SQLAlchemy |
| LLM | Ollama (local) / OpenAI (cloud) |
| Frontend | React + Vite + Tailwind (or plain HTML/JS) |
| Deployment | Docker, Docker Compose, Nginx |

---

## 10. Future Enhancements
- **Multi-modal documents** (images, scanned PDFs → OCR)
- **Fine-tuned retrieval** with hybrid search (BM25 + dense)
- **Feedback loop** (thumbs up/down to improve answers)
- **Multi-tenancy** with per-organization document isolation
- **Streaming with citations** (link to source chunks)
- **Webhooks** / Slack / Teams integration
