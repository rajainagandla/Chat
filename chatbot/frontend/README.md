# AI-Powered Intelligent Chatbot — Frontend (Scaffold)

> **Phase 6 deliverable.** This directory is the placeholder scaffold for the chat UI.
> No implementation yet — the plan calls for building the frontend in Phase 6.

## Planned Tech Stack
- React + Vite
- Tailwind CSS
- SSE streaming client for chat

## Planned Layout
```
chatbot/frontend/
├── src/
│   ├── components/          # Chat, MessageBubble, DocumentUpload, Sidebar
│   ├── hooks/               # useChat, useDocuments, useSSE
│   ├── services/            # API client
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

## Backend API Contract (from Phase 1–5)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Ask a question (non-streaming) |
| `POST` | `/api/chat/stream` | Ask a question (SSE streaming) |
| `POST` | `/api/documents` | Upload document (multipart) |
| `GET` | `/api/documents` | List documents |
| `DELETE` | `/api/documents/{id}` | Delete document |
| `GET` | `/api/conversations` | List conversations |
| `GET` | `/api/conversations/{id}/messages` | Get messages |

## Status
🚧 Scaffold only — implementation scheduled for **Phase 6**.
