"""Validação de referências; não substitui avaliação semântica das afirmações."""
import re

NO_EVIDENCE = (
    'Não encontrei evidências suficientes na base local para responder a esta pergunta. '
    'Isso não significa que a alegação seja verdadeira ou falsa. '
    'Você pode reformular a pergunta com o tema específico ou consultar a fonte original. '
    'Não faço diagnóstico nem prescrição.'
)
INVALID_ANSWER = (
    'Encontrei trechos na base, mas não consegui produzir uma resposta que atendesse '
    'às regras de referências. Consulte os trechos e as fontes abaixo. '
    'Não é possível concluir, apenas com esta tentativa, se a alegação é verdadeira ou falsa.'
)


def is_abstention(content):
    return isinstance(content, str) and bool(re.fullmatch(
        r'SEM_EVIDENCIA(?:\s*\[[0-9]+\])?[.!]?', content.strip()))


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
