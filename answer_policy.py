"""Regras determinísticas de referências e do parecer de fidelidade por IA."""
import json
import re

NO_EVIDENCE = (
    'Não encontrei evidências suficientes na base local para responder a esta pergunta. '
    'Isso não significa que a alegação seja verdadeira ou falsa. '
    'Você pode reformular a pergunta com o tema específico ou consultar a fonte original. '
    'Não faço diagnóstico nem prescrição.'
)
INVALID_ANSWER = (
    'Encontrei trechos na base, mas não consegui produzir uma resposta que atendesse '
    'às verificações de referências e apoio documental. Consulte os trechos e as fontes abaixo. '
    'Não é possível concluir, apenas com esta tentativa, se a alegação é verdadeira ou falsa.'
)


def is_abstention(content):
    return isinstance(content, str) and bool(re.fullmatch(
        r'SEM_EVIDENCIA(?:\s*\[[0-9]+\])?[.!]?', content.strip(), re.IGNORECASE))


def normalize_references(content):
    """Ajusta apenas espaços e agrupamento numérico; nunca inventa IDs."""
    if not isinstance(content, str):
        return content
    return re.sub(r'\[\s*([1-9][0-9]*(?:\s*[,;]\s*[1-9][0-9]*)*)\s*\]',
                  lambda match: ''.join(f'[{part.strip()}]' for part in
                                       re.split(r'[,;]', match[1])), content).strip()


def answer_paragraphs(content):
    return [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]


def grounding_errors(raw, content, sources):
    """O parecer deve cobrir todo parágrafo e trazer evidência literal de cada ID.

    A existência da evidência é verificada aqui; o julgamento de suporte é da IA.
    """
    try:
        verdict = json.loads(raw)
        paragraphs = answer_paragraphs(content)
        if not isinstance(verdict, dict) or type(verdict.get('answers_question')) is not bool or type(verdict.get('conflicting_sources')) is not bool:
            return ['invalid_verification']
        checks = verdict.get('paragraphs')
        if not isinstance(checks, list) or len(checks) != len(paragraphs):
            return ['invalid_verification']
        errors = []
        if not verdict['answers_question']:
            errors.append('insufficient_support')
        if verdict['conflicting_sources']:
            errors.append('conflicting_sources')
        for index, (paragraph, check) in enumerate(zip(paragraphs, checks), 1):
            if not isinstance(check, dict) or type(check.get('id')) is not int or check['id'] != index or type(check.get('supported')) is not bool:
                return ['invalid_verification']
            if not check['supported']:
                errors.append('unsupported_claim')
                continue
            evidence = check.get('evidence')
            if not isinstance(evidence, list) or not evidence:
                return ['invalid_verification']
            cited = {int(ref) for ref in re.findall(r'\[([0-9]+)\]', paragraph)}
            verified = set()
            for item in evidence:
                if not isinstance(item, dict):
                    return ['invalid_verification']
                source_id, quote = item.get('source_id'), item.get('quote')
                if type(source_id) is not int or source_id not in cited or not 1 <= source_id <= len(sources):
                    return ['invalid_evidence_source']
                if not isinstance(quote, str) or len(quote.strip()) < 12 or quote not in sources[source_id - 1]['text']:
                    return ['unverified_evidence_quote']
                verified.add(source_id)
            if verified != cited:
                errors.append('unchecked_citation')
        return sorted(set(errors))
    except (ValueError, TypeError, KeyError):
        return ['invalid_verification']


def reference_errors(content, sources):
    if not isinstance(content, str) or not content.strip():
        return ['empty_answer']
    errors = []
    # URLs ficam exclusivamente nos registros fornecidos pelo servidor.
    if re.search(r'(?i)\b(?:[a-z][a-z0-9+.-]*://|www\.)|\[[^\]]*\]\s*\(|\b(?:[a-z0-9-]+\.)+[a-z]{2,63}\b', content):
        errors.append('generated_link')
    citations = re.findall(r'\[([^\]]*)\]', content)
    if not citations:
        errors.append('missing_citation')
    if any(not re.fullmatch(r'[1-9][0-9]*', ref) or
           len(ref) > 3 or not 1 <= int(ref) <= len(sources) for ref in citations):
        errors.append('invalid_citation')
    # Toda unidade de texto emitida pelo modelo precisa terminar com referência.
    # Isso verifica formato e rastreabilidade, não que a evidência sustente o texto.
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
    if any(not re.search(r'\[[1-9][0-9]*\][.!?]?$', p) for p in paragraphs):
        errors.append('uncited_paragraph')
    return errors
