"""Generation service: build prompt and call LLM to produce answers."""
from typing import Generator, List

from .llm import get_llm

SYSTEM_PROMPT = (
    "You are an intelligent assistant that answers questions based only on the "
    "provided context from uploaded documents. If the context does not contain "
    "the answer, say you don't know based on the available documents. Respond "
    "in the same language as the user's question. Be concise and factual."
)


def _build_prompt(query: str, context_chunks: List[str], history: List[dict]) -> str:
    context_block = "\n\n".join(
        f"[Source {i + 1}]\n{chunk}" for i, chunk in enumerate(context_chunks)
    )
    history_block = "\n".join(
        f"{m['role']}: {m['content']}" for m in history
    ) if history else "No prior conversation."

    user_prompt = (
        f"Conversation history:\n{history_block}\n\n"
        f"Relevant context from documents:\n{context_block}\n\n"
        f"Question: {query}\n\n"
        f"Answer:"
    )
    return user_prompt


def generate_answer(
    query: str,
    context_chunks: List[str],
    history: List[dict],
) -> str:
    prompt = _build_prompt(query, context_chunks, history)
    llm = get_llm()
    return llm.complete(SYSTEM_PROMPT, prompt)


def stream_answer(
    query: str,
    context_chunks: List[str],
    history: List[dict],
) -> Generator[str, None, None]:
    prompt = _build_prompt(query, context_chunks, history)
    llm = get_llm()
    yield from llm.stream(SYSTEM_PROMPT, prompt)
