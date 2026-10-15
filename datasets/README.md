# Datasets & Corpus Oficial

Este diretório concentra o catálogo, dados brutos, documentos higienizados e bases de avaliação do projeto **SUSANA (Meu SUS Brasília)**.

Consulte a documentação completa no [Catálogo do Corpus Oficial](file:///Users/aluno2/SUSANA/datasets/catalogo_do_corpus.md).

---

## 📁 Estrutura de Pastas

* **[`corpus/`](file:///Users/aluno2/SUSANA/datasets/corpus/)**: Documentos estruturados (JSON e TXT) indexados pelo RAG Híbrido (**ChromaDB + BM25**), contendo a REME-DF 2025, 346 blocos clínicos das 35 RAs do DF, FAQs oficiais do Meu SUS Digital, manuais de vacinação e protocolos da SES-DF.
* **[`raw/`](file:///Users/aluno2/SUSANA/datasets/raw/)**: Dados tabulares primários (CSV) contendo o cadastro oficial de UBSs, UPAs, Hospitais, Policlínicas, CAPS e divisão político-administrativa do Distrito Federal.
* **[`eval/`](file:///Users/aluno2/SUSANA/datasets/eval/)**: Conjuntos de dados rotulados para avaliação de alucinações, testes *In-Domain* / *Out-of-Domain* (OOD) e o dataset de treinamento da camada de **Guardrails** clínicos.
* **[`catalogo_do_corpus.md`](file:///Users/aluno2/SUSANA/datasets/catalogo_do_corpus.md)**: Inventário detalhado das 9 fontes oficiais, dicionário de tags, metadados semânticos e conformidade com a LGPD.
