"""RAG orchestrator: coordinates retrieval and generation for a chat request."""
from sqlalchemy.orm import Session

from .retrieval import retrieve_context
from .generation import generate_answer, stream_answer
from .conversation import get_or_create_conversation, get_history, add_message


def answer_query(
    db: Session,
    query: str,
    conversation_id: str | None = None,
) -> tuple[str, str, list[dict]]:
    """Run the full RAG pipeline. Returns (conversation_id, answer, sources)."""
    # Ensure conversation exists
    conv = get_or_create_conversation(db, conversation_id)
    conv_id = conv.id

    # Get history
    history = get_history(db, conv_id)

    # Retrieve context
    results = retrieve_context(query)
    context_chunks = [r["text"] for r in results]
    sources = [
        {"document": r["metadata"].get("filename", "unknown"), "score": r["score"]}
        for r in results
    ]

    # Persist user message
    add_message(db, conv_id, "user", query)

    # Generate
    answer = generate_answer(query, context_chunks, history)

    # Persist assistant message
    add_message(db, conv_id, "assistant", answer)

    return conv_id, answer, sources


def stream_query(
    db: Session,
    query: str,
    conversation_id: str | None = None,
):
    """Streamed version of the RAG pipeline. Yields (event, data)."""
    conv = get_or_create_conversation(db, conversation_id)
    conv_id = conv.id
    history = get_history(db, conv_id)
    results = retrieve_context(query)
    context_chunks = [r["text"] for r in results]
    sources = [
        {"document": r["metadata"].get("filename", "unknown"), "score": r["score"]}
        for r in results
    ]

    add_message(db, conv_id, "user", query)

    yield "conversation_id", conv_id
    yield "sources", sources

    full_answer_parts = []
    for token in stream_answer(query, context_chunks, history):
        full_answer_parts.append(token)
        yield "token", token

    full_answer = "".join(full_answer_parts)
    add_message(db, conv_id, "assistant", full_answer)
