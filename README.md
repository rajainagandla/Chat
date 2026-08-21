<<<<<<< HEAD
# AI-Powered Intelligent Chatbot (RAG)

An AI-powered intelligent chatbot that answers natural-language questions from organization-specific documents (PDF, manuals, reports, policies, FAQs) using **Retrieval-Augmented Generation (RAG)** with Large Language Models (LLMs).

## Features
- 📄 Upload & parse documents (PDF, DOCX, TXT, MD)
- 🧠 RAG-based question answering with context-aware responses
- 💬 Conversational chat with persistent history
- 🌍 Multilingual interaction (LLM responds in the query language)
- ⚡ Streaming responses (SSE)
- 🔍 Vector search (ChromaDB)
- 🗂️ Conversation persistence (SQLite)
- 🔌 Pluggable LLM/embedding providers (local Ollama or OpenAI)

## Repository Layout
```
.
├── chatbot/
│   ├── backend/            # FastAPI backend (Python 3.11+)
│   │   ├── app/
│   │   │   ├── api/        #   API routes (health, documents, chat, conversations)
│   │   │   ├── core/       #   Config & security
│   │   │   ├── db/         #   SQLAlchemy session & ORM models
│   │   │   ├── models/     #   Pydantic schemas
│   │   │   ├── services/   #   RAG pipeline (ingest, retrieve, generate, converse)
│   │   │   └── utils/      #   Parsers & chunkers
│   │   ├── tests/          #   Unit & integration tests
│   │   ├── requirements.txt      #   Runtime dependencies
│   │   ├── requirements-dev.txt  #   Dev/tooling dependencies
│   │   ├── pyproject.toml        #   Ruff, Black, mypy, pytest config
│   │   ├── .env.example          #   Environment template
│   │   └── Dockerfile
│   └── frontend/           # Chat UI (scaffold — Phase 6)
│       └── README.md
├── docs/
│   ├── Implementation-plan.md    # Phase-wise implementation plan
│   └── edge-case.md              # Edge cases & corner scenarios
├── .github/workflows/ci.yml      # CI: lint + test on push
├── ARCHITECTURE.md               # System architecture
├── docker-compose.yml
├── .gitignore
└── PROBLEM_STATEMENT.md
```

## Quick Start (Backend)

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) (optional, for local LLM mode)

### 1. Install dependencies
```bash
cd chatbot/backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements-dev.txt
```

### 2. Configure
```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```
Default is **local** mode (Ollama + sentence-transformers + ChromaDB).
For OpenAI, set `LLM_PROVIDER=openai` and add `OPENAI_API_KEY`.

### 3. (Optional) Start Ollama
```bash
ollama pull llama3
ollama serve
```

### 4. Run
```bash
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

## Development Tooling
| Tool | Purpose | Command |
|------|---------|---------|
| **Ruff** | Linter | `ruff check app tests` |
| **Black** | Formatter | `black app tests` |
| **mypy** | Type checker | `mypy app` |
| **pytest** | Tests | `pytest --cov=app` |

## CI/CD
GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR to `main`/`develop`:
- Ruff lint + Black format check + mypy type check
- pytest with coverage
- Backend import verification

## Documentation
- [Implementation Plan](docs/Implementation-plan.md)
- [Edge Cases](docs/edge-case.md)
- [Architecture](ARCHITECTURE.md)

## License
MIT
=======
# Chat
>>>>>>> 6113fd28905e7f1c36769c94bb0c992ad1e7aac3
