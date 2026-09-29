import asyncio
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.models.document import Document
from app.providers.ollama import OllamaProvider
from app.services.rag_service import RAGService


async def main(document_id: str) -> None:
    try:
        parsed_id = UUID(document_id)
    except ValueError as exc:
        raise SystemExit("document_id precisa ser um UUID válido.") from exc

    async with SessionLocal() as db:
        document = await db.get(Document, parsed_id)
        if not document:
            raise SystemExit("Documento não encontrado.")
        try:
            chunks = await RAGService(db, OllamaProvider()).ingest(document)
        except Exception as exc:
            await db.rollback()
            raise SystemExit(f"Falha na ingestão: {exc}") from exc
        print(f"Documento indexado: {chunks} chunks.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python -m scripts.ingest <document_id>")
    asyncio.run(main(sys.argv[1]))
