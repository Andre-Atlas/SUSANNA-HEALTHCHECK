"""Importa o conjunto versionado e remove fontes substituídas explicitamente."""
import json
from pathlib import Path
from knowledge import DATABASE, import_document, remove_document


def seed_knowledge(source_dir=None, database=DATABASE):
    source_dir = Path(source_dir) if source_dir else Path(__file__).resolve().parent / 'sources'
    for path in sorted(source_dir.glob('*.json')):
        document = json.loads(path.read_text(encoding='utf-8'))
        count = import_document(path, database)
        replaced_url = document.get('replaces_url')
        removed = remove_document(replaced_url, database) if replaced_url else 0
        suffix = f'; {removed} trecho(s) substituido(s)' if removed else ''
        print(f'{path.name}: {count} trecho(s) importado(s){suffix}.')


if __name__ == '__main__':
    seed_knowledge()
    print('Conjunto experimental: sinteses por IA; revisao documental por IA concluida.')
