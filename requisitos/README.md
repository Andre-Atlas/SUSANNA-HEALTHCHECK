# Requisitos Funcionais e Não Funcionais

Este diretório documenta a especificação técnica dos requisitos do sistema **Meu SUS Brasília (SUSANA)**.

Consulte a especificação completa e rastreabilidade em: [Especificação de Requisitos](requisitos_susana.md).

**Resumo:** 43 requisitos (25 RF e 18 RNF). A versão final acrescentou conta opcional, agenda com lembretes criados pelo chat, vacinas pendentes por perfil, monitoramento epidemiológico, segurança/LGPD e implantação (seção 7 do documento).

## 📋 Categorias de Requisitos
- **Requisitos Funcionais (RF):**
  - Busca e localização de Unidades Básicas de Saúde (UBS), UPAs e Hospitais por Região Administrativa.
  - Informações completas sobre o Componente Especializado (Farmácia de Alto Custo), documentos e laudo LME.
  - Consulta de calendários de vacinação e recomendações por faixa etária.
  - Navegação multi-turn com resolução de anáforas e toponímia do Distrito Federal.
  - Conta opcional (CPF + senha, sessão persistente), perfil de saúde e exclusão de conta.
  - Vacinas pendentes por perfil e agenda pessoal com lembretes criados pelo chat, com confirmação do cidadão.
  - Monitoramento epidemiológico com dados oficiais.
- **Requisitos Não Funcionais (RNF):**
  - Guardrail de segurança clínica com bloqueio instantâneo (< 10ms) de tentativas de automedicação.
  - Zero alucinações de telefones inexistentes (restrito a 160, 136 e 192).
  - Execução de inferência local (privacidade de dados e conformidade com LGPD).
  - Segurança de contas (hash de senha, sessões, limite de tentativas) e minimização de dados enviados ao modelo.
  - HTTPS e implantação reprodutível em contêineres.
  - Recuperação vetorial (ChromaDB) com filtro por Região Administrativa e casamento lexical de termos e entidades.
