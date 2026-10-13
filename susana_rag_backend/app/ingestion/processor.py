"""Processador incremental de ingestão e indexação contínua no ChromaDB."""
from __future__ import annotations

import hashlib
import json
import logging
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from app.config import get_settings
from app.ingestion.contracts import IngestionResult, RawDocumentPayload, SUSDataTag
from app.rag.corpus import CorpusBlock, _block_id, _chunks

logger = logging.getLogger("susana.ingestion.processor")


class IngestionProcessor:
    """Processa documentos crus, aplica deduplicação por SHA-256 e indexa no ChromaDB."""

    def __init__(
        self,
        retriever=None,
        storage_dir: Optional[Path] = None,
        cache_invalidator=None,
    ):
        self.settings = get_settings()
        self.retriever = retriever
        self.cache_invalidator = cache_invalidator
        self.storage_dir = storage_dir or (self.settings.docs_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.storage_dir / "ingestion_manifest.json"
        self.ingested_corpus_file = self.storage_dir / "ingested_sus.txt"
        self._lock = threading.RLock()
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_file.exists():
            try:
                data = json.loads(self.manifest_file.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "documents" in data:
                    return data
                elif isinstance(data, list):
                    docs = {d.get("sha256", f"doc_{i}"): d for i, d in enumerate(data)}
                    return {"documents": docs}
            except Exception as e:
                logger.warning("Falha ao ler %s existente, iniciando vazio: %s", self.manifest_file.name, e)
        return {"documents": {}}

    def _save_manifest(self) -> None:
        try:
            self.manifest_file.write_text(
                json.dumps(self._manifest, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error("Erro ao persistir manifest.json: %s", e)

    @staticmethod
    def compute_hash(text: str, url: str) -> str:
        content = f"{url.strip().lower()}|{text.strip()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def process_document(self, payload: RawDocumentPayload) -> IngestionResult:
        with self._lock:
            return self._process_document_unlocked(payload)

    def _process_document_unlocked(self, payload: RawDocumentPayload) -> IngestionResult:
        doc_hash = self.compute_hash(payload.text, payload.source_url)
        
        # 1. Checagem de duplicidade
        if doc_hash in self._manifest["documents"]:
            logger.info("Documento duplicado ignorado: %s (hash: %s)", payload.title[:50], doc_hash[:10])
            return IngestionResult(
                status="skipped",
                document_id=doc_hash,
                chunks_created=0,
                is_duplicate=True,
                message="Documento com mesmo conteúdo e URL já indexado anteriormente.",
            )

        # 2. Chunking semântico
        normalized_text = re.sub(r"\s+", " ", payload.text).strip()
        chunks = list(_chunks(normalized_text, max_chars=900))
        if not chunks:
            return IngestionResult(
                status="error",
                document_id=doc_hash,
                chunks_created=0,
                is_duplicate=False,
                message="Conteúdo vazio após normalização.",
            )

        new_blocks: List[CorpusBlock] = []
        for index, chunk in enumerate(chunks, 1):
            suffix = f" (parte {index})" if len(chunks) > 1 else ""
            header = f"[{payload.tag.value}] {payload.title}{suffix}"
            block_text = f"{header}\n{chunk}\nFonte: {payload.source_url}".strip()
            block_id = _block_id(f"{payload.source_url}\n{block_text}")
            new_blocks.append(
                CorpusBlock(
                    id=block_id,
                    header=header,
                    tag=payload.tag.value,
                    text=block_text,
                    url=str(payload.source_url),
                )
            )

        # 3. Persistência incremental em arquivo de texto
        try:
            with self.ingested_corpus_file.open("a", encoding="utf-8") as f:
                for block in new_blocks:
                    f.write(f"{block.text}\n\n")
        except Exception as e:
            logger.warning("Falha ao gravar em ingested_sus.txt: %s", e)

        # 4. Inserção incremental no ChromaDB (se retriever fornecido)
        indexed_count = 0
        if self.retriever is not None:
            try:
                # Se a URL já foi indexada anteriormente com conteúdo diferente, expurga blocos obsoletos
                url_str = str(payload.source_url)
                if hasattr(self.retriever, "delete_by_url"):
                    self.retriever.delete_by_url(url_str)

                # Upsert seguro: NÃO remove blocos pré-existentes de outros documentos
                if hasattr(self.retriever, "upsert"):
                    indexed_count = self.retriever.upsert(new_blocks, batch_size=32)
                else:
                    indexed_count = self.retriever.index(new_blocks, batch_size=32)
                logger.info("Upsert incremental de %d blocos no ChromaDB", indexed_count)
            except Exception as e:
                logger.error("Erro ao indexar no ChromaDB: %s", e)
                return IngestionResult(
                    status="error",
                    document_id=doc_hash,
                    chunks_created=0,
                    is_duplicate=False,
                    message=f"Falha na indexação vetorial: {e}",
                )
        else:
            indexed_count = len(new_blocks)

        # Invalidação do cache semântico para expurgar respostas antigas ou negativas
        if self.cache_invalidator is not None:
            try:
                self.cache_invalidator()
                logger.info("Cache semântico invalidado com sucesso após nova ingestão.")
            except Exception as e:
                logger.warning("Falha ao invalidar cache semântico: %s", e)

        # 5. Atualização do manifesto
        self._manifest["documents"][doc_hash] = {
            "title": payload.title,
            "url": str(payload.source_url),
            "tag": payload.tag.value,
            "author_or_department": payload.author_or_department,
            "fetched_at": payload.fetched_at.isoformat(),
            "indexed_at": datetime.now(timezone.utc).isoformat(),
            "chunks_count": len(new_blocks),
            "char_count": len(payload.text),
        }
        self._save_manifest()

        logger.info("Documento indexado com sucesso: %s (%d blocos)", payload.title[:50], len(new_blocks))
        return IngestionResult(
            status="success",
            document_id=doc_hash,
            chunks_created=len(new_blocks),
            is_duplicate=False,
            message=f"Documento indexado com sucesso ({len(new_blocks)} blocos gerados).",
        )
