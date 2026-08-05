# Implementation Plan — AI-Powered Intelligent Chatbot (RAG)

> **Goal:** Build a scalable, RAG-based intelligent chatbot that answers natural-language questions from organization-specific documents (PDF, DOCX, TXT, MD) using LLMs, with conversation history, multilingual support, and scalable deployment.
>
> **References:** This plan is derived from `ARCHITECTURE.md` (system design) and `PROBLEM_STATEMENT.md` (requirements). It is organized into delivery phases, each with clear deliverables, tasks, and acceptance criteria.

---

## Plan Summary

| Phase | Name | Focus | Duration (est.) |
|-------|------|-------|-----------------|
| 0 | Foundation & Setup | Project scaffolding, tooling, CI | 1 week |
| 1 | Core Backend Skeleton | FastAPI app, DB, config | 1 week |
| 2 | Document Ingestion | Upload, parse, chunk, embed, index | 1–2 weeks |
| 3 | Retrieval | Vector search, scoring | 1 week |
| 4 | LLM Generation | Prompting, provider abstraction, streaming | 1–2 weeks |
| 5 | RAG Orchestration | End-to-end pipeline, conversation history | 1 week |
| 6 | API & Frontend | REST/SSE endpoints + chat UI | 2 weeks |
| 7 | Security, Auth & Rate Limiting | Hardening | 1–2 weeks |
| 8 | Testing & QA | Unit, integration, edge cases | 1–2 weeks |
| 9 | Deployment & Scaling | Docker, orchestration, monitoring | 1–2 weeks |
| 10 | Post-Launch Enhancements | Multilingual, OCR, citations, feedback | Ongoing |

**Total estimated duration:** 10–15 weeks for a single team.

---

## Phase 0 — Foundation & Setup

**Objective:** Establish project structure, tooling, and development conventions.

### Tasks
- [ ] Define repository layout (`chatbot/backend`, `chatbot/frontend`, `docs/`, `tests/`).
- [ ] Initialize Python 3.11+ environment + virtual environment.
- [ ] Create `requirements.txt` with pinned versions (FastAPI, Uvicorn, SQLAlchemy, ChromaDB, sentence-transformers, pypdf, python-docx, langchain-text-splitters, openai, httpx).
- [ ] Set up `.env.example` for all configuration.
- [ ] Configure linters/formatters (Ruff, Black), type checking (mypy).
- [ ] Set up `git` + `.gitignore` + initial commit.
- [ ] Add CI (GitHub Actions) for lint + test on push.

### Acceptance Criteria
- [ ] `pip install -r requirements.txt` succeeds.
- [ ] Codebase imports cleanly; lint passes.
- [ ] Repo structure documented in README.

---

## Phase 1 — Core Backend Skeleton

**Objective:** Stand up a running FastAPI application with configuration and database.

### Tasks
- [ ] Create `app/config.py` (Pydantic Settings) with provider, storage, vector, RAG, and server settings.
- [ ] Create `app/db/session.py` (SQLAlchemy engine, `SessionLocal`, `get_db` dependency, `init_db`).
- [ ] Create `app/db/models.py` (Document, Conversation, Message ORM models).
- [ ] Create `app/models/schemas.py` (Pydantic request/response models).
- [ ] Create `app/main.py` with CORS, lifespan DB init, and route registration.
- [ ] Add a `/api/health` endpoint.
- [ ] Add `app/api/routes/` package with empty route modules.

### Acceptance Criteria
- [ ] `uvicorn app.main:app` starts successfully.
- [ ] `GET /api/health` returns `{"status":"ok"}`.
- [ ] SQLite DB tables created on startup.

---

## Phase 2 — Document Ingestion

**Objective:** Accept document uploads and convert them into a searchable vector index.

### Tasks
- [ ] Implement `app/utils/parsers.py` — extract text from PDF/DOCX/TXT/MD.
- [ ] Implement `app/utils/chunkers.py` — chunk text with configurable size/overlap.
- [ ] Implement `app/services/embeddings.py` — embedding provider abstraction (local + OpenAI).
- [ ] Implement `app/services/vector_store.py` — ChromaDB collection add/search/delete.
- [ ] Implement `app/services/ingestion.py` — orchestrate parse → chunk → embed → index.
- [ ] Implement `app/api/routes/documents.py` — upload (multipart), list, delete.
- [ ] Add file validation (extension, size limit).
- [ ] **(Later/Phase 9)** Move ingestion to background worker.

### Acceptance Criteria
- [ ] Uploading a valid file creates a `ready` document with `chunk_count > 0`.
- [ ] Invalid/oversized/unsupported files return proper 4xx errors.
- [ ] Chunks are queryable in ChromaDB.

---

## Phase 3 — Retrieval

**Objective:** Retrieve the most relevant chunks for a user query.

### Tasks
- [ ] Implement `app/services/retrieval.py` — wrap vector store search.
- [ ] Implement query embedding + top-K search with score conversion.
- [ ] **(Edge-case)** Clamp `top_k` to collection size; handle empty collection.
- [ ] **(Edge-case)** Add minimum relevance threshold / fallback.

### Acceptance Criteria
- [ ] Given an indexed document, a related query returns relevant chunks with scores.
- [ ] Empty store returns an empty result gracefully (no crash).

---

## Phase 4 — LLM Generation

**Objective:** Generate context-aware answers via pluggable LLM providers.

### Tasks
- [ ] Implement `app/services/llm.py` — provider abstraction (Ollama local + OpenAI).
- [ ] Implement `complete()` (non-stream) and `stream()` methods.
- [ ] Implement `app/services/generation.py` — system prompt + prompt assembly + generate/stream.
- [ ] **(Edge-case)** Guard against empty context; handle LLM unavailable/timeout.
- [ ] **(Edge-case)** Token-based context/history truncation.

