# Proposta: Ingestão Autônoma, Avaliação Honesta e Concorrência Não-Bloqueante

## 1. Contexto e Motivação
A assistente virtual administrativa Susana (SUS-DF) necessita de atualização contínua de sua base de conhecimento através de fontes oficiais do ecossistema do SUS (Secretaria de Saúde do DF - `saude.df.gov.br`, Portal de Dados Abertos - `dados.df.gov.br`, Ministério da Saúde - `gov.br`).

A arquitetura original apresentava três vulnerabilidades críticas:
1. **Destruição Involuntária de Índice:** O método de indexação no ChromaDB expurgava blocos existentes não presentes na carga atual.
2. **Viés e Vazamento Fora de Domínio (OOD):** A função de relevância sofria falsos positivos com perguntas não relacionadas a saúde devido à colisão de topônimos do DF (Taguatinga, Samambaia, etc.) e falsos negativos em perguntas naturais de cidadãos.
3. **Bloqueio de Event Loop e Invalidação Ausente:** Operações de inferência síncronas bloqueavam o event loop do FastAPI e o `SemanticCache` permanecia com dados obsoletos após novas ingestões.

## 2. Escopo da Mudança
- **Fase A (Segurança & Isolamento):** Sanitização de credenciais Git, métodos `upsert` e `delete_by_url` cirúrgicos no ChromaDB, isolamento do manifesto em `ingestion_manifest.json`, enforcement de TLS obrigatório (`verify=True`), autenticação fail-closed por chave secreta no webhook e allowlist estrita de domínios oficiais do SUS.
- **Fase B (Avaliação Honesta & Desenviesamento):** Criação de datasets congelados DEV/TEST (20 in-domain, 15 OOD em cada partição), calibração léxico-semântica em `is_relevant` com `_GENERIC_GEO_TERMS`, `_HEALTH_TERMS` e `_STOPWORDS`, e portão relativo de promoção de modelos no MLflow (`CV F1 >= champion - 0.02` e `recall >= 0.95`).
- **Fase C (Concorrência & Confiabilidade):** Despacho de rotinas intensivas via `run_in_threadpool`, proteção de thread-safety com `RLock` no `SemanticCache`, hook de invalidação atômica de cache após ingestão e idempotência garantida contra rajadas concorrentes de webhooks (TOCTOU mitigado).
- **Fase D (Governança & Homologação):** Governança OpenSpec, documentação viva, auditoria do Conselho da Trindade e suíte de testes 100% verde (52/52).

## 3. Impacto e Riscos Mitigados
- **Integridade da Base:** Elimina o risco de perda acidental de conhecimento durante ingestão diária ou scraping autônomo.
- **Segurança da Informação:** Apenas fontes institucionais autorizadas podem ser ingeridas; webhooks sem credencial válida são sumariamente rejeitados com HTTP 403.
- **Experiência do Usuário (UX/Latência):** P50 de busca reduzido para 21.73ms, ausência de travamentos no streaming ou na API REST, e dados sempre frescos após comunicados oficiais.
