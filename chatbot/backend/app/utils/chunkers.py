"""Text chunking utilities for RAG ingestion."""

from ..config import settings

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap if overlap is not None else settings.chunk_overlap
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)

except ImportError:  # fallback without langchain

    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap if overlap is not None else settings.chunk_overlap
        chunks: list[str] = []
        start = 0
        n = len(text)
        while start < n:
            end = min(start + chunk_size, n)
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            if end >= n:
                break
            start = end - overlap
        return chunks
