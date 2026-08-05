"""Retrieval service: fetch relevant context chunks for a query."""

from .vector_store import get_vector_store


def retrieve_context(query: str, top_k: int = None) -> list[dict]:
    """Return list of {'text','score','metadata'} for relevant chunks."""
    store = get_vector_store()
    results = store.search(query, top_k=top_k)
    return [{"text": text, "score": score, "metadata": meta} for text, score, meta in results]
