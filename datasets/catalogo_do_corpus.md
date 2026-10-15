# Catálogo do Corpus Oficial e Metadados — SUSANA (SES-DF)

> **Programa:** Residência em Inteligência Artificial — Instituto Eldorado  
> **Projeto:** Meu SUS Brasília (SUSANA)  
> **Metodologia:** Challenge-Based Learning (CBL) — Challenge 1: Fake News / Desinformação  
> **Status:** Homologado / Corpus Versão 2.0 (Outubro 2026)  

---

## 1. Visão Geral do Corpus

O corpus do projeto **SUSANA** é uma base de conhecimento controlada, auditada e estruturada, projetada para alimentar a arquitetura de **Recuperação Aumentada por Geração (RAG Híbrido)**. Em estrito alinhamento com a *Essential Question* do Challenge 1 (*como sistemas de IA podem apoiar o pensamento crítico sem substituir a autoridade do usuário*), o corpus baseia-se exclusivamente em **fontes primárias oficiais de saúde pública**, eliminando especulações, boatos e prescrições não autorizadas.

O corpus encontra-se particionado em três camadas lógicas dentro do diretório `datasets/`:

```text
datasets/
├── corpus/               # Documentos estruturados (JSON e TXT) indexados pelo RAG
│   ├── diretorio_saude_df.json                          # 346 blocos clínicos/territoriais das 35 RAs
│   ├── 01_REME_DF_2025_Medicamentos.json                # Catálogo oficial REME-DF 2025
│   ├── 02_HUB_Farmacia_Escola.json                      # Componente Farmácia Escola HUB/UnB
│   ├── 03_Componente_Especializado_Alto_Custo.json      # Protocolos e unidades CEAF
│   ├── 04_Farmacias_Vivas_Fitoterapicos.json            # Fitoterapia oficial da SES-DF
│   ├── meu_sus_digital_faq_estruturado.json             # Perguntas frequentes Meu SUS Digital
│   ├── Unidades-Básicas-de-Saúde-(UBS)-SES-DF.json      # Catálogo de UBSs e serviços
│   ├── Atendimento-Urgencia-Emergencia-UPAs-Hosp.json   # Rede 24h e fluxos de gravidade
│   ├── Saúde-Mental-SES-DF.json                         # Rede de Atenção Psicossocial (CAPS)
│   ├── Práticas-Integrativas-em-Saúde-SES-DF.json       # PICS (acupuntura, reiki, fitoterapia)
│   ├── Maternidades.json                                # Centros obstétricos e pré-natal
│   ├── Centro-de-Testagem-e-Aconselhamento-CTA.json     # ISTs, HIV e profilaxias PEP/PrEP
│   ├── Busca-Saúde-CEPAV.json                           # Atendimento a vítimas de violência
│   ├── Hran-animais-peçonhentos.json                    # Soros e referência do HRAN
│   ├── sesdf_public.txt / dados_abertos.txt             # Guias gerais e dados abertos GDF
│   ├── ingested_sus.txt / sus_docs.txt                  # Telefones institucionais (136, 160, 192)
│   └── manifest.json / ingestion_manifest.json          # Metadados de integridade e hashes
├── raw/                  # Tabelas brutas (CSV) de estabelecimentos e toponímia do DF
│   ├── Unidade_Básica_de_Saúde.csv                      # Lista nominal de 176+ UBSs
│   ├── Unidades_de_Pronto_Atendi.csv                    # UPAs com CNES e endereços
│   ├── Hospitais.csv                                    # Hospitais Regionais e Especializados
│   ├── Policlínicas.csv                                 # Policlínicas distritais
│   ├── Centros_Especializados.csv                       # Centros de reabilitação e odontologia
│   ├── Centros_de_Atenção_Psicos.csv                    # CAPS I, II, III e álcool/drogas
│   ├── Regiões_Administrativas.csv                      # 35 RAs oficiais do Distrito Federal
│   ├── Regiões_de_Saúde.csv                             # 7 Regiões de Saúde (Central, Norte, etc.)
│   ├── Macrorregiões_de_Saúde.csv                       # Estrutura macrorregional do DF
│   └── Outras_Unidades_de_Saúde.csv                     # Unidades móveis, consultórios de rua
└── eval/                 # Datasets de validação, guardrails e benchmark
    ├── guardrails_dataset.csv                           # 284 intenções clínicas e operacionais
    ├── in_domain_dev.json / in_domain_test.json         # Perguntas in-domain para avaliação RAG
    └── ood_dev.json / ood_test.json                     # Cenários fora de domínio (Out-of-Domain)
```

---

## 2. Inventário Detalhado das Fontes Oficiais

