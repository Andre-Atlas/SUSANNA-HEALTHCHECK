"""Continuidade limitada e determinística; respostas da IA não viram consulta."""
import json
import re
import unicodedata

CLARIFY = 'A qual assunto ou pergunta anterior você se refere? Escreva o tema para eu consultar a base local.'


def is_followup(text):
    normalized = ''.join(c for c in unicodedata.normalize('NFD', text.lower())
                         if unicodedata.category(c) != 'Mn')
    normalized = ' '.join(re.sub(r'[^\w\s]', '', normalized).split())
    return bool(re.fullmatch(
        r'(?:e\s+)?(?:nesse caso|neste caso|nessa situacao|isso|quanto a isso|'
        r'(?:as?\s+)?(?:reacoes|efeitos|prevencao|riscos)|como assim|pode explicar melhor)', normalized))


def resolve_question(messages):
    """Retorna consulta, mensagens para geração/revisão e pedido de esclarecimento.

    Só formas explicitamente reconhecidas herdam até três perguntas anteriores.
    O último assunto explícito é a âncora; jamais atravessa uma mudança de assunto.
    """
    current = messages[-1]['content']
    if not is_followup(current):
        return current, list(messages), False
    previous = [m['content'] for m in messages[:-1] if m['role'] == 'user'][-3:]
    context = []
    for text in reversed(previous):
        context.insert(0, text)
        if not is_followup(text):
            break
    if not context or all(is_followup(text) for text in context):
        return current, list(messages), True
    # Limite explícito: não cortar silenciosamente a pergunta que define o assunto.
    if sum(len(text) for text in context) + len(current) > 3000:
        return current, list(messages), True
    contextual = json.dumps({'perguntas_anteriores_do_usuario': context,
                             'pergunta_atual': current}, ensure_ascii=False)
    resolved = [*messages[:-1], {'role': 'user', 'content': contextual}]
    return ' '.join([*context, current]), resolved, False
