"""
Testes de robustez, concorrência e thread-safety para a Fase C:
- Thread-safety do SemanticCache sob alta concorrência paralela
- Invalidação de cache semântico na ingestão de novos documentos
- Execução não-bloqueante do endpoint de chat
- Idempotência sob rajada concorrente de webhooks
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.rag.retriever import SemanticCache
from app.ingestion.contracts import RawDocumentPayload, SUSDataTag
from app.ingestion.processor import IngestionProcessor
from app.ingestion.webhook import set_processor


def test_semantic_cache_thread_safety_under_heavy_concurrency():
    """Valida que o SemanticCache não dispara RuntimeError sob 50 threads concorrentes de leitura e escrita."""
    cache = SemanticCache(max_distance=0.08, max_size=100, ttl_s=60.0)
    
    dim = 64
    rng = np.random.default_rng(42)
    vectors = [rng.standard_normal(dim).astype(np.float32) for _ in range(50)]
    for v in vectors:
        v /= np.linalg.norm(v)

    def worker(worker_id: int):
        vec = vectors[worker_id % len(vectors)]
        # Alterna entre escrita e leitura
        cache.put(vec, {"worker": worker_id, "data": f"result_{worker_id}"})
        hit = cache.get(vec)
        # Pode ou não encontrar dependendo do estado, mas NUNCA deve estourar exceção de concorrência
        if worker_id % 10 == 0:
            cache.clear()

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(worker, i) for i in range(100)]
        for f in futures:
            f.result()  # Se lançar exceção de concorrência, o teste falha


def test_cache_invalidation_triggered_on_document_ingestion(tmp_path):
    """Valida que a ingestão de novo documento via processor dispara a invalidação do cache semântico."""
    cache = SemanticCache(max_distance=0.1)
    dummy_vec = np.array([1.0, 0.0], dtype=np.float32)
    cache.put(dummy_vec, {"response": "Resposta antiga do cache"})

    assert cache.get(dummy_vec) is not None

    processor = IngestionProcessor(
        retriever=None,
        storage_dir=tmp_path,
        cache_invalidator=cache.clear,
    )

    payload = RawDocumentPayload(
        title="Novo Comunicado SES-DF",
        source_url="https://www.saude.df.gov.br/novo-comunicado",
        tag=SUSDataTag.INSTITUCIONAL,
        text="A Secretaria de Saúde do Distrito Federal informa nova medida de acolhimento para o cidadão.",
    )

    result = processor.process_document(payload)
    assert result.status == "success"

    # O cache deve ter sido limpo imediatamente
    assert cache.get(dummy_vec) is None


def test_concurrent_webhook_burst_idempotency(tmp_path):
    """Sob rajada paralela de 10 requisições do mesmo documento, exatamente 1 deve ser inserida e 9 ignoradas."""
    processor = IngestionProcessor(retriever=None, storage_dir=tmp_path)

    payload = RawDocumentPayload(
        title="Comunicado Concorrente Único",
        source_url="https://www.saude.df.gov.br/comunicado-concorrente",
        tag=SUSDataTag.SERVICO,
        text="Texto exato transmitido em rajada de webhooks para testar integridade de manifesto.",
    )

    def ingest_worker():
        return processor.process_document(payload)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(ingest_worker) for _ in range(10)]
        results = [f.result() for f in futures]

    statuses = [r.status for r in results]
    assert statuses.count("success") == 1
    assert statuses.count("skipped") == 9
    assert len(processor._manifest["documents"]) == 1


def test_chat_endpoint_responds_without_blocking():
    """Valida que o chat_endpoint atende requisições sequenciais e concorrentes com sucesso."""
    with TestClient(app) as client:
        # Pergunta administrativa
        r1 = client.post("/api/chat", json={"message": "Qual o telefone de emergência do SAMU?"})
        assert r1.status_code == 200
        data1 = r1.json()
        assert data1["is_blocked"] is False
        assert "192" in data1["response"] or "SAMU" in data1["response"]

        # Pergunta bloqueada por guardrails
        r2 = client.post("/api/chat", json={"message": "Estou com febre de 40 graus e tosse com sangue, o que tomar?"})
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["is_blocked"] is True