### Acceptance Criteria
- [ ] A query with context produces a coherent, source-grounded answer.
- [ ] Streaming yields tokens incrementally.
- [ ] Clear errors when LLM backend is down (503, not 500).

---

## Phase 5 — RAG Orchestration

**Objective:** Wire the full pipeline with conversation history.

### Tasks
- [ ] Implement `app/services/conversation.py` — get/create conversation, history, add message.
- [ ] Implement `app/services/rag_pipeline.py` — `answer_query()` and `stream_query()`.
- [ ] Persist user + assistant messages after each turn.
- [ ] **(Edge-case)** Handle LLM failure without corrupting history (rollback/save error).

### Acceptance Criteria
- [ ] End-to-end: query → retrieve → generate → respond → persist.
- [ ] Multi-turn conversations reference prior context.
- [ ] Sources returned with each answer.

---

## Phase 6 — API & Frontend

**Objective:** Expose a complete API and a usable chat UI.

### Tasks
- [ ] Implement `app/api/routes/chat.py` — `POST /api/chat` + `POST /api/chat/stream` (SSE).
- [ ] Implement `app/api/routes/conversations.py` — list convs, get messages.
- [ ] Build frontend (`chatbot/frontend`) — chat window, document upload, conversation sidebar.
- [ ] Wire SSE streaming in the frontend.
- [ ] Add document status indicators.

### Acceptance Criteria
- [ ] All endpoints documented in `/docs` (OpenAPI).
- [ ] User can upload a document and chat about it from the UI.
- [ ] Streaming responses appear incrementally.

---

## Phase 7 — Security, Auth & Rate Limiting

**Objective:** Harden the application for production.

### Tasks
- [ ] Add JWT authentication (`app/core/security.py`).
- [ ] Add per-user/per-IP rate limiting.
- [ ] Validate file content (magic bytes), not just extension.
- [ ] File size limits + streaming to disk.
- [ ] Sanitize filenames and prompt inputs (prompt-injection hardening).
- [ ] Add global JSON exception handler.
- [ ] Set restrictive CORS.

### Acceptance Criteria
- [ ] Unauthenticated requests rejected.
- [ ] Rate limits enforced.
- [ ] Malicious uploads blocked.
- [ ] Consistent JSON error responses.

---

## Phase 8 — Testing & QA

**Objective:** Ensure correctness and cover edge cases.

### Tasks
- [ ] Unit tests for parsers, chunkers, embeddings, vector store, services.
- [ ] Integration tests for API endpoints (upload, chat, stream, conversations).
- [ ] Edge-case tests mapped from `docs/edge-case.md`.
- [ ] Performance/load tests for concurrent uploads and chats.
- [ ] Multilingual query tests.

### Acceptance Criteria
- [ ] Test coverage ≥ 80% core modules.
- [ ] All edge cases in `docs/edge-case.md` have an associated test.
- [ ] CI runs tests on every PR.

---

## Phase 9 — Deployment & Scaling

**Objective:** Package and deploy the system reliably.

### Tasks
- [ ] Create `Dockerfile` for backend.
- [ ] Create `docker-compose.yml` (backend, frontend/nginx, ChromaDB, PostgreSQL, Ollama).
- [ ] Mount persistent volumes for SQLite/Chroma/uploads.
- [ ] Add healthchecks + graceful shutdown.
- [ ] Pre-bake embedding model into image.
- [ ] Migrate to PostgreSQL + Chroma server mode for multi-instance scaling.
- [ ] Add Alembic migrations.
- [ ] Add monitoring (logs, metrics, alerting).

### Acceptance Criteria
- [ ] `docker-compose up` runs the full stack.
- [ ] Data persists across container restarts.
- [ ] System scales horizontally safely.

---

## Phase 10 — Post-Launch Enhancements

**Objective:** Improve capabilities and UX based on the problem statement.

### Tasks
- [ ] **Multilingual UX** — full language detection + response translation layer.
- [ ] **OCR** — support scanned/image-based PDFs.
- [ ] **Hybrid search** — BM25 + dense retrieval for better precision.
- [ ] **Citations** — link answers to source chunks.
- [ ] **Feedback loop** — thumbs up/down to improve retrieval.
- [ ] **Multi-tenancy** — per-organization document isolation.
- [ ] **Integrations** — Slack, Teams, webhooks.

### Acceptance Criteria
- [ ] Scanned documents become searchable.
- [ ] Answers include citatable sources.
- [ ] User feedback improves answer quality over time.

---

## Delivery Strategy

- **Phased milestones** — each phase ends with a runnable, demoable increment.
- **Backward compatibility** — API schema evolves via additive changes.
- **Parallelism** — Frontend (Phase 6) can start once API contracts are frozen (end of Phase 5).
- **Risk management**:
  - LLM/embedding availability → abstract providers + graceful degradation (Phase 4).
  - Index drift on model change → version indexes / rebuild (Phase 2/3).
  - Concurrency / scaling → background workers + PostgreSQL (Phase 9).

---

## Alignment with Problem Statement

| Problem-statement requirement | Implemented in |
|-------------------------------|----------------|
| Natural-language Q&A | Phase 4, 5 |
| Retrieve relevant info from documents | Phase 2, 3 |
| Handle PDF/manuals/reports/policies/FAQs | Phase 2 (parsers) |
| Conversation history | Phase 5 |
| Multilingual interaction | Phase 4, 10 |
| Scalable deployment | Phase 9 |
| Reduce human effort / availability 24/7 | Phase 6, 9 |

---

*This plan should be updated as the project evolves. Each phase maps to testable deliverables and can be tracked in the project's issue tracker.*
