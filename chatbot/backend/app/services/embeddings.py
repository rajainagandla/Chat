"""Embedding provider abstraction supporting local (sentence-transformers) and OpenAI."""
from functools import lru_cache
from typing import List

from ..config import settings


class EmbeddingProvider:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        return self.embed([text])[0]

    @property
    def dim(self) -> int:
        raise NotImplementedError


class LocalEmbeddings(EmbeddingProvider):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self._dim = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    @property
    def dim(self) -> int:
        return self._dim


class OpenAIEmbeddings(EmbeddingProvider):
    def __init__(self, api_key: str, model: str):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._dim = 1536  # text-embedding-3-small default

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Batch in chunks of 64
        out: List[List[float]] = []
        for i in range(0, len(texts), 64):
            batch = texts[i : i + 64]
            resp = self._client.embeddings.create(model=self._model, input=batch)
            data = sorted(resp.data, key=lambda d: d.index)
            out.extend([d.embedding for d in data])
        return out

    @property
    def dim(self) -> int:
        return self._dim


@lru_cache
def get_embeddings() -> EmbeddingProvider:
    if settings.llm_provider == "openai":
        return OpenAIEmbeddings(settings.openai_api_key, settings.openai_embedding_model)
    return LocalEmbeddings(settings.embedding_model)
