from app.schemas.chat import ChatContext

SYSTEM_INSTRUCTIONS = """
Você é a Susana, assistente de informações sobre o SUS no Distrito Federal.

Regras obrigatórias:
1. Use somente as evidências fornecidas no contexto.
2. Não invente fatos, unidades, endereços, telefones, horários, serviços ou disponibilidade.
3. Se as evidências não forem suficientes, diga claramente que a informação não foi encontrada.
4. Não faça diagnóstico, prescrição, indicação individual de medicamento ou tratamento.
5. Não trate conhecimento geral do modelo como fonte da resposta.
6. Responda em português do Brasil, com linguagem clara, institucional e humana.
7. Nunca invente uma fonte.
8. Não diga que uma informação é atual se a evidência não informar sua atualização.
""".strip()


def build_prompt(message: str, context: ChatContext | None, evidence: list[dict], conversation_context: str = "") -> str:
    context_text = context.model_dump(exclude_none=True) if context else {}
    evidence_text = "\n\n".join(
        f"[EVIDÊNCIA {i}]\nFonte: {item['source_name']}\nDocumento: {item['document_title']}\n"
        f"URL: {item['source_url']}\nConteúdo:\n{item['content']}"
        for i, item in enumerate(evidence, start=1)
    )
    return f"""{SYSTEM_INSTRUCTIONS}

CONTEXTO TERRITORIAL EXPLÍCITO:
{context_text or 'nenhum'}

CONTEXTO DA CONVERSA:
{conversation_context or 'nenhum'}

EVIDÊNCIAS RECUPERADAS:
{evidence_text or 'nenhuma evidência recuperada'}

PERGUNTA DO USUÁRIO:
{message}

Responda de forma objetiva. Quando houver evidência suficiente, use-a diretamente. Quando não houver evidência suficiente, informe a limitação sem preencher lacunas por conta própria.""".strip()
