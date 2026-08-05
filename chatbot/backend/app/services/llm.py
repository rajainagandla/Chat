"""LLM provider abstraction supporting local (Ollama) and OpenAI."""
from functools import lru_cache
from typing import Generator

from ..config import settings


class LLMProvider:
    """Unified interface for text generation."""

    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError

    def stream(self, system: str, user: str) -> Generator[str, None, None]:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _request(self, system: str, user: str, stream: bool):
        import httpx

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": stream,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        return httpx.post(url, json=payload, timeout=120)

    def complete(self, system: str, user: str) -> str:
        resp = self._request(system, user, stream=False)
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()

    def stream(self, system: str, user: str) -> Generator[str, None, None]:
        import httpx

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "stream": True,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        with httpx.stream("POST", url, json=payload, timeout=120) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    import json

                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                except Exception:
                    continue


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        except ImportError:
            self._client = None

    def complete(self, system: str, user: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content.strip()

    def stream(self, system: str, user: str) -> Generator[str, None, None]:
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


@lru_cache
def get_llm() -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    return OllamaProvider(settings.ollama_base_url, settings.ollama_model)
