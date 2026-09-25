"""Verificação e cópia consistente da base, sem sobrescrever arquivos existentes."""
import argparse
from contextlib import closing
from pathlib import Path
import sqlite3
from knowledge import DATABASE


def inspect_database(path=DATABASE):
    path = Path(path).resolve()
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as conn:
        if conn.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('Falha na integridade SQLite.')
        count = conn.execute('SELECT count(*) FROM chunks').fetchone()[0]
        conn.execute("SELECT count(*) FROM chunks WHERE chunks MATCH 'saude'").fetchone()
        if not count:
            raise ValueError('A base documental está vazia.')
        return {'ready': True, 'chunks': count}


def copy_database(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    inspect_database(source)
    # Criação exclusiva: nem backup nem recuperação substituem a base atual.
    with destination.open('xb'):
        pass
    try:
        destination.chmod(0o600)
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as src:
            with closing(sqlite3.connect(destination)) as dst:
                src.backup(dst)
        return inspect_database(destination)
    except Exception:
        destination.unlink()
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'backup'])
    parser.add_argument('--source', type=Path, default=DATABASE)
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    if args.action == 'backup' and args.destination is None:
        parser.error('backup exige --destination (arquivo novo em diretório existente).')
    try:
        result = (inspect_database(args.source) if args.action == 'check' else
                  copy_database(args.source, args.destination))
    except (OSError, sqlite3.Error, ValueError) as exc:
        parser.exit(1, f'Operação não concluída: {exc}\n')
    print(f"Base íntegra: {result['chunks']} trechos.")
