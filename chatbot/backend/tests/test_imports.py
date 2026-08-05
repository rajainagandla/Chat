"""Basic smoke test: verify all modules import and app builds."""


def test_config_imports():
    from app.config import settings  # noqa: F401

    assert settings.top_k > 0


def test_schemas_import():
    from app.models.schemas import ChatRequest, ChatResponse, DocumentOut  # noqa: F401

    assert ChatRequest


def test_services_import():
    from app.services.embeddings import get_embeddings  # noqa: F401
    from app.services.llm import get_llm  # noqa: F401
    from app.utils.chunkers import chunk_text  # noqa: F401

    assert callable(chunk_text)


def test_app_builds():
    from app.main import app  # noqa: F401

    assert app.title == "AI-Powered Intelligent Chatbot API"
