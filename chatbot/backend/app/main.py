"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.session import init_db
from .api.routes import chat, documents, health, conversations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    yield


app = FastAPI(
    title="AI-Powered Intelligent Chatbot API",
    version="1.0.0",
    description="RAG-based chatbot that answers questions from uploaded documents.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(conversations.router)


@app.get("/")
def root():
    return {"message": "AI-Powered Intelligent Chatbot API", "docs": "/docs"}
