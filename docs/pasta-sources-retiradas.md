# Pasta `sources/retiradas/`

Arquiva documentos JSON de fontes que foram retiradas do conjunto ativo. Mantê-los separados preserva o histórico e permite entender decisões anteriores sem incluí-los na importação normal da base local.

O `seed_knowledge.py` percorre apenas os arquivos JSON diretamente em `sources/`, portanto este subdiretório não é importado automaticamente. Os arquivos arquivados também não são consultados pelo chat online.