| Código da Fonte | Órgão Mantenedor | Instrumento / Base de Dados | Formato | Volume / Registros | Finalidade no Sistema |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **SRC-01** | SES-DF | Relação de Medicamentos do DF (REME-DF 2025) | JSON | 3,5 MB / 600+ fármacos | Orientação sobre disponibilidade na APS, farmácias de alto custo e laudos LME. |
| **SRC-02** | SES-DF / DATASUS | Cadastro Nacional de Estabelecimentos (CNES) | CSV / JSON | 176+ UBS, 14 UPAs, 16 Hospitais | Toponímia, geolocalização e vínculo institucional por RA. |
| **SRC-03** | SES-DF | Diretório Estruturado de Saúde do DF (V2.0) | JSON | 346 blocos semânticos | Busca Híbrida RAG com metadados de serviços, horários e referências. |
| **SRC-04** | Min. da Saúde / DATASUS | Cartilha Meu SUS Digital | JSON | 85 tópicos estruturados | Resolução de dúvidas sobre o aplicativo, cartão digital e agendamentos. |
| **SRC-05** | SES-DF (DIVEP) | Calendário Oficial de Imunização do DF | JSON / TXT | 22 imunobiológicos | Calendários completos da criança, gestante, adulto e idoso. |
| **SRC-06** | SES-DF (DIASF) | Componente Especializado (CEAF / Alto Custo) | JSON | 4 Farmácias (Asa Sul, Ceilândia, Gama, Taguatinga) | Requisitos documentais, laudo LME e locais de retirada. |
| **SRC-07** | SES-DF (DISAM) | Diretrizes da Rede de Atenção Psicossocial | JSON / CSV | 18 unidades CAPS | Acolhimento em saúde mental, sofrimento psíquico e dependência química. |
| **SRC-08** | GDF / SEGOV | Portal de Dados Abertos do DF (dados.df.gov.br) | CSV | 35 RAs, 7 Regiões | Desambiguação geográfica de setores e regiões administrativas. |
| **SRC-09** | Equipe SUSANA | Dataset de Guardrails Supervisionados | CSV | 284 exemplos rotulados | Treinamento do classificador SVM/TF-IDF contra automedicação e risco. |

---

## 3. Arquitetura de Metadados e Chunks RAG

Cada bloco indexado na coleção vetorial do **ChromaDB** e no índice léxico **BM25** adota uma taxonomia estrita para permitir filtragem contextual precisa:

### 3.1 Tags Estruturais
* `[UNIDADE_REGIONAL]`: Panorama da rede de saúde da Região Administrativa, elencando hospitais, UPAs e UBSs correspondentes.
* `[UNIDADE_UBS]`: Ficha completa da Unidade Básica de Saúde, endereço exato, horário de funcionamento regular e programa Saúde na Hora.
* `[VACINACAO]`: Relação de vacinas disponíveis na sala de imunização da unidade, exigência de caderneta e público-alvo.
* `[MEDICAMENTOS_FARMACIA]`: Itens da REME-DF, farmácia básica e orientações sobre receitas médicas.
* `[FARMACIA_ALTO_CUSTO]`: Instruções específicas do Componente Especializado da Assistência Farmacêutica (CEAF).
* `[URGENCIA_EMERGENCIA]`: Critérios de classificação de risco (Protocolo de Manchester), endereços de UPAs e emergências hospitalares.
* `[SAUDE_MENTAL_CAPS]`: Modalidades CAPS (Infantojuvenil, Adulto, Álcool e Outras Drogas).

### 3.2 Metadados Associados a Cada Bloco
```json
{
  "id": "e4f8a1290bc931f2",
  "header": "[UNIDADE_UBS] UBS 1 Ceilândia - Ceilândia (Oeste)",
  "tag": "UNIDADE_UBS",
  "url": "https://www.saude.df.gov.br/ubs-ceilandia",
  "metadata": {
    "cluster": "atencao_primaria",
    "ra": "ceilandia",
    "tipo_unidade": "ubs",
    "servicos": "saude_da_familia,vacinacao,prenatal,puericultura,farmacia_basica,odontologia"
  }
}
```

---

## 4. Higienização e Saneamento do Corpus

Durante a preparação da versão final (homologação 2.0), foram aplicados os seguintes tratamentos técnicos:
1. **Remoção de Caminhos Absolutos de Desenvolvimento:** Eliminação de referências locais (`/Users/...`, `/home/...`) nos cabeçalhos dos blocos para garantir conformidade e neutralidade.
2. **Correção de Encodings e Normalização Unicode:** Padronização em UTF-8 com NFKD, garantindo que termos com acentuação e cedilha (`Ceilândia`, `Taguatinga`, `Atenção Básica`) coincidam exatamente na busca léxica e semântica.
3. **Truncamento Inteligente de Chunks:** Segmentação com limite rígido de 900 caracteres por bloco com overlap de fronteira frasal, evitando quebras abruptas de endereços ou telefones.
4. **Governança de Telefones Oficiais:** O corpus foi auditado para erradicar números descontinuados ou fictícios, mantendo exclusivamente:
   * **160:** Ouvidoria e TeleSaúde do DF (SES-DF).
   * **136:** Disque Saúde do Ministério da Saúde.
   * **192:** Serviço de Atendimento Móvel de Urgência (SAMU DF).
   * **190:** Polícia Militar (casos de violência/apoio).

---

## 5. Governança, Ética e Conformidade com LGPD

* **Zero Dados Pessoais Identificáveis (PII):** Nenhum dado de prontuário, CPF, nome de paciente ou histórico clínico consta no corpus. Todos os documentos são de transparência ativa e acesso público.
* **Rastreabilidade Fidedigna:** 100% dos blocos indexados contam com metadado `url` apontando para páginas sob os domínios `.df.gov.br` ou `.saude.gov.br`.
* **Atualização Periódica:** As fontes tabulares e normativas possuem periodicidade de revisão trimestral, com versionamento incremental gerenciado via Git.
