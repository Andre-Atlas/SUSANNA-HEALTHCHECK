"""Mede a latência do pipeline local sem registrar perguntas ou respostas."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile
import threading
import time

import knowledge
import server
from jobs import JobQueue

ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT / 'evaluation/search-cases.json'
TIMING_KEYS = ('queue', 'retrieval', 'generation', 'review', 'total')


def sysctl(name):
    try:
        return subprocess.check_output(['sysctl', '-n', name], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def percentile(values, percentile):
    """Percentil inclusivo por interpolação linear (método Hyndman-Fan 7)."""
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    fraction = position - lower
    return round(values[lower] * (1 - fraction) + values[upper] * fraction, 4)


def load_cases(path):
    cases = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(cases, list) or not cases:
        raise ValueError('O arquivo de casos deve conter uma lista não vazia.')
    selected = []
    for index, case in enumerate(cases, 1):
        if not isinstance(case, dict) or not isinstance(case.get('question'), str):
            continue
        # Conversas sintéticas de avaliação só são aceitas se contiverem mensagens
        # alternadas user/assistant; o conteúdo é usado em memória e nunca copiado ao relatório.
        history = case.get('history', [])
        if not isinstance(history, list) or any(not isinstance(item, str) for item in history):
            continue
        messages = []
        for previous in history:
            messages.extend([{'role': 'user', 'content': previous},
                             {'role': 'assistant', 'content': 'Entendi.'}])
        messages.append({'role': 'user', 'content': case['question']})
        selected.append({'case_id': f'case_{index:03d}', 'messages': messages})
    if not selected:
        raise ValueError('Nenhum caso com pergunta válida foi encontrado.')
    return selected


def metrics_report(samples):
    summary = {}
    for key in TIMING_KEYS:
        values = [sample['timings_seconds'][key] for sample in samples
                  if sample.get('state') == 'done' and key in sample.get('timings_seconds', {})
                  and (key in ('queue', 'retrieval', 'total') or sample.get('llm_called'))]
        summary[key] = {'count': len(values), 'p50': percentile(values, 50),
                        'p95': percentile(values, 95)}
    return summary


def maybe_log_mlflow(report, experiment):
    """Registra somente metadados técnicos e agregados; nenhum texto conversacional."""
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError('MLflow não está instalado. Instale-o para usar --mlflow.') from exc
    mlflow.set_experiment(experiment)
    with mlflow.start_run(run_name=report['run_id']):
        mlflow.log_params({
            'model': report['model'], 'ollama_version': report['ollama_version'],
            'platform': report['hardware']['platform'], 'cpu': report['hardware']['cpu'] or 'unknown',
            'python': report['hardware']['python'], 'warmup_runs': report['warmup_runs'],
            'repetitions': report['repetitions'], 'case_count': report['case_count'],
            'case_set_sha256': report['case_set_sha256'],
        })
        metrics = {}
        for stage_name, values in report['summary_seconds'].items():
            if values['p50'] is not None:
                metrics[f'{stage_name}_p50_seconds'] = values['p50']
            if values['p95'] is not None:
                metrics[f'{stage_name}_p95_seconds'] = values['p95']
            metrics[f'{stage_name}_sample_count'] = values['count']
        mlflow.log_metrics(metrics)
        mlflow.set_tag('privacy', 'no prompts, questions, answers, or retrieved sources logged')
        mlflow.set_tag('benchmark_run_id', report['run_id'])


def benchmark(case_path=DEFAULT_CASES, warmup_runs=1, repetitions=3):
    cases = load_cases(case_path)
    initial = server.ollama('/api/ps', timeout=5)
    initial_loaded = any(item.get('name') == server.MODEL for item in initial.get('models', []))
    source_files = sorted((ROOT / 'sources').glob('*.json'))
    code_files = [ROOT / name for name in (
        'server.py', 'jobs.py', 'ollama_transport.py', 'knowledge.py',
        'conversation.py', 'answer_policy.py', 'benchmark_performance.py')]
    report = {
        'created_at': datetime.now(timezone.utc).isoformat(),
        'run_id': datetime.now(timezone.utc).strftime('latency-%Y%m%dT%H%M%SZ'),
        'hardware': {'platform': platform.platform(), 'cpu': sysctl('machdep.cpu.brand_string'),
                     'ram_bytes': sysctl('hw.memsize'), 'python': platform.python_version()},
        'ollama_version': server.ollama('/api/version', timeout=5).get('version', 'unknown'),
        'model': server.MODEL,
        'model_loaded_before_benchmark': initial_loaded,
        'warmup_runs': warmup_runs, 'repetitions': repetitions,
        'case_count': len(cases), 'case_set_sha256': hashlib.sha256(case_path.read_bytes()).hexdigest(),
        'samples': [], 'summary_seconds': {},
        'method': ('Synthetic representative cases from the versioned search suite; warmups are excluded. '
                   'The model is not unloaded. Queue, retrieval, generation, review and total are reported. '
                   'Conversation text, prompts, answers, sources and job IDs are not stored.'),
        'sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in code_files + source_files},
    }

    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / 'knowledge.sqlite3'
        for path in source_files:
            knowledge.import_document(path, database)
        original_retrieve = server.retrieve
        server.retrieve = lambda query: knowledge.retrieve(query, database)
        queue = JobQueue(server.process_messages, concurrency=1, capacity=0,
                         lease=600, run_timeout=600)
        try:
            # Aquecimento usa o primeiro caso e nunca entra nas distribuições.
            for warmup_index in range(warmup_runs):
                job = queue.submit(cases[warmup_index % len(cases)]['messages'])
                if not job.finished.wait(600):
                    queue.cancel(job.id, 'benchmark_timeout')
                    raise TimeoutError('O aquecimento excedeu 600 segundos.')
                if job.state != 'done':
                    raise RuntimeError('Falha durante aquecimento do benchmark.')

            for repetition in range(1, repetitions + 1):
                for case in cases:
                    job = queue.submit(case['messages'])
                    if not job.finished.wait(600):
                        queue.cancel(job.id, 'benchmark_timeout')
                        raise TimeoutError('Uma execução excedeu 600 segundos.')
                    snapshot = queue.snapshot(job)
                    # Somente métricas e estado são preservados. O resultado com
                    # resposta e fontes permanece transitório na memória do job.
                    sample = {'case_id': case['case_id'], 'repetition': repetition,
                              'state': job.state, 'timings_seconds': dict(job.timings),
                              'answer_status': snapshot.get('result', {}).get('answer_status'),
                              'llm_called': snapshot.get('result', {}).get('llm_called', False)}
                    report['samples'].append(sample)
                    print(json.dumps(sample, ensure_ascii=False), flush=True)
            report['summary_seconds'] = metrics_report(report['samples'])
        finally:
            queue.close()
            server.retrieve = original_retrieve
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=DEFAULT_CASES,
                        help='JSON sintético; conteúdo nunca é copiado para o relatório')
    parser.add_argument('--warmup', type=int, default=1, help='Execuções descartadas para aquecimento')
    parser.add_argument('--repetitions', type=int, default=3, help='Repetições por caso após aquecimento')
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/performance.json')
    parser.add_argument('--mlflow', action='store_true', help='Registra agregados técnicos em MLflow local')
    parser.add_argument('--mlflow-experiment', default='saude-gov-br-latency')
    args = parser.parse_args()
    if args.warmup < 0 or args.repetitions < 1:
        parser.error('--warmup deve ser >= 0 e --repetitions deve ser >= 1.')
    try:
        report = benchmark(args.cases, args.warmup, args.repetitions)
        if args.mlflow:
            maybe_log_mlflow(report, args.mlflow_experiment)
    except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
        parser.exit(1, f'Benchmark falhou: {exc}\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary_seconds'], ensure_ascii=False, indent=2), flush=True)
    print(f"Relatório: {args.output}", flush=True)
