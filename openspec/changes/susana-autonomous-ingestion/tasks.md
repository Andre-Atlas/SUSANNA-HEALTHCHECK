# Tarefas: Ingestão Autônoma, Desenviesamento e Concorrência

## Fase A: Segurança, Isolamento e Correção do Índice
- [x] Sanitizar `.git/config` removendo tokens em texto claro do remote.
- [x] Implementar método `upsert(blocks)` e `delete_by_url(url)` no `ChromaRetriever`.
- [x] Atualizar `IngestionProcessor` para usar `upsert` e separar manifesto em `ingestion_manifest.json`.
- [x] Enforçar TLS obrigatório (`verify=True`) no `SESDFScraper`.
- [x] Implementar autenticação fail-closed no webhook (`X-Ingestion-Key`).
- [x] Enforçar allowlist estrita de domínios oficiais (`ALLOWED_SUS_DOMAINS`).
- [x] Testes de regressão da pipeline de ingestão (9 testes passando).
- [x] Homologação unânime da Fase A pelo Conselho da Trindade (3/3).

## Fase B: Avaliação Honesta e Desenviesamento
- [x] Criar datasets congelados e isolados DEV e TEST (`in_domain_dev.json`, `in_domain_test.json`, `ood_dev.json`, `ood_test.json`).
- [x] Implementar portão relativo de promoção de modelos no MLflow (`CV F1 >= champion - 0.02` e `recall >= 0.95`).
- [x] Expandir `_GENERIC_GEO_TERMS`, `_STOPWORDS` e incluir `_HEALTH_TERMS` no `retriever.py`.
- [x] Calibrar `relevance_confident_threshold: 0.35` protegendo mocks e bloqueando OOD.
- [x] Integrar corpus oficial com Banco de Leite Humano SES-DF no `dados_abertos.txt`.
- [x] Executar benchmark honesto: 0.0% OOD leak, 0.0% FN rejection, 95% Recall@1 e Recall@3.
- [x] Homologação unânime da Fase B pelo Conselho da Trindade (3/3).

## Fase C: Concorrência sem Bloqueio e Invalidação de Cache
- [x] Tornar `chat_endpoint` e `chat_stream_endpoint` não-bloqueantes usando `run_in_threadpool`.
- [x] Implementar thread-safety reentrante (`threading.RLock()`) no `SemanticCache`.
- [x] Criar hook de invalidação atômica de cache (`cache_invalidator`) no `IngestionProcessor`.
- [x] Mitigar TOCTOU com seção crítica sincronizada sob rajada concorrente no webhook.
- [x] Desenvolver suíte de testes de concorrência (`tests/test_concurrency_robustness.py`).
- [x] Executar suíte completa de testes do backend: 52/52 testes passando (100% Green).
- [x] Homologação unânime da Fase C pelo Conselho da Trindade (3/3).

## Fase D: Governança OpenSpec e Homologação Final
- [x] Elaborar proposta, design (ADRs), especificações delta e tarefas no OpenSpec.
- [x] Atualizar artefato vivo de rastreabilidade e walkthrough (`walkthrough.md`).
- [x] Validar estrita conformidade com restrição de ausência de commits diretos no Git.
- [x] Concluir ciclo do plano orquestrado.
