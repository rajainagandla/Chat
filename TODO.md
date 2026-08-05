# Implementation Steps — Phase 0 + Phase 1 (Core Backend Skeleton)

## Phase 0 — Foundation & Setup
Complete Phase 0 (Foundation & Setup) and wire the backend to run with the configured database.

## Steps
- [x] 1. Update `chatbot/backend/app/config.py` — add `database_url` setting (default `postgresql+pg8000://chatbot:chatbot@localhost:5432/chatbot`)
- [x] 2. Update `chatbot/backend/app/db/session.py` — use configured `database_url` with SQLite fallback
- [x] 3. Fix `chatbot/backend/tests/test_imports.py` — correct `chunk_text` import path to `app.utils.chunkers`
- [x] 4. Install dependencies into `.venv` (including `pg8000`, chromadb, langchain, fastapi)
- [x] 5. Verify imports (app imports cleanly), confirmed PostgreSQL connection (PostgreSQL 18.4)
- [x] 6. Run the FastAPI server with `uvicorn app.main:app --reload --port 8000` — server starts, `/api/health` returns `{"status":"ok"}`

## Phase 1 — Core Backend Skeleton
Stand up a running FastAPI application with configuration and database.

## Steps
- [x] 1. `app/config.py` — Pydantic Settings with provider, storage, vector, RAG, and server settings (already present, verified)
- [x] 2. `app/db/session.py` — SQLAlchemy engine, `SessionLocal`, `get_db` dependency, `init_db` (already present; refactored `Base` to shared `base_class.py`)
- [x] 3. `app/db/models.py` — Document, Conversation, Message ORM models (already present; imports `Base` from `base_class.py`)
- [x] 4. `app/models/schemas.py` — Pydantic request/response models (already present)
- [x] 5. `app/main.py` — CORS, lifespan DB init, route registration (rewritten: fixed `base_class` import, added CORS, lifespan pattern, tolerant favicon)
- [x] 6. `GET /api/health` returns `{"status":"ok"}`
- [x] 7. `app/api/routes/` package with route modules (health, documents, conversations, chat)
- [x] 8. Created `app/db/base_class.py` — shared declarative `Base`
- [x] 9. Fixed route DI to use `Annotated[Session, Depends(get_db)]` idiom (chat, conversations, documents)
- [x] 10. Verified `uvicorn app.main:app` starts (lifespan init runs), `/api/health` returns `{"status":"ok"}`, DB tables created
- [x] 11. Lint (ruff), format (black), and pytest all pass

## Acceptance Criteria (Phase 1)
- [x] `uvicorn app.main:app` starts successfully
- [x] `GET /api/health` returns `{"status":"ok"}`
- [x] SQLite/configured DB tables (`documents`, `conversations`, `messages`) created on startup
