"""Avaliação reproduzível de recuperação; --llm registra respostas para revisão."""
import argparse
import hashlib
import json
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from knowledge import import_document, retrieve
from server import MODEL, build_prompt, generate_answer

ROOT = Path(__file__).resolve().parent


def evaluate(use_llm=False):
    cases = json.loads((ROOT / 'evaluation/questions.json').read_text(encoding='utf-8'))
    files = sorted((ROOT / 'sources').glob('*.json'))
    urls = {path.name: json.loads(path.read_text(encoding='utf-8'))['url'] for path in files}
    results = []
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / 'evaluation.sqlite3'
        for path in files:
            import_document(path, database)
        for case in cases:
            sources = retrieve(case['question'], database)
            expected = urls.get(case['expected_source'])
            retrieved = [source['url'] for source in sources]
            prompt, supplied = build_prompt([{'role': 'user', 'content': case['question']}], sources)
            row = {**case, 'retrieved_urls': retrieved,
                   'retrieval_pass': expected in retrieved if expected else not retrieved,
                   'expected_source_sent': expected in [s['url'] for s in supplied] if expected else None,
                   'sources_sent': supplied}
            if use_llm:
                start = time.monotonic()
                try:
                    result = generate_answer(prompt, supplied)
                    answer = result['message']
                    if not isinstance(answer, str) or not answer.strip():
                        raise ValueError('Resposta vazia ou inválida')
                    row['answer'] = answer
                    row['answer_status'] = result['answer_status']
                    row['llm_called'] = result['llm_called']
                    row['validation_errors'] = result['validation_errors']
                    refs = [int(ref) for ref in re.findall(r'\[(\d+)\]', answer)]
                    row['citation_ids_in_range'] = all(1 <= ref <= len(supplied) for ref in refs)
                    row['has_citation'] = bool(refs)
                    row['review_note'] = 'Revisão automática por IA quando grounding_checked; não é garantia factual.'
                    row['done_reason'] = result.get('done_reason')
                except Exception as exc:
                    row['error'] = f'{type(exc).__name__}: {exc}'
                row['seconds'] = round(time.monotonic() - start, 2)
            results.append(row)
            print(f"{case['id']}: recuperação {'OK' if row['retrieval_pass'] else 'FALHOU'}", flush=True)
    return {'created_at': datetime.now(timezone.utc).isoformat(), 'model': MODEL if use_llm else None,
            'corpus_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            'code_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ('server.py', 'knowledge.py', 'answer_policy.py', 'evaluate.py')},
            'retrieval_passed': sum(r['retrieval_pass'] for r in results), 'total': len(results),
            'note': 'Conjunto pequeno de desenvolvimento; não é validação clínica nem teste independente.',
            'results': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--llm', action='store_true', help='Executa também inferência local para cada pergunta')
    parser.add_argument('--output', type=Path, default=ROOT / 'evaluation/latest.json')
    args = parser.parse_args()
    report = evaluate(args.llm)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Recuperação: {report['retrieval_passed']}/{report['total']}. Relatório: {args.output}")
    raise SystemExit(1 if report['retrieval_passed'] != report['total'] or any('error' in r for r in report['results']) else 0)
