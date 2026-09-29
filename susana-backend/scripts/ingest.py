import asyncio
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.models.document import Document
from app.providers.ollama import OllamaProvider
from app.services.rag_service import RAGService


async def main(document_id: str) -> None:
    async with SessionLocal() as db:
        document = await db.get(Document, UUID(document_id))
        if not document: raise SystemExit("Documento não encontrado.")
        chunks = await RAGService(db, OllamaProvider()).ingest(document)
        print(f"Documento indexado: {chunks} chunks.")


if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit("Uso: python -m scripts.ingest <document_id>")
    asyncio.run(main(sys.argv[1]))
