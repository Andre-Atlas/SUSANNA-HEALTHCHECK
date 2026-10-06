import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.source import Source
from app.providers.ollama import OllamaProvider
from app.services.rag_service import RAGService


@dataclass(frozen=True)
class MarkdownDocument:
    title: str
    category: str
    source_name: str
    source_url: str
    source_description: str
    content: str
    filename: str


def load_approved_documents(manifest_path: Path) -> tuple[list[MarkdownDocument], list[tuple[str, str]]]:
    manifest_path = manifest_path.resolve()
    data_root = manifest_path.parent.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    approved: list[MarkdownDocument] = []
    skipped: list[tuple[str, str]] = []

    for item in manifest.get("documents", []):
        filename = item.get("file", "")
        if item.get("status") != "approved":
            skipped.append((filename or "(sem nome)", item.get("status", "sem status")))
            continue

        path = (data_root / filename).resolve()
        if path.parent != data_root or path.suffix.lower() != ".md":
            raise ValueError(f"Caminho Markdown inválido no manifesto: {filename}")

        required = ("title", "category", "source_name", "source_url")
        missing = [key for key in required if not item.get(key)]
        if missing:
            raise ValueError(f"Metadados ausentes para {filename}: {', '.join(missing)}")

        source_url = item["source_url"]
        parsed_url = urlparse(source_url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ValueError(f"A origem precisa ser uma URL HTTPS: {filename}")

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            skipped.append((filename, "arquivo vazio"))
            continue

        approved.append(
            MarkdownDocument(
                title=item["title"],
                category=item["category"],
                source_name=item["source_name"],
                source_url=source_url,
                source_description=item.get("source_description", ""),
                content=content,
                filename=filename,
            )
        )

    return approved, skipped


async def ingest_documents(documents: list[MarkdownDocument]) -> None:
    provider = OllamaProvider()
    async with SessionLocal() as db:
        for item in documents:
            source = await db.scalar(select(Source).where(Source.url == item.source_url))
            if source is None:
                source = Source(
                    name=item.source_name,
                    url=item.source_url,
                    source_type="official",
                    description=item.source_description,
                )
                db.add(source)
                await db.flush()

            document = await db.scalar(
                select(Document).where(
                    Document.source_id == source.id,
                    Document.url == item.source_url,
                    Document.title == item.title,
                )
            )

            if document is None:
                document = Document(
                    source_id=source.id,
                    title=item.title,
                    category=item.category,
                    url=item.source_url,
                    content=item.content,
                    status="pending",
                )
                db.add(document)
                await db.commit()
                await db.refresh(document)
            elif document.content == item.content and document.status == "indexed":
                print(f"Já indexado, sem mudanças: {item.filename}")
                continue
            else:
                document.content = item.content
                document.category = item.category
                document.status = "pending"
                document.content_hash = None
                await db.commit()

            chunks = await RAGService(db, provider).ingest_document(document.id)
            print(f"Indexado: {item.filename} ({chunks} trechos), origem {source.url}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexa somente os Markdown marcados como approved em DADOS/manifest.json."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("../DADOS/manifest.json"),
        help="Caminho do manifesto; padrão relativo à pasta susana-backend.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Grava documentos e gera embeddings. Sem esta opção, apenas mostra o plano.",
    )
    args = parser.parse_args()

    documents, skipped = load_approved_documents(args.manifest)
    if not documents:
        raise SystemExit("Nenhum Markdown aprovado para ingestão.")

    print(f"Documentos aprovados: {len(documents)}")
    for item in documents:
        print(f"- {item.filename}: {item.title} -> {item.source_url}")
    for filename, reason in skipped:
        print(f"IGNORADO: {filename} ({reason})")

    if args.apply:
        asyncio.run(ingest_documents(documents))
    else:
        print("Prévia apenas. Revise o plano; use --apply para indexar.")


if __name__ == "__main__":
    main()