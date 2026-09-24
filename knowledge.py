"""Base documental local. Importação explícita de textos revisados pela equipe."""
import argparse
import json
import re
import sqlite3
import unicodedata
from contextlib import closing
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

DATABASE = Path(__file__).resolve().parent / 'data' / 'knowledge.sqlite3'
STOPWORDS = set('a o as os um uma de da do das dos em no na nos nas e ou que se para por com como qual quais onde quando porque sobre isso isto esse essa ser sao foi tem pode nao mais uma'.split())


def search_terms(text):
    normalized = ''.join(c for c in unicodedata.normalize('NFD', text.lower())
                         if unicodedata.category(c) != 'Mn')
    return list(dict.fromkeys(word for word in re.findall(r'\w+', normalized)
                             if len(word) > 2 and word not in STOPWORDS))


def initialize(connection):
    connection.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
        title, text, url UNINDEXED, reviewed_at UNINDEXED,
        tokenize='unicode61 remove_diacritics 2')''')


def import_document(path, database=DATABASE):
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(document, dict):
        raise ValueError('O documento deve ser um objeto JSON.')
    for field in ('title', 'text', 'url', 'reviewed_at'):
        if not isinstance(document.get(field), str) or not document[field].strip():
            raise ValueError(f'Campo obrigatório: {field}')
    url = urlsplit(document['url'])
    if url.scheme != 'https' or not url.hostname or url.username or url.password:
        raise ValueError('A fonte deve ter uma URL HTTPS sem credenciais.')
    if len(document['title']) > 300 or len(document['url']) > 2000:
        raise ValueError('Título ou URL muito longo.')
    reviewed = date.fromisoformat(document['reviewed_at'])
    if reviewed > date.today():
        raise ValueError('A data de revisão não pode estar no futuro.')
    # Blocos limitados, sem cortar palavras. Não executa nem baixa o conteúdo da URL.
    words = document['text'].split()
    if any(len(word) > 1200 for word in words):
        raise ValueError('Texto contém uma palavra ou sequência excessivamente longa.')
    chunks, current = [], ''
    for word in words:
        if len(current) + len(word) + 1 > 1200:
            chunks.append(current)
            current = ''
        current = f'{current} {word}'.strip()
    if current:
        chunks.append(current)
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database)) as connection, connection:
        initialize(connection)
        connection.execute('DELETE FROM chunks WHERE url = ?', (document['url'],))
        connection.executemany(
            'INSERT INTO chunks(title, text, url, reviewed_at) VALUES (?, ?, ?, ?)',
            [(document['title'], chunk, document['url'], document['reviewed_at']) for chunk in chunks])
    return len(chunks)


def remove_document(url, database=DATABASE):
    """Retira somente os trechos da URL exata; não cria uma base ausente."""
    database = Path(database)
    if not database.exists():
        return 0
    with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=rw', uri=True)) as connection, connection:
        cursor = connection.execute('DELETE FROM chunks WHERE url = ?', (url,))
        return cursor.rowcount


def retrieve_lexical(question, database=DATABASE):
    """Busca lexical na pergunta atual; resultados não significam confirmação factual."""
    if not Path(database).exists():
        return []
    terms = search_terms(question)[:32]
    if not terms:
        return []
    expression = ' OR '.join(f'"{term}"' for term in terms)
    with closing(sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute('''SELECT title, text, url, reviewed_at FROM chunks
            WHERE chunks MATCH ? ORDER BY bm25(chunks), rowid LIMIT 30''', (expression,)).fetchall()
    # Evita aceitar só uma coincidência isolada em uma pergunta com vários termos.
    # Heurística lexical, não confiança factual; pode reduzir a recuperação por sinônimos.
    required = min(2, len(terms))
    matches = [dict(row) for row in rows
               if len(set(terms) & set(search_terms(row['title'] + ' ' + row['text']))) >= required]
    return matches[:3]


# Alternativas de busca, não equivalências clínicas. Cada grupo conta uma vez.
TERM_GROUPS = [
    'vacina vacinas vacinacao imunizacao imunizante imunizantes',
    'seguranca segura seguras seguro seguros',
    'reacao reacoes efeito efeitos',
    'passageira passageiras temporaria temporarias',
    'antibiotico antibioticos',
    'antimicrobiano antimicrobianos',
    'virus viral virais',
    'bacteria bacterias bacteriana bacterianas',
    'prevencao prevenir evitar',
    'transmissao transmitida transmite transmitido pega pegar',
    'boato boatos desinformacao fake news',
    'identificar reconhecer detectar',
    'conferir confira verificar checar examine',
    'noticia noticias informacao informacoes',
    'compartilhar dividir',
    'sobra sobras',
    'resfriado resfriados',
]
ALIASES = {term: frozenset(group.split()) for group in TERM_GROUPS for term in group.split()}
INFORMAL = set('posso pra pro ta to vc voces gente saber queria quero sera mesmo nesse nessa caso entao disso dessas desses elas eles'.split())


def one_edit(left, right):
    """Uma inserção, exclusão, substituição ou transposição adjacente."""
    if abs(len(left) - len(right)) > 1:
        return False
    if len(left) == len(right):
        changed = [i for i, (a, b) in enumerate(zip(left, right)) if a != b]
        return len(changed) == 1 or (len(changed) == 2 and changed[1] == changed[0] + 1
            and left[changed[0]] == right[changed[1]] and left[changed[1]] == right[changed[0]])
    short, long = sorted((left, right), key=len)
    index = next((i for i in range(len(short)) if short[i] != long[i]), len(short))
    return short[index:] == long[index + 1:]


def query_groups(question, vocabulary):
    groups = []
    for term in search_terms(question)[:32]:
        if term in INFORMAL:
            continue
        if term not in vocabulary and term not in ALIASES and 5 <= len(term) <= 40:
            candidates = sorted(word for word in vocabulary | ALIASES.keys()
                                if one_edit(term, word))
            # Ambiguidade: não escolher silenciosamente entre duas correções.
            if len(candidates) == 1:
                term = candidates[0]
        group = ALIASES.get(term, frozenset([term]))
        if group not in groups:
            groups.append(group)
    return groups


def retrieve(question, database=DATABASE, *, rerank=False):
    """FTS com expansão controlada e seleção por conceitos distintos."""
    if not Path(database).exists():
        return []
    with closing(sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        # Vocabulário lido do índice atual; novas importações não exigem reinício.
        connection.execute("CREATE VIRTUAL TABLE temp.vocabulary USING fts5vocab(main, chunks, row)")
        vocabulary = {row[0] for row in connection.execute('SELECT term FROM temp.vocabulary')}
        groups = query_groups(question, vocabulary)
        if not groups:
            return []
        terms = sorted(set().union(*groups))
        expression = ' OR '.join(f'"{term}"' for term in terms)
        rows = connection.execute('''SELECT title, text, url, reviewed_at FROM chunks
            WHERE chunks MATCH ? ORDER BY bm25(chunks), rowid LIMIT 30''', (expression,)).fetchall()
    required = min(2, len(groups))
    matches = []
    for index, row in enumerate(rows):
        words = set(search_terms(row['title'] + ' ' + row['text']))
        coverage = sum(bool(group & words) for group in groups)
        if coverage >= required:
            matches.append((coverage, index, dict(row)))
    if rerank:
        matches.sort(key=lambda item: (-item[0], item[1]))
    return [item[2] for item in matches[:3]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', nargs='?', help='Arquivo JSON revisado pela equipe')
    parser.add_argument('--remove-url', help='Retira os trechos da URL exata da base local')
    args = parser.parse_args()
    if bool(args.document) == bool(args.remove_url):
        parser.error('Informe um documento ou --remove-url, exclusivamente.')
    try:
        count = remove_document(args.remove_url) if args.remove_url else import_document(args.document)
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f'Não foi possível atualizar a base: {exc}\n')
    action = 'retirados' if args.remove_url else 'importados'
    print(f'{count} trechos {action}. Base: {DATABASE}')
