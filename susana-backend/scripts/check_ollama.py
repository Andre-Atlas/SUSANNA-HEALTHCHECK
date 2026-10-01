import asyncio

from app.core.config import get_settings
from app.providers.ollama import OllamaProvider


async def main() -> int:
    settings = get_settings()
    provider = OllamaProvider()
    print(f"Ollama: {settings.ollama_base_url}")
    print(f"Chat model: {settings.ollama_model or '<não configurado>'}")
    print(f"Embedding model: {settings.embedding_model or '<não configurado>'}")
    print(f"Embedding dimensions esperadas: {settings.embedding_dimensions}")

    if not settings.embedding_model:
        print("Configure EMBEDDING_MODEL antes do teste.")
        return 2

    try:
        vector = await provider.embed("teste de embedding da Susana")
    except Exception as exc:
        print(f"Falha: {exc}")
        return 1

    print(f"Embedding recebido: {len(vector)} dimensões")
    print("Configuração de embedding compatível.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
