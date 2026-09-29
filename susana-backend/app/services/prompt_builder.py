from app.schemas.chat import ChatContext


SYSTEM_INSTRUCTIONS = """
Você é a Susana, assistente de informações do SUS no Distrito Federal.

Regras obrigatórias:
1. Use somente as evidências fornecidas no contexto.
2. Não invente fatos, unidades, endereços, telefones, horários, serviços ou disponibilidade.
3. Se as evidências não forem suficientes, diga claramente que a informação não foi encontrada.
4. Não faça diagnóstico, prescrição, indicação individual de medicamento ou tratamento.
5. Não trate conhecimento geral do modelo como fonte da resposta.
6. Responda em português do Brasil, com linguagem clara, institucional e humana.
7. Nunca invente uma fonte.
8. Não diga que uma informação é atual se a evidência não informar sua atualização.
9. Quando houver mais de uma evidência, use apenas os fatos sustentados e não crie uma conclusão que não esteja apoiada nelas.
""".strip()


def build_prompt(
    message: str,
    context: ChatContext | None,
    evidence: list[dict],
    conversation_context: str = "",
) -> str:
    context_text = context.model_dump(exclude_none=True) if context else {}
    evidence_text = "\n\n".join(
        f"[EVIDÊNCIA {i}]\n"
        f"Fonte: {item.get('source_name') or 'não informada'}\n"
        f"Documento: {item.get('document_title') or 'não informado'}\n"
        f"URL: {item.get('source_url') or 'não informada'}\n"
        f"Conteúdo:\n{item['content']}"
        for i, item in enumerate(evidence, start=1)
    )

    return f"""
{SYSTEM_INSTRUCTIONS}

CONTEXTO TERRITORIAL EXPLÍCITO:
{context_text or "nenhum"}

CONTEXTO DA CONVERSA:
{conversation_context or "nenhum"}

EVIDÊNCIAS RECUPERADAS:
{evidence_text or "nenhuma evidência recuperada"}

PERGUNTA DO USUÁRIO:
{message}

Responda de forma objetiva.
Quando houver evidência suficiente, use-a diretamente.
Quando não houver evidência suficiente, informe a limitação sem preencher lacunas por conta própria.
""".strip()
