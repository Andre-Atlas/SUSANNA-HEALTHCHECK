"""Aceitação via HTTP real + Ollama; corpus/ataques isolados em banco temporário."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import time
from urllib.request import Request, urlopen

import knowledge
import server
from jobs import JobQueue

ROOT = Path(__file__).resolve().parent
SAFE_ABSTENTIONS = {'no_evidence', 'insufficient_evidence'}


def assess(case, result, expected_url=None):
    """Verifica contrato, exposição do caso e estado; não julga verdade semântica."""
    status = result.get('answer_status')
    checks = {'has_message': isinstance(result.get('message'), str) and bool(result['message'].strip()),
              'no_attack_marker': not any(marker in result.get('message', '') for marker in case.get('forbidden', []))}
    allowed = SAFE_ABSTENTIONS if case['expected'] == 'abstain' else {'grounding_checked'}
    if case['expected'] == 'answer_or_abstain':
        allowed = allowed | SAFE_ABSTENTIONS
    checks['expected_status'] = status in allowed
    if expected_url:
        checks['expected_source_supplied'] = expected_url in [s['url'] for s in result.get('sources', [])]
    if 'expected_sources_count' in case:
        checks['fixture_exercised'] = len(result.get('sources', [])) == case['expected_sources_count']
    # Falhas técnicas/formato não contam como reconhecimento semântico correto.
    checks['no_technical_rejection'] = status not in {'reference_rejected', 'grounding_rejected'}
    return checks


def request_json(base, path, method='GET', body=None):
    request = Request(base + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=10) as response:
        return json.load(response)


def run_turn(base, messages):
    job = request_json(base, '/api/jobs', 'POST', {'messages': messages})
    job_id = job['id']
    states = []
    start = time.monotonic()
    try:
        while True:
            state = (job['state'], job['stage'])
            if not states or states[-1] != list(state):
                states.append(list(state))
            if job['state'] != 'done' and 'result' in job:
                raise AssertionError('Resultado exposto antes de concluir a validação.')
            if job['state'] in {'done', 'error', 'cancelled'}:
                return {'state': job['state'], 'stages_observed': states, 'result': job.get('result'),
                        'error': job.get('error'), 'timings': job.get('timings'),
                        'http_roundtrip_seconds': round(time.monotonic() - start, 3)}
            if time.monotonic() - start > 490:
                raise TimeoutError('Tempo de avaliação excedido.')
            time.sleep(.2)
            job = request_json(base, '/api/jobs/' + job_id)
    finally:
        request_json(base, '/api/jobs/' + job_id, 'DELETE')


def human_packet(report, report_path):
    lines = ['# Revisão humana — pendente', '',
        'Duas pessoas devem preencher avaliações separadas. Este arquivo não contém aprovação humana.', '',
        f'Relatório: `{report_path.name}`. Data: {report["created_at"]}.',
        f'SHA-256 dos casos: `{report["hashes"]["evaluation/acceptance-cases.json"]}`.', '',
        'Rubrica e critérios: [protocolo](../docs/aceitacao.md).', '',
        'Para cada revisor: identificação, data, fidelidade, pertinência, citações, segurança, clareza, decisão e justificativa.',
        'Usar aprovado / reprovado / não aplicável. Toda divergência requer adjudicação documentada.', '']
    for row in report['results']:
        lines += [f'## {row["id"]} — {row["category"]}', '', f'Critério: {row["rubric"]}', '']
        for index, turn in enumerate(row.get('turns', []), 1):
            result = turn.get('result') or {}
            lines += [f'### Turno {index}', '', f'Pergunta: {turn["question"]}', '',
                      'Resposta exibida:', '', result.get('message', '(sem resposta; erro técnico)'), '']
            for number, source in enumerate(result.get('sources', []), 1):
                lines += [f'Fonte [{number}]: {source["title"]}', '', source['text'], '',
                          f'URL de referência: {source["url"]}', '']
        lines += ['Revisor A: **PENDENTE**', '', 'Revisor B: **PENDENTE**', '',
                  'Divergências e decisão final: **PENDENTE**', '']
    return '\n'.join(lines)


def evaluate(output):
    suite = json.loads((ROOT / 'evaluation/acceptance-cases.json').read_text())
    files = [ROOT / name for name in ('server.py', 'jobs.py', 'ollama_transport.py', 'knowledge.py',
        'conversation.py', 'answer_policy.py', 'evaluate_acceptance.py', 'evaluation/acceptance-cases.json')]
    files += sorted((ROOT / 'sources').glob('*.json'))
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'model': server.MODEL,
        'ollama_version': server.ollama('/api/version', timeout=5), 'provenance': suite['provenance'],
        'hashes': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        'human_review': 'pending', 'browser_review': 'pending', 'results': [],
        'note': 'Verificações automáticas de estado não certificam fidelidade ou segurança. '
                'Casos criados por IA após desenvolvimento; sem ajuste do produto para esta rodada.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / 'acceptance.sqlite3'
        original_retrieve = server.retrieve
        server.retrieve = lambda query: knowledge.retrieve(query, database)
        app = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        app.jobs = JobQueue(server.process_messages)
        thread = threading.Thread(target=app.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{app.server_port}'
        try:
            for case in suite['cases']:
                database.unlink(missing_ok=True)
                if 'fixture_texts' in case:
                    for index, text in enumerate(case['fixture_texts']):
                        fixture = Path(directory) / f'fixture-{index}.json'
                        fixture.write_text(json.dumps({'title': 'Documento sintético de demonstração',
                            'text': text, 'url': f'https://example.org/teste/{index}',
                            'reviewed_at': '2026-01-01'}))
                        knowledge.import_document(fixture, database)
                else:
                    for path in sorted((ROOT / 'sources').glob('*.json')):
                        knowledge.import_document(path, database)
                row = {key: case[key] for key in ('id', 'category', 'expected', 'rubric')}
                row['turns'] = []
                messages = []
                try:
                    for question in case['turns']:
                        messages.append({'role': 'user', 'content': question})
                        turn = run_turn(base, messages)
                        row['turns'].append({'question': question, **turn})
                        if turn['state'] != 'done':
                            raise ValueError('Fluxo HTTP não concluiu com resposta.')
                        messages.append({'role': 'assistant', 'content': turn['result']['message']})
                    expected_url = None
                    if case.get('expected_source'):
                        expected_url = json.loads((ROOT / 'sources' / case['expected_source']).read_text())['url']
                    row['checks'] = assess(case, row['turns'][-1]['result'], expected_url)
                    row['automatic_pass'] = all(row['checks'].values())
                except Exception as exc:
                    row['error'] = f'{type(exc).__name__}: {exc}'
                    row['automatic_pass'] = False
                report['results'].append(row)
                report['automatic_passed'] = sum(item['automatic_pass'] for item in report['results'])
                report['completed'] = len(report['results'])
                report['total'] = len(suite['cases'])
                output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
                output.with_suffix('.human.md').write_text(human_packet(report, output))
                print(f'{case["id"]}: {"OK automático" if row["automatic_pass"] else "REVISAR"}', flush=True)
        finally:
            app.jobs.close()
            app.shutdown()
            app.server_close()
            thread.join(2)
            server.retrieve = original_retrieve
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/acceptance.json')
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix('.human.md').exists():
        parser.error('Escolha --output novo para preservar o relatório e as revisões existentes.')
    report = evaluate(args.output)
    print(f'Critérios automáticos: {report["automatic_passed"]}/{report["total"]}. Revisão humana pendente.')
    raise SystemExit(0 if report['automatic_passed'] == report['total'] else 1)
