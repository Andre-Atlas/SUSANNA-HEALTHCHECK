# Pasta `sources/`

Armazena documentos JSON versionados com sínteses, trechos, títulos, URLs e datas de revisão. Eles servem ao conjunto experimental usado em avaliações offline e à construção/manutenção da base SQLite local.

No modo atual do chat, o servidor busca conteúdo ao vivo no gov.br e não consulta esses JSON para responder. O script `seed_knowledge.py` importa arquivos JSON diretamente desta pasta; o subdiretório `retiradas/` não entra nessa importação automática.

Edite ou acrescente fontes seguindo o formato esperado por `knowledge.py` e os critérios de revisão documental. Uma URL de origem, por si só, não significa que toda afirmação do documento foi validada.
