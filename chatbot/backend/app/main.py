"""FastAPI application entrypoint for the AI-Powered Intelligent Chatbot API."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from app.api.routes import chat, conversations, documents, health
from app.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize the database on startup."""
    init_db()
    yield


app = FastAPI(
    title="AI-Powered Intelligent Chatbot API",
    version="1.0.0",
    description="AI-Powered Intelligent Chatbot using LLMs and RAG.",
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

# Include routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(chat.router)


# Root route with HTML landing page
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <h1>AI-Powered Intelligent Chatbot API</h1>
    <p>Welcome! Use <a href="/docs">/docs</a> to explore the interactive API docs.</p>
    <p>Or check out <a href="/redoc">/redoc</a> for ReDoc documentation.</p>
    """


# Favicon route (served only if the file exists)
FAVICON_PATH = Path(__file__).resolve().parent / "static" / "favicon.ico"


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if FAVICON_PATH.exists():
        return FileResponse(FAVICON_PATH)
    return HTMLResponse(status_code=204)
