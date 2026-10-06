import hashlib

from app.providers.base import EmbeddingProvider, LLMProvider


class FakeLLMProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        return "Resposta de teste. Esta resposta não representa informação oficial."


class FakeEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 768) -> None:
        self.dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [byte / 255.0 for byte in digest]
        return (values * ((self.dimensions // len(values)) + 1))[: self.dimensions]
