# Datasets & Corpus Oficial

Este diretório concentra a base de conhecimento do RAG, as tabelas cadastrais da rede de saúde do DF, os conjuntos de avaliação e os insumos das EDAs do projeto **SUSANA (Meu SUS Brasília)**.

O inventário completo, com origem, qualidade e pendências de cada arquivo, está no [Catálogo do Corpus](catalogo_do_corpus.md).

---

## 📁 Estrutura de pastas

| Pasta | Conteúdo | Lido pelo indexador do RAG? |
| :--- | :--- | :---: |
| [`corpus/`](corpus/) | 21 arquivos JSON/TXT: REME-DF 2025, páginas oficiais da SES-DF transcritas, FAQ do Meu SUS Digital e diretório por região | Sim |
| [`raw/`](raw/) | 14 tabelas CSV (`;`): UBS, UPAs, hospitais, policlínicas, CAPS, regiões administrativas e de saúde | Sim |
| [`eval/`](eval/) | Dataset do guardrail clínico (283 exemplos) e partições de recuperação *in-domain*/*out-of-domain* (20/20/15/15) | Não |
| [`eda_inputs/`](eda_inputs/) | 4 bases públicas usadas pelo notebook `eda_sus_digital` | Não |

---

## 🔢 Números verificados

* **2.283 blocos** indexados ao aplicar o indexador do backend sobre `corpus/` + `raw/`.
* **54%** do índice vem da REME-DF 2025 (transcrição por OCR, com revisão pendente).
* O diretório por região tem **346 blocos** (70 UBS, 33 regiões), e não 346 unidades.

> ⚠️ Antes da apresentação, consulte a [seção 7 do catálogo](catalogo_do_corpus.md#7-pendências-de-qualidade-antes-da-apresentação): há arquivos de teste e de exemplo dentro de `corpus/` e links de origem do diretório que retornam 404.
