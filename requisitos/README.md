# Requisitos Funcionais e Não Funcionais

Este diretório documenta a especificação técnica dos requisitos do sistema **Meu SUS Brasília (SUSANA)**.

Consulte a especificação completa e rastreabilidade em: [Especificação de Requisitos](file:///Users/aluno2/SUSANA/requisitos/requisitos_susana.md).

## 📋 Categorias de Requisitos
- **Requisitos Funcionais (RF):**
  - Busca e localização de Unidades Básicas de Saúde (UBS), UPAs e Hospitais por Região Administrativa.
  - Informações completas sobre o Componente Especializado (Farmácia de Alto Custo), documentos e laudo LME.
  - Consulta de calendários de vacinação e recomendações por faixa etária.
  - Navegação multi-turn com resolução de anáforas e toponímia do Distrito Federal.
- **Requisitos Não Funcionais (RNF):**
  - Guardrail de segurança clínica com bloqueio instantâneo (< 10ms) de tentativas de automedicação.
  - Zero alucinações de telefones inexistentes (restrito a 160, 136 e 192).
  - Execução de inferência local (privacidade de dados e conformidade com LGPD).
  - Busca Híbrida combinando vetores densos (ChromaDB) e léxico exato (BM25 com RRF).
