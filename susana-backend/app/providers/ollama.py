import httpx

from app.core.config import get_settings
from app.providers.base import EmbeddingProvider, LLMProvider


class OllamaProvider(LLMProvider, EmbeddingProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.embedding_model = settings.embedding_model
        self.timeout = settings.ollama_timeout_seconds

    async def generate(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("OLLAMA_MODEL não configurado.")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            result = str(data.get("response", "")).strip()
            if not result:
                raise RuntimeError("Ollama não retornou uma resposta.")
            return result

    async def embed(self, text: str) -> list[float]:
        if not self.embedding_model:
            raise RuntimeError("EMBEDDING_MODEL não configurado.")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.embedding_model, "input": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings = data.get("embeddings") or []
            if not embeddings or not isinstance(embeddings[0], list):
                raise RuntimeError("Ollama não retornou embedding em formato válido.")
            vector = [float(value) for value in embeddings[0]]
            expected = get_settings().embedding_dimensions
            if len(vector) != expected:
                raise RuntimeError(
                    f"Dimensão do embedding incompatível: recebido={len(vector)}, esperado={expected}."
                )
            return vector
