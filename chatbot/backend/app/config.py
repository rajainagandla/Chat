"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ===== Provider =====
    llm_provider: str = "local"  # local | openai

    # ===== Local / Ollama =====
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ===== OpenAI =====
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"

    # ===== Vector store =====
    chroma_persist_dir: str = "./data/chroma"

    # ===== Storage =====
    upload_dir: str = "./data/uploads"

    # ===== Server =====
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ===== RAG tuning =====
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 4

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def upload_path(self) -> Path:
        p = Path(self.upload_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def chroma_path(self) -> Path:
        p = Path(self.chroma_persist_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
