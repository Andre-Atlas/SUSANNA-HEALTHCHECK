"""Resume relatórios de avaliação em uma tabela sem copiar conteúdo conversacional."""
import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / 'evaluation'
DEFAULT_OUTPUT = ROOT / 'evaluation' / 'analytics-summary.csv'
TRACKING_DIR = ROOT / '.mlflow'


def numeric(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    if value != value:  # pandas pode representar ausência como NaN depois da leitura.
        return None
    return value


def summarize_report(path):
    """Retorna somente campos de resumo explicitamente permitidos."""
    try:
        report = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(report, dict):
        return None

    row = {
        'report': path.name,
        'created_at': report.get('created_at'),
        'model': report.get('model') if isinstance(report.get('model'), str) else None,
        'ollama_version': report.get('ollama_version'),
    }

    summary = report.get('summary_seconds')
    if isinstance(summary, dict):
        row['kind'] = 'performance'
        for stage, values in summary.items():
            if not isinstance(values, dict):
                continue
            for statistic in ('count', 'p50', 'p95'):
                value = numeric(values.get(statistic))
                if value is not None:
                    row[f'{stage}_{statistic}'] = value
        row['total_cases'] = numeric(report.get('case_count'))
        return row

    total = numeric(report.get('total'))
    if total is None or total <= 0:
        return None
    for source_key, kind in (
        ('automatic_passed', 'acceptance'),
        ('passed', 'reviewer'),
        ('retrieval_passed', 'retrieval'),
    ):
        passed = numeric(report.get(source_key))
        if passed is not None:
            row.update(kind=kind, passed=passed, total=total,
                       pass_rate=round(passed / total, 6))
            return row
    return None


def collect_reports(input_dir):
    rows = [row for path in sorted(input_dir.glob('*.json'))
            if (row := summarize_report(path)) is not None]
    if not rows:
        raise ValueError(f'Nenhum relatório de avaliação compatível em {input_dir}.')
    frame = pd.DataFrame(rows)
    return frame.sort_values(['kind', 'created_at', 'report'], na_position='last').reset_index(drop=True)


def local_tracking_uri():
    TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    database = (TRACKING_DIR / 'mlflow.db').resolve().as_posix()
    return f'sqlite:///{database}'


def log_aggregates(frame, experiment):
    """Registra apenas métricas agregadas e nomes de relatórios, nunca seus conteúdos."""
    import mlflow

    mlflow.set_tracking_uri(local_tracking_uri())
    mlflow.set_experiment(experiment)
    for row in frame.to_dict(orient='records'):
        safe_name = Path(row['report']).stem[:200]
        with mlflow.start_run(run_name=safe_name):
            mlflow.set_tag('report_kind', row['kind'])
            mlflow.set_tag('source_report', row['report'])
            mlflow.set_tag('privacy', 'aggregate metrics only; no prompts, questions, answers, or sources')
            if row.get('created_at'):
                mlflow.set_tag('source_created_at', str(row['created_at']))
            if row.get('model'):
                mlflow.log_param('model', row['model'])
            if row.get('ollama_version'):
                version = row['ollama_version']
                mlflow.log_param('ollama_version', version if isinstance(version, str) else json.dumps(version))
            for key in ('passed', 'total', 'pass_rate', 'total_cases'):
                value = numeric(row.get(key))
                if value is not None:
                    mlflow.log_metric(key, value)
            for key, value in row.items():
                if key.endswith(('_p50', '_p95', '_count')) and numeric(value) is not None:
                    mlflow.log_metric(key, value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT,
                        help='Pasta com relatórios JSON agregados (padrão: evaluation/)')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT,
                        help='CSV com uma linha agregada por relatório')
    parser.add_argument('--mlflow', action='store_true',
                        help='Registra métricas agregadas no MLflow local do projeto')
    parser.add_argument('--experiment', default='susanna-evaluation-summary')
    args = parser.parse_args()

    frame = collect_reports(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False, encoding='utf-8')
    if args.mlflow:
        log_aggregates(frame, args.experiment)

    print(f'Relatórios resumidos: {len(frame)}')
    print(frame.groupby('kind').size().to_string())
    print(f'CSV agregado: {args.output}')
    if args.mlflow:
        print(f'Métricas agregadas registradas no experimento MLflow: {args.experiment}')


if __name__ == '__main__':
    main()
