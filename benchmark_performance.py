"""Mede o pipeline real com Ollama, banco temporário e memória amostrada."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import threading
import time

import knowledge
import server
from jobs import JobQueue

ROOT = Path(__file__).resolve().parent


def sysctl(name):
    try:
        return subprocess.check_output(['sysctl', '-n', name], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def memory_sample():
    """RSS de processos; não equivale ao uso total de RAM/GPU do modelo."""
    own, ollama = None, 0
    try:
        rows = subprocess.check_output(['ps', '-axo', 'pid=,rss=,comm='], text=True).splitlines()
        for row in rows:
            fields = row.strip().split(None, 2)
            if len(fields) != 3:
                continue
            pid, kib, command = fields
            if int(pid) == os.getpid():
                own = round(int(kib) / 1024, 2)
            if 'ollama' in Path(command).name.lower():
                ollama += int(kib)
        return {'python_rss_mib': own, 'ollama_processes_rss_mib': round(ollama / 1024, 2)}
    except (OSError, subprocess.CalledProcessError):
        return {'python_rss_mib': None, 'ollama_processes_rss_mib': None}


def benchmark():
    initial = server.ollama('/api/ps', timeout=5)
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
        'hardware': {'platform': platform.platform(), 'cpu': sysctl('machdep.cpu.brand_string'),
                     'ram_bytes': sysctl('hw.memsize'), 'python': platform.python_version()},
        'ollama_version': server.ollama('/api/version', timeout=5), 'model': server.MODEL,
        'initial_models': initial, 'runs': [],
        'method': 'Pipeline real em um worker; banco temporário com fontes versionadas. '
                  'Tempos excluem HTTP do navegador, polling e apresentação progressiva. '
                  'RSS amostrado a cada 0,5 s; pode perder picos. RSS de processos Ollama '
                  'pode contar páginas compartilhadas. Alocação do modelo não deve ser somada ao RSS.',
        'sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in [ROOT / name for name in ('server.py', 'jobs.py', 'ollama_transport.py',
                       'knowledge.py', 'conversation.py', 'answer_policy.py', 'benchmark_performance.py')]
                   + sorted((ROOT / 'sources').glob('*.json'))}}
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / 'knowledge.sqlite3'
        for path in sorted((ROOT / 'sources').glob('*.json')):
            knowledge.import_document(path, database)
        original = server.retrieve
        server.retrieve = lambda query: knowledge.retrieve(query, database)
        queue = JobQueue(server.process_messages, lease=30)
        messages = [{'role': 'user', 'content': 'Como a segurança das vacinas é avaliada?'}]
        try:
            for label, cancel_stage in [('first', None), ('repeat', None),
                                         ('cancel_generation', 'generation'), ('cancel_review', 'review')]:
                samples = []
                stop = threading.Event()
                def sample():
                    while not stop.is_set():
                        samples.append(memory_sample())
                        stop.wait(.5)
                sampler = threading.Thread(target=sample, daemon=True)
                sampler.start()
                job = queue.submit(messages)
                requested = None
                streaming_since = None
                while not job.finished.wait(.05):
                    queue.get(job.id)
                    with job.lock:
                        ready = (job.stage == cancel_stage and job.upstream is not None
                                 and cancel_stage + '_first_token' in job.timings) if cancel_stage else False
                    if ready and streaming_since is None:
                        streaming_since = time.monotonic()
                    ready = ready and time.monotonic() - streaming_since >= .25
                    if ready and requested is None:
                        requested = time.monotonic()
                        queue.cancel(job.id)
                stop.set()
                sampler.join(2)
                snapshot = queue.snapshot(job)
                result = snapshot.get('result', {})
                run = {'label': label, 'state': job.state, 'timings_seconds': job.timings,
                       'answer_status': result.get('answer_status'),
                       'validation_errors': result.get('validation_errors'), 'error': job.error,
                       'cancel_requested': requested is not None,
                       'cancel_to_worker_exit_seconds': round(job.ended - requested, 4) if requested else None,
                       'memory_samples': len(samples),
                       'memory_peak_mib': {key: max((item[key] for item in samples if item[key] is not None), default=None)
                                           for key in ('python_rss_mib', 'ollama_processes_rss_mib')},
                       'loaded_models_after': server.ollama('/api/ps', timeout=5)}
                report['runs'].append(run)
                print(json.dumps({key: run[key] for key in ('label', 'state', 'timings_seconds',
                    'answer_status', 'cancel_to_worker_exit_seconds', 'memory_peak_mib')}, ensure_ascii=False), flush=True)
        finally:
            queue.close()
            server.retrieve = original
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/performance.json')
    args = parser.parse_args()
    report = benchmark()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Relatório: {args.output}', flush=True)
    raise SystemExit(0 if all(run['state'] == ('cancelled' if run['label'].startswith('cancel_') else 'done')
                             for run in report['runs']) else 1)
