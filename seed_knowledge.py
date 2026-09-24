"""Importa o conjunto inicial versionado sem excluir outros documentos da base."""
from pathlib import Path
from knowledge import import_document


if __name__ == '__main__':
    for path in sorted((Path(__file__).resolve().parent / 'sources').glob('*.json')):
        count = import_document(path)
        print(f'{path.name}: {count} trecho(s) importado(s).')
    print('Conjunto experimental: sínteses por IA; revisão documental por IA concluída.')
