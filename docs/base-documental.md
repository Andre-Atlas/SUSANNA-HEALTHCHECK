# Base documental local — primeira versão

Esta etapa usa Python, SQLite FTS5 e Ollama. Não requer serviço pago,
embeddings ou novos pacotes pip. O Python precisa ter SQLite com FTS5 habilitado.
Busca por palavras não compreende todos os sinônimos nem resolve perguntas
de continuidade como “e ela?”. A consulta considera a pergunta atual.

## Cadastrar uma fonte

Para as três sínteses iniciais, consulte o [relatório e registro de revisão](revisao-fontes.md). Ele registra a conferência por IA, sem atribuir aprovação humana e registra as pendências de reutilização.

A equipe deve selecionar e revisar o texto original e suas condições de uso.
Priorize documentos institucionais e registre a URL da página específica.
Não inclua dados pessoais. O cadastro não certifica a veracidade do documento.

Crie um arquivo JSON UTF-8 fora da pasta pública com estes campos:

```json
{
  "title": "Título real do documento",
  "url": "https://instituicao.example/documento",
  "reviewed_at": "2026-09-22",
  "text": "Texto real revisado pela equipe, preservando o contexto da fonte."
}
```

O exemplo é apenas um formato: não é uma fonte real e não deve ser importado.
`reviewed_at` registra a data de conferência documental, não a data de publicação nem aprovação clínica. No conjunto inicial essa conferência foi feita por IA; o status Revisado por IA está registrado nos JSONs.

```bash
python3 knowledge.py /caminho/para/documento.json
```

A importação divide o texto em trechos de até 1.200 caracteres e atualiza
atomicamente o documento identificado pela mesma URL. O índice fica em
`data/knowledge.sqlite3`, ignorado pelo Git. A URL não é baixada automaticamente.
Novas importações ficam disponíveis sem reiniciar o servidor.

## Como funciona

O conjunto ampliado contém seis sínteses. Consulte [temas, cobertura e manutenção](escopo-fontes.md), incluindo o procedimento de retirada por `python knowledge.py --remove-url "URL"`.

1. A pergunta atual é pesquisada no índice lexical FTS5.
2. Até 30 candidatos são ordenados por BM25. Para perguntas com vários termos, exigem-se pelo menos duas coincidências distintas; até três trechos são selecionados. Esse filtro é heurístico e não mede confiança factual.
3. O servidor ajusta histórico e trechos a um orçamento conservador de contexto.
4. O Ollama recebe as instruções, os trechos e a conversa restante.
5. A interface apresenta os trechos efetivamente enviados e seus links.

O orçamento usa bytes UTF-8 como estimativa conservadora para o Qwen padrão,
com reserva para resposta e template. Não é uma contagem exata de tokens.
Remove pares antigos de conversa e depois trechos, mantendo a pergunta atual.
Perguntas que sozinhas excedem o orçamento são recusadas com uma mensagem clara.

Sem base ou sem resultados, a interface informa a ausência de fontes. Uma base
corrompida gera erro explícito. Os documentos são dados, não instruções;
a resistência à injeção de prompt ainda precisa de avaliação adversarial.

## Limitações e próximas entregas

- O conjunto ampliado contém seis sínteses experimentais: carregue com `python3 seed_knowledge.py`. Status: Revisado por IA.
- Resultados lexicais podem ser irrelevantes. Não existe limiar calibrado de relevância.
- Links vêm dos registros locais; citações no texto ainda são geradas pelo modelo.
- Há revisão automática de apoio documental por IA e conferência de evidências literais; ela pode errar e não garante fidelidade factual.
- Não há atualização automática, extração de PDFs, busca semântica ou reranking.
- Antes do piloto: revisar as sínteses e ampliar o conjunto de perguntas com casos independentes. Os metadados de publicação, autoria e revisão por IA estão nos JSONs versionados; o índice atual mantém somente título, texto, URL e data de conferência.

Referências técnicas: [SQLite FTS5](https://www.sqlite.org/fts5.html) e
[API do Ollama](https://docs.ollama.com/api/chat).

## Testes

```bash
python3 -m unittest discover -s tests -v
```

Os testes usam documentos sintéticos temporários e não alimentam a base real.

A avaliação do conjunto real está descrita em [avaliação inicial](avaliacao-inicial.md).
