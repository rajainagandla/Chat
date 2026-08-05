# Edge Cases & Corner Scenarios — AI-Powered Intelligent Chatbot (RAG)

> **References:** This document catalogues edge cases and corner scenarios for the RAG-based chatbot.
> It is grounded in the actual implementation found in `chatbot/backend/` (FastAPI + SQLAlchemy +
> ChromaDB + pluggable LLM/embeddings) and the design described in `ARCHITECTURE.md`.

Each edge case is tagged with:
- **Severity:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
- **Area:** the component it affects
- **Current behavior** (as implemented) and **Recommended handling** (gap/improvement)

---

## Table of Contents
1. [Document Upload & Ingestion](#1-document-upload--ingestion)
2. [File Parsing](#2-file-parsing)
3. [Text Chunking](#3-text-chunking)
4. [Embeddings](#4-embeddings)
5. [Vector Store (ChromaDB)](#5-vector-store-chromadb)
6. [Retrieval & Similarity Scoring](#6-retrieval--similarity-scoring)
7. [RAG Pipeline & Context Assembly](#7-rag-pipeline--context-assembly)
8. [LLM Generation & Streaming](#8-llm-generation--streaming)
9. [Conversation History](#9-conversation-history)
10. [API & Request Handling](#10-api--request-handling)
11. [Configuration & Environment](#11-configuration--environment)
12. [Database & Persistence](#12-database--persistence)
13. [Concurrency & Performance](#13-concurrency--performance)
14. [Security](#14-security)
15. [Deployment & Operations](#15-deployment--operations)

---

## 1. Document Upload & Ingestion

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E1.1 | **Empty file (`filename` is `None`)** | 🟠 | Upload | `_validate_file(file.filename or "")` → `Path("").suffix` returns `""` → 400 "Unsupported file type: " | Return a clearer 400 message: "Filename is required." |
| E1.2 | **File with no extension** (e.g. `report`) | 🟡 | Upload | Returns 400 "Unsupported file type" | Clear message; acceptable, but consider suggesting supported types. |
| E1.3 | **Capitalized extension** (`.PDF`, `.DOCX`) | 🟢 | Upload | `.lower()` normalizes → accepted correctly | ✅ Already handled. |
| E1.4 | **File exactly at size limit (25 MB)** | 🟡 | Upload | Reads `MAX_FILE_SIZE + 1` bytes; if `len == MAX_FILE_SIZE` it passes; if `> MAX_FILE_SIZE` → 413 | ✅ Correct boundary. Test with exact 25 MB file. |
| E1.5 | **File slightly over 25 MB** | 🟡 | Upload | 413 "File too large" | ✅ Handled. |
| E1.6 | **Zero-byte file / empty content** | 🟠 | Upload/Parse | `extract_text` raises `ValueError("Extracted text is empty")` → doc marked `failed` | Consider returning a 400 early with "File is empty" instead of a generic failure. |
| E1.7 | **Scan-only / image-only PDF** (no extractable text) | 🔴 | Parse | `page.extract_text()` returns `None`/`""` → concatenated empty → `ValueError` → doc `failed` | ⚠️ No OCR. Recommend documenting that scanned PDFs are unsupported, or adding OCR. |
| E1.8 | **Corrupted / unreadable PDF** | 🔴 | Parse | `pypdf` raises exception → caught in upload `except` → doc `failed` with error | ✅ Graceful failure, but error stored only in DB; surface to user. |
| E1.9 | **Corrupted / encrypted DOCX** | 🟠 | Parse | `python-docx` raises → doc `failed` | Add friendly error message; consider catching `PackageNotFoundError`. |
| E1.10 | **Non-UTF8 text file** | 🟡 | Parse | `read_text(encoding="utf-8", errors="ignore")` silently drops invalid bytes | ✅ Handled (no crash), but data loss is silent. Consider warning. |
| E1.11 | **File contains only whitespace/blank PDF pages** | 🟡 | Parse | Empty after `.strip()` → `ValueError("Extracted text is empty")` → `failed` | ✅ Handled, but message could be clearer. |
| E1.12 | **Ingestion fails AFTER DB row created** | 🟠 | Ingestion | Doc saved with `status="processing"`, then `except` sets `failed`, commits | ✅ Model records `failed` + `error`. ⚠️ Orphan file remains on disk (no cleanup). Recommend deleting file on failure. |
| E1.13 | **Chunks produced but embedding fails** (e.g. Ollama down) | 🔴 | Ingestion | Exception → doc `failed`; file remains; no chunks indexed | Add retry; cleanup partial state. |
| E1.14 | **Duplicate file uploads** | 🟡 | Upload | No dedup — each upload creates a new document + duplicate index entries | Consider content-hash deduplication or explicit duplicate warning. |
| E1.15 | **Very large text (many chunks)** | 🟡 | Ingestion | Synchronous upload — blocks request; no progress/queue | ⚠️ Move ingestion to a background worker (Celery/RQ) for scalability. |
| E1.16 | **Uploading a directory / multiple files at once** | 🟢 | Upload | Single-file endpoint only (`UploadFile`) | Frontend must send one file per request; document this. |
| E1.17 | **Filename with path traversal** (`../../etc/passwd`) | 🔴 | Security | Filename stored as-is; **saved file uses UUID**, so disk path is safe. But `filename` shown in UI unsanitized | ⚠️ Sanitize displayed filename / escape in frontend to prevent XSS. |
| E1.18 | **Deleting a document mid-ingestion** | 🟠 | Concurrency | No locking; delete may run while ingestion writes chunks → partial state | Add ingestion status lock / atomic delete. |

---

## 2. File Parsing

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E2.1 | **Unsupported extension reaching `extract_text`** | 🟡 | Parse | `PARSERS.get` returns `None` → raises `ValueError` | ✅ Handled defensively. |
| E2.2 | **PDF with 1000+ pages** | 🟡 | Parse | Parses all pages synchronously → slow, memory heavy | Add page limit / streaming / async. |
| E2.3 | **DOCX with tables** | 🟡 | Parse | `parse_docx` only reads `document.paragraphs`; **table text is ignored** | ⚠️ Tables lost. Consider extracting tables with `document.tables`. |
| E2.4 | **DOCX headers/footers** | 🟡 | Parse | Not read | ⚠️ Content in headers/footers lost. |
| E2.5 | **PDF with columns / complex layout** | 🟡 | Parse | `pypdf` linear extraction may jumble text order | Note as limitation; consider layout-aware parser (e.g. pdfplumber). |
| E2.6 | **Encrypted PDF requiring password** | 🟠 | Parse | `pypdf` raises `/Encryption` error → doc `failed` | Provide clear "encrypted PDF not supported" message. |
| E2.7 | **`.md` file with code blocks / images** | 🟢 | Parse | Read as plain text; code blocks preserved, images ignored | ✅ Acceptable; note limitation. |

---

## 3. Text Chunking

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E3.1 | **Chunk size ≥ document length** | 🟢 | Chunking | Returns the whole text as 1 chunk | ✅ Handled. |
| E3.2 | **`chunk_overlap` ≥ `chunk_size`** | 🟡 | Chunking | Fallback splitter: `start = end - overlap` could go negative/new → infinite loop risk | ⚠️ Validate config: require `overlap < chunk_size`. |
| E3.3 | **Empty input text** | 🟡 | Chunking | `chunk_text("")` → `[]` (fallback) or `[]` (langchain) | `add_document` returns 0 early. ✅ Handled but means no index. |
| E3.4 | **Single word / very short chunk** | 🟢 | Chunking | `chunk.strip()` may be empty → skipped | ✅ Handled. |
| E3.5 | **Very long unbroken string (no newlines/periods)** | 🟡 | Chunking | LangChain `RecursiveCharacterTextSplitter` falls back to char split at `""` separator → works; fallback uses fixed size | ✅ Works, but chunk boundaries may split mid-sentence. |
| E3.6 | **Multilingual text chunking** | 🟡 | Chunking | Character-based splitting may break CJK/agglutinative languages mid-word | ⚠️ Consider language-aware splitters. |

---

## 4. Embeddings

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E4.1 | **Local model not downloaded / Ollama offline** | 🔴 | Embeddings | `SentenceTransformer(model)` downloads on first use (may fail offline) → ingestion fails | Pre-download model; clear error message; retry. |
| E4.2 | **Empty chunk list passed to `embed`** | 🟡 | Embeddings | `add_document` returns 0 before embedding | ✅ Guarded. |
| E4.3 | **OpenAI mode with missing/invalid API key** | 🔴 | Embeddings | `OpenAI(api_key="")` created; call fails at runtime | Validate key at startup; fail fast with clear message. |
| E4.4 | **OpenAI rate limit (429)** | 🟠 | Embeddings | Batch of 64; no retry/backoff → 429 raises → doc `failed` | Add exponential backoff + retry. |
| E4.5 | **Embedding dimension mismatch** (switching models with existing index) | 🔴 | Vector Store | ChromaDB collection created with old dim; new embeddings different dim → query/insert error | ⚠️ Check collection dim vs current model; rebuild index on model change. |
| E4.6 | **Batch > API limit** | 🟠 | Embeddings | Batches at 64 (OpenAI limit is 2048) | ✅ Safe. |
| E4.7 | **Empty text string in embed batch** | 🟡 | Embeddings | May produce meaningless embedding or error | Filter empty chunks before embedding. |

---

## 5. Vector Store (ChromaDB)

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E5.1 | **Query with no indexed documents** | 🟠 | Vector Store | `_collection.query` on empty collection → Chroma may raise or return empty → `retrieve_context` returns `[]` → generation gets no context | ⚠️ Handle empty collection gracefully; return a clear "no documents uploaded" message. |
| E5.2 | **`top_k` larger than collection size** | 🟡 | Vector Store | `query(n_results=top_k)` with `top_k > count` → Chroma raises `ValueError` | ⚠️ Clamp `n_results = min(top_k, count)`. |
| E5.3 | **Duplicate chunk IDs** (same doc ingested twice) | 🟠 | Vector Store | IDs are `doc_id::i`; re-ingesting same doc_id overwrites (same IDs) — but if `doc_id` differs, duplicates created | ⚠️ Dedup by doc_id; delete old chunks before re-add. |
| E5.4 | **Deleting a doc whose chunks don't exist** | 🟢 | Vector Store | `delete(where=...)` no-ops | ✅ Safe. |
| E5.5 | **ChromaDB corrupted / lock file present** | 🔴 | Vector Store | `PersistentClient` raises on startup/insert | Add retry + clear error; consider container restart policy. |
| E5.6 | **Concurrent writes to ChromaDB** (multi-worker) | 🟠 | Concurrency | ChromaDB file-based is not multi-process safe | ⚠️ Single-writer; use a worker queue or a server-mode Chroma for horizontal scaling. |
| E5.7 | **Collection name collision** | 🟢 | Vector Store | Fixed name `"documents"`; `get_or_create` reuses | ✅ Intended, but no multi-tenancy isolation. |

---

## 6. Retrieval & Similarity Scoring

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E6.1 | **Query with no semantic match** | 🟠 | Retrieval | Returns top-k anyway (low scores); LLM told to say "I don't know" | ✅ Prompt handles it; but low-score filtering is recommended. |
| E6.2 | **Score conversion formula** | 🟡 | Retrieval | `score = 1.0 / (1.0 + dist)` — assumes L2 distance; depends on Chroma's metric | ⚠️ Verify Chroma default distance metric; document score semantics. Score is similarity (higher=better). |
| E6.3 | **`distance = 0` (perfect match)** | 🟢 | Retrieval | `score = 1.0` | ✅ Handled. |
| E6.4 | **Very large/degenerate distance** | 🟢 | Retrieval | `score → 0` | ✅ Bounded (0,1]. |
| E6.5 | **Empty query string** | 🟠 | Retrieval | `ChatRequest` requires `min_length=1` → 422 | ✅ Handled at schema level. |
| E6.6 | **Query that is only whitespace** `"   "` | 🟠 | Retrieval | Passes `min_length=1` (3 chars) → embeds meaningless query | ⚠️ Add `strip()` validation; reject blank messages. |
| E6.7 | **Top-k = 0 or negative via config** | 🟡 | Retrieval | `n_results=0` → error; negative → error | Validate config `top_k >= 1`. |

---

## 7. RAG Pipeline & Context Assembly

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E7.1 | **No relevant context found** | 🟠 | RAG | `context_chunks=[]` → prompt has empty context block → LLM may hallucinate | ⚠️ Add a guard: if no context, return canned "no documents / no match" message instead of calling LLM. |
| E7.2 | **Context exceeds LLM token limit** (many/short top_k or huge chunks) | 🔴 | RAG | `context_block` concatenates all chunks; no truncation → may exceed model context window | ⚠️ Estimate tokens; truncate context to fit; trim history. |
| E7.3 | **Conversation history grows unbounded in prompt** | 🟠 | RAG | `get_history` limited to `limit=10` | ✅ Handled (last 10 messages). ⚠️ Still could be large; consider token-based trimming. |
| E7.4 | **User message persisted but LLM call fails** | 🔴 | RAG | `add_message(user)` committed, then `generate_answer` raises → no assistant message, user msg saved | ⚠️ Wrap in try/except; save an error assistant message or rollback. |
| E7.5 | **Sources list empty** | 🟢 | RAG | `sources` derived from results | ✅ Returns `[]` gracefully. |
| E7.6 | **Metadata missing `filename`** | 🟢 | RAG | `r["metadata"].get("filename", "unknown")` | ✅ Safe default. |

---

## 8. LLM Generation & Streaming

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E8.1 | **Ollama not running** | 🔴 | LLM | `httpx.post` connection refused → exception → 500 | ⚠️ Catch and return 503 "LLM backend unavailable". |
| E8.2 | **Ollama returns non-200 / error body** | 🟠 | LLM | `resp.raise_for_status()` raises → 500 | Map to 502/503 with clear message. |
| E8.3 | **Ollama response missing `message.content`** | 🟡 | LLM | `resp.json()["message"]["content"]` → `KeyError` → 500 | Defensive `.get()` with default. |
| E8.4 | **Stream response malformed line** | 🟡 | LLM | `json.loads` in try/except → skipped | ✅ Handled (skips bad lines). |
| E8.5 | **Model produces empty answer** | 🟡 | LLM | Returns empty string; persisted as empty assistant message | Provide fallback message. |
| E8.6 | **OpenAI exception (auth, quota, network)** | 🔴 | LLM | `openai` raises → 500 | Catch; map to 502; clear message. |
| E8.7 | **Streaming client disconnects mid-stream** | 🟠 | LLM | In `chat.py`, generator raises `ClientDisconnected`; no handling → partial answer not persisted | ⚠️ Catch disconnect; persist partial or skip persistence. |
| E8.8 | **Streaming yields no tokens** | 🟡 | LLM | `full_answer=""` saved | Guard against empty. |
| E8.9 | **LLM timeout (120s)** | 🟠 | LLM | `httpx` timeout=120 → raises → 500 | Add retry + informative error. |
| E8.10 | **Prompt injection via document content** | 🔴 | Security | Document text inserted into prompt; malicious instructions could override system prompt | ⚠️ Consider instruction-delimiter wrapping and prompt-hardening. |

---

## 9. Conversation History

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E9.1 | **`conversation_id` provided that doesn't exist** | 🟠 | History | `get_or_create_conversation` creates a NEW conversation (silently ignores bad id) | ⚠️ Ambiguous. Consider 404 if id given but not found, OR document this "create-on-miss" behavior. |
| E9.2 | **`conversation_id` is `null`/omitted** | 🟢 | History | Creates new conversation | ✅ Intended. |
| E9.3 | **Empty conversation (no messages) queried** | 🟢 | History | `get_history` returns `[]` | ✅ Prompt handles "No prior conversation." |
| E9.4 | **More than 10 messages** | 🟡 | History | Only last 10 used in prompt | ✅ Handled; document the cap. |
| E9.5 | **Concurrent messages to same conversation** | 🟠 | Concurrency | No locking; last-write wins; history may interleave | ⚠️ Add per-conversation lock or versioning. |
| E9.6 | **Deleting a conversation** | 🟢 | History | No delete endpoint exists | ⚠️ Consider adding conversation delete. |
| E9.7 | **Message ordering ties** (same `created_at`) | 🟢 | History | `order_by(created_at.asc())` — ties possible | Add secondary sort by `id` for determinism. |

---

## 10. API & Request Handling

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E10.1 | **`message` missing or empty** | 🟢 | API | Pydantic `min_length=1` → 422 | ✅ Handled. |
| E10.2 | **`message` only whitespace** | 🟠 | API | Passes validation (see E6.6) | Add strip validation. |
| E10.3 | **Unknown document id in DELETE** | 🟢 | API | 404 "Document not found" | ✅ Handled. |
| E10.4 | **Unknown conversation id in GET messages** | 🟢 | API | 404 "Conversation not found" | ✅ Handled. |
| E10.5 | **Malformed JSON body** | 🟢 | API | FastAPI → 422 | ✅ Handled. |
| E10.6 | **Unsupported Content-Type for upload** | 🟡 | API | Only extension validated; content-type mismatch (e.g. `.txt` but actually binary) | ⚠️ Validate via magic bytes, not just extension. |
| E10.7 | **Large multipart body / memory** | 🟡 | API | Reads whole file into memory inline; 25MB cap | ⚠️ Consider streaming to disk for large files / memory limits. |
| E10.8 | **SSE endpoint non-streaming client expectations** | 🟡 | API | Returns `text/event-stream`; JSON events wrapped in `data:` | Frontend must parse SSE format. ✅ Documented. |
| E10.9 | **No global error handler** | 🟠 | API | Unexpected exceptions → default 500 HTML | Add JSON exception handlers for consistent errors. |

---

## 11. Configuration & Environment

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E11.1 | **`LLM_PROVIDER` set to unknown value** | 🟠 | Config | `get_llm` treats anything not `"openai"` as Ollama | ⚠️ Validate provider value; fail fast on typo. |
| E11.2 | **OpenAI mode but no `OPENAI_API_KEY`** | 🔴 | Config | `OpenAI("")` created; fails at first call | Validate at startup. |
| E11.3 | **`CORS_ORIGINS` empty / whitespace** | 🟡 | Config | Parsed to `[]` → no CORS origins allowed | Set sensible default; document. |
| E11.4 | **`chunk_size`/`chunk_overlap`/`top_k` invalid values** | 🟠 | Config | No validation; can cause runtime errors | Add pydantic validators (min values). |
| E11.5 | **`.env` missing** | 🟢 | Config | Defaults used | ✅ Handled. |
| E11.6 | **Relative paths in config** (`./data/...`) | 🟡 | Config | Resolved relative to **CWD**, not project dir → breaks if run from elsewhere | ⚠️ Resolve relative to `BASE_DIR`. |
| E11.7 | **Host/port invalid** | 🟢 | Config | Uvicorn fails at startup | Validate. |

---

## 12. Database & Persistence

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E12.1 | **`data/` directory missing** | 🟢 | DB | `init_db` / module creates `./data` | ✅ Handled. |
| E12.2 | **Race on `./data` creation** (multi-worker) | 🟢 | DB | `mkdir(parents=True, exist_ok=True)` is safe | ✅ Handled. |
| E12.3 | **SQLite file locked under concurrency** | 🟠 | DB | `check_same_thread=False`; concurrent writes may hit `database is locked` | ⚠️ SQLite not ideal for concurrent write; use PostgreSQL in prod. |
| E12.4 | **Document row but file missing on disk** | 🟡 | DB | Delete uses `unlink(missing_ok=True)` → safe | ✅ Handled. |
| E12.5 | **DB schema migration** | 🟠 | DB | `create_all` only creates; no migrations (Alembic) | ⚠️ Add Alembic for schema evolution. |
| E12.6 | **Foreign key integrity** (message w/o conversation) | 🟢 | DB | `foreign_keys` on; SQLite needs PRAGMA to enforce | Ensure FK enforcement enabled. |

---

## 13. Concurrency & Performance

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E13.1 | **Multiple simultaneous document uploads** | 🟠 | Concurrency | Synchronous ingestion blocks event loop/worker | ⚠️ Async / background queue required. |
| E13.2 | **Multiple chat requests to same conversation** | 🟠 | Concurrency | No locking | Add per-conversation serialization. |
| E13.3 | **Vector store singleton caching** | 🟡 | Perf | `@lru_cache` returns same store; fine within process | ✅ OK for single process; breaks across workers (multi-process → separate locks). |
| E13.4 | **Embedding model loaded multiple times** | 🟡 | Perf | `get_embeddings` is `@lru_cache`d → loaded once | ✅ Handled. |
| E13.5 | **Long-running LLM blocks worker** | 🟠 | Perf | Sync def endpoints run in threadpool; streaming blocks during generation | ⚠️ Consider async generation. |

---

## 14. Security

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E14.1 | **No authentication** | 🔴 | Security | All endpoints open | ⚠️ Add JWT/auth for production. |
| E14.2 | **No rate limiting** | 🔴 | Security | Infinite requests possible (LLM cost, DoS) | Add rate limiting per user/IP. |
| E14.3 | **Path traversal via filename** | 🟠 | Security | Saved path uses UUID (safe), but display unsanitized | Sanitize display; escape in frontend. |
| E14.4 | **Prompt injection via document/query** | 🔴 | Security | Raw content in prompt | Harden prompt; delimit context. |
| E14.5 | **CORS with `allow_credentials=True`** | 🟡 | Security | Combined with wildcard origins would be insecure; current origins are explicit | ✅ Explicit origins; keep credentials False unless needed. |
| E14.6 | **Sensitive document exposure** | 🟠 | Security | No per-user doc isolation / authorization on retrieval | Add multi-tenancy & per-doc ACLs. |
| E14.7 | **Malicious file upload (binary/executable renamed `.txt`)** | 🟠 | Security | Extension-only check | Validate magic bytes; store outside web root. |

---

## 15. Deployment & Operations

| # | Scenario | Severity | Area | Current Behavior | Recommended Handling |
|---|----------|----------|------|------------------|----------------------|
| E15.1 | **ChromaDB persistence across restarts** | 🟡 | Ops | Persistent path configured; ensure volume mounted in Docker | ✅ Configure volume in docker-compose. |
| E15.2 | **SQLite DB not persisted in Docker** | 🔴 | Ops | Default `./data` must be a mounted volume or lost on container restart | ✅ Mount volume. |
| E15.3 | **Model download on first run in container** | 🟠 | Ops | `SentenceTransformer` downloads at runtime (slow, needs network) | Pre-bake model into image. |
| E15.4 | **Ollama service dependency** | 🔴 | Ops | LLM must be separate container/service; health check needed | Add Ollama container + healthcheck in docker-compose. |
| E15.5 | **Multiple replicas sharing SQLite/Chroma** | 🔴 | Scaling | Not safe for multi-instance | Use PostgreSQL + Chroma server / network storage. |
| E15.6 | **Graceful shutdown during streaming** | 🟡 | Ops | Long-lived SSE may be cut off | Implement graceful shutdown + client disconnect handling. |

---

## Cross-Cutting Recommended Fixes (Prioritized)

1. 🔴 **Validate LLM/embedding provider availability at startup** — fail fast with clear messages (E4.1, E4.3, E8.1, E11.2).
2. 🔴 **Handle empty vector store / no context** before calling LLM (E5.1, E7.1).
3. 🔴 **Add authentication + rate limiting** (E14.1, E14.2).
4. 🟠 **Clamp `top_k` to collection size** (E5.2) and validate config values (E11.4).
5. 🟠 **Move ingestion to a background queue** (E1.15, E13.1, E13.2).
6. 🟠 **Add token-based context/history truncation** (E7.2).
7. 🟠 **Persist partial/rollback on LLM failure** (E7.4, E8.7).
8. 🟠 **Resolve relative config paths against project root** (E11.6).
9. 🟠 **Add Alembic migrations & PostgreSQL for production** (E12.5, E15.5).
10. 🟡 **Strip whitespace from `message`** (E6.6, E10.2).
11. 🟡 **Validate file content (magic bytes), not just extension** (E10.6, E14.7).
12. 🟡 **Add global JSON exception handler** (E10.9).

---

*This document should be kept in sync with code changes. Each edge case maps to a test case in `tests/` and a potential fix ticket.*
