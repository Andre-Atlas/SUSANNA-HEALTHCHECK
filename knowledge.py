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


def retrieve(question, database=DATABASE):
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
