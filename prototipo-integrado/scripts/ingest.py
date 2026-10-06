import asyncio
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.providers.ollama import OllamaProvider
from app.services.rag_service import (
    DocumentAlreadyProcessingError,
    DocumentNotFoundError,
    RAGService,
)


async def main(document_id: str) -> None:
    try:
        parsed_id = UUID(document_id)
    except ValueError as exc:
        raise SystemExit("document_id precisa ser um UUID válido.") from exc

    async with SessionLocal() as db:
        try:
            chunks = await RAGService(db, OllamaProvider()).ingest_document(parsed_id)
        except DocumentNotFoundError as exc:
            raise SystemExit(str(exc)) from exc
        except DocumentAlreadyProcessingError as exc:
            raise SystemExit(str(exc)) from exc
        except Exception as exc:
            raise SystemExit(f"Falha na ingestão: {exc}") from exc
        print(f"Documento indexado: {chunks} chunks.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python -m scripts.ingest <document_id>")
    asyncio.run(main(sys.argv[1]))
