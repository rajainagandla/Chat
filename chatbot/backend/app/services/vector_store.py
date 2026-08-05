"""ChromaDB vector store service for document chunk indexing and retrieval."""

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config import settings
from .embeddings import get_embeddings

COLLECTION_NAME = "documents"


class VectorStore:
    def __init__(self, persist_dir: str):
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._embeddings = get_embeddings()
        self._collection = self._client.get_or_create_collection(name=COLLECTION_NAME)

    def add_document(self, doc_id: str, filename: str, chunks: list[str]) -> int:
        """Embed and index chunks for a document. Returns number of chunks."""
        if not chunks:
            return 0
        vectors = self._embeddings.embed(chunks)
        ids = [f"{doc_id}::{i}" for i in range(len(chunks))]
        metadatas = [
            {"document_id": doc_id, "filename": filename, "chunk_index": i}
            for i in range(len(chunks))
        ]
        self._collection.add(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas)
        return len(chunks)

    def search(self, query: str, top_k: int = None) -> list[tuple[str, float, dict]]:
        """Return list of (text, score, metadata) for the most relevant chunks."""
        top_k = top_k or settings.top_k
        query_embedding = self._embeddings.embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        out = []
        for text, meta, dist in zip(docs, metas, dists, strict=True):
            # Chroma returns L2-ish distances; lower is closer. Convert to similarity.
            score = 1.0 / (1.0 + dist)
            out.append((text, score, meta))
        return out

    def delete_document(self, doc_id: str) -> None:
        """Delete all chunks belonging to a document."""
        self._collection.delete(where={"document_id": doc_id})

    def count(self) -> int:
        return self._collection.count()


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore(str(settings.chroma_path))


def reset_vector_store() -> None:
    """For tests: clear the cached singleton."""
    get_vector_store.cache_clear()
