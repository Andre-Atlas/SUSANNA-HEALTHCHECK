"""Compara busca original, expansão e expansão com seleção, sem chamar a LLM."""
import json
import hashlib
import tempfile
import time
from pathlib import Path

from conversation import resolve_question
from knowledge import import_document, retrieve, retrieve_lexical

ROOT = Path(__file__).resolve().parent


def case_messages(case):
    messages = []
    for question in case.get('history', []):
        messages.extend([{'role': 'user', 'content': question},
                         {'role': 'assistant', 'content': 'Resposta anterior não usada na busca.'}])
    return messages + [{'role': 'user', 'content': case['question']}]


def evaluate():
    cases = json.loads((ROOT / 'evaluation/questions.json').read_text())
    cases += json.loads((ROOT / 'evaluation/search-cases.json').read_text())
    urls = {}
    results = []
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / 'knowledge.sqlite3'
        for path in sorted((ROOT / 'sources').glob('*.json')):
            urls[path.name] = json.loads(path.read_text())['url']
            import_document(path, database)
        for case in cases:
            query, _, clarify = resolve_question(case_messages(case))
            variants = {}
            for name in ('original', 'expanded', 'contextual', 'selected'):
                start = time.perf_counter()
                if name == 'original':
                    sources = retrieve_lexical(case['question'], database)
                elif name == 'expanded':
                    sources = retrieve(case['question'], database)
                else:
                    sources = [] if clarify else retrieve(query, database, rerank=name == 'selected')
                found = [source['url'] for source in sources]
                expected = urls.get(case['expected_source'])
                passed = expected in found if expected else not found
                variants[name] = {'passed': passed, 'urls': found,
                    'expected_first': bool(expected and found and found[0] == expected),
                    'milliseconds': round((time.perf_counter() - start) * 1000, 3)}
            results.append({'id': case['id'], 'category': case.get('category', 'original'),
                'question': case['question'], 'query': query, 'needs_clarification': clarify,
                'expected_source': case['expected_source'], 'variants': variants})
    summary = {}
    for name in ('original', 'expanded', 'contextual', 'selected'):
        summary[name] = {'passed': sum(row['variants'][name]['passed'] for row in results),
            'total': len(results),
            'expected_first': sum(row['variants'][name]['expected_first'] for row in results),
            'negative_false_positives': sum(bool(row['variants'][name]['urls']) for row in results
                                            if row['expected_source'] is None)}
    return {'note': 'Casos de desenvolvimento; avalia recuperação, não correção das respostas. '
                    'Contextual e selected usam continuidade. Tempos locais sem inferência.',
            'sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in [ROOT / 'knowledge.py', ROOT / 'conversation.py',
                                    ROOT / 'evaluate_search.py', ROOT / 'evaluation/questions.json',
                                    ROOT / 'evaluation/search-cases.json', *sorted((ROOT / 'sources').glob('*.json'))]},
            'summary': summary, 'results': results}


if __name__ == '__main__':
    report = evaluate()
    (ROOT / 'evaluation/search-comparison.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['summary']['contextual']['passed'] == report['summary']['contextual']['total'] else 1)
