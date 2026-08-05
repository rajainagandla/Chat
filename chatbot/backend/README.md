# AI-Powered Intelligent Chatbot — Backend

RAG-based chatbot backend that answers natural-language questions from uploaded documents (PDF, DOCX, TXT, MD).

## Features
- 📄 Upload & parse documents (PDF, DOCX, TXT, MD)
- 🧠 Retrieval-Augmented Generation (RAG)
- 💬 Conversational chat with history
- 🌍 Multilingual (LLM responds in query language)
- ⚡ Streaming responses (SSE)
- 🗂️ Conversation persistence (SQLite)
- 🔍 Vector search (ChromaDB)

## Quick Start

### 1. Create environment & install dependencies
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure
```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

By default, the app uses **local** mode (Ollama + sentence-transformers + ChromaDB). To use OpenAI, set `LLM_PROVIDER=openai` and add your `OPENAI_API_KEY`.

### 3. (Optional) Install Ollama for local LLM
```bash
# Install Ollama from https://ollama.com
ollama pull llama3
ollama serve
```

### 4. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Environment Variables
See `.env.example` for all options:
| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `local` | `local` or `openai` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_MODEL` | `llama3` | Local model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model |
| `OPENAI_API_KEY` | `` | Set when using OpenAI |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | Vector store path |
| `UPLOAD_DIR` | `./data/uploads` | Uploaded files path |
| `CHUNK_SIZE` | `500` | Chunk size (tokens) |
| `TOP_K` | `4` | Retrieved chunks per query |

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/documents` | Upload & process a document (multipart) |
| `GET` | `/api/documents` | List documents |
| `DELETE` | `/api/documents/{id}` | Delete document + chunks |
| `POST` | `/api/chat` | Ask a question (non-streaming) |
| `POST` | `/api/chat/stream` | Ask a question (SSE streaming) |
| `GET` | `/api/conversations` | List conversations |
| `GET` | `/api/conversations/{id}/messages` | Get messages |

## Example Usage

### Upload a document
```bash
curl -X POST http://localhost:8000/api/documents \
  -F "file=@policy.pdf"
```

### Ask a question
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the refund policy?"}'
```

## License
MIT
