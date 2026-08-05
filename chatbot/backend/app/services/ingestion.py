"""Document ingestion pipeline: parse -> chunk -> embed -> index."""
from ..utils.parsers import extract_text
from ..utils.chunkers import chunk_text
from .vector_store import get_vector_store


def ingest_document(doc_id: str, filename: str, filepath: str) -> int:
    """Process a stored file and index its chunks. Returns chunk count."""
    text = extract_text(filepath)
    chunks = chunk_text(text)
    store = get_vector_store()
    return store.add_document(doc_id, filename, chunks)
