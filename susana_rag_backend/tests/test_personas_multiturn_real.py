"""
Suíte de Testes 100% REAL com Personas do SUS-DF (ZERO MOCKS).
Valida o pipeline RAG, a contextualização multi-turn, a normalização de vocabulário popular
e a ausência de bloqueios falsos do Guardrail em 5 jornadas representativas:
1. Idoso (Seu Sebastião, 72 anos, Ceilândia Sul)
2. Gestante (Camila, 28 anos, Taguatinga)
3. Criança (Juliana e Enzo, 4 anos, Samambaia)
4. Recém-Nascido (Lucas e bebê de 15 dias, Gama)
5. Suspeita de Dengue / Urgência (Marcos, Asa Norte)
"""
import pytest
from app.config import get_settings
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever, is_relevant
from app.rag.guardrails import GuardrailsClassifier
from app.rag.conversation import ConversationalContextManager, expand_popular_terms


class MockHistoryItem:
    def __init__(self, text: str, is_user: bool):
        self._text = text
        self._is_user = is_user

    def get_text(self) -> str:
        return self._text

    def is_user(self) -> bool:
        return self._is_user


@pytest.fixture(scope="module")
def real_components():
    """Carrega os componentes reais de produção conectados ao ChromaDB do SUS-DF."""
    settings = get_settings()
    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    guardrails = GuardrailsClassifier()
    assert retriever.count() > 0, "O banco de dados ChromaDB real deve conter blocos indexados!"
    return {
        "settings": settings,
        "embedder": embedder,
        "retriever": retriever,
        "guardrails": guardrails,
    }


def execute_turn(components, user_message: str, history: list) -> dict:
    """Executa um turno real através da esteira de contextualização, guardrail e busca vetorial."""
    settings = components["settings"]
    embedder = components["embedder"]
    retriever = components["retriever"]
    guardrails = components["guardrails"]

    # 1. Contextualização
    contextualized_query = ConversationalContextManager.contextualize(user_message, history)
    
    # 2. Guardrail
    is_blocked = guardrails.is_clinical(contextualized_query)
    
    # 3. Busca Vetorial Real no ChromaDB
    q_vec = embedder.encode_queries([contextualized_query])[0]
    chunks = retriever.search(q_vec, k=settings.top_k, query_text=contextualized_query)
    
    # 4. Chips Interativos
    sample_response = f"Informações sobre {contextualized_query} na rede do SUS-DF: " + (chunks[0].text[:120] if chunks else "")
    chips = ConversationalContextManager.build_interactive_chips(contextualized_query, sample_response, [c.source for c in chunks])

    return {
        "original_query": user_message,
        "contextualized_query": contextualized_query,
        "is_blocked": is_blocked,
        "chunks": chunks,
        "chips": chips,
    }


# ============================================================================
# PERSONA 1: IDOSO (Seu Sebastião, 72 anos, Ceilândia Sul)
# ============================================================================
def test_persona_1_idoso_ceilandia(real_components):
    """Jornada multi-turn do idoso: postinho -> vacinas -> seleção de opção '1'."""
    history = []

    # Turno 1: Linguagem popular com "postinho" e "pegar remédio" em Ceilândia
    t1 = execute_turn(real_components, "onde tem postinho em ceilandia para idoso pegar remedio?", history)
    assert not t1["is_blocked"], "Pergunta de postinho e remédios de idoso NÃO deve ser bloqueada pelo guardrail!"
    assert "ubs" in t1["contextualized_query"].lower(), "Termo popular 'postinho' deve ser normalizado para UBS!"
    assert len(t1["chunks"]) > 0, "Retriever real deve encontrar unidades de saúde do DF!"
    
    # Atualiza histórico com a resposta simulada contendo opções
    history.append(MockHistoryItem("onde tem postinho em ceilandia para idoso pegar remedio?", is_user=True))
    bot_reply_t1 = (
        "Em Ceilândia você pode buscar acolhimento nas UBSs da região. "
        "1. Horários das salas de vacinação para idosos; "
        "2. Farmácia para retirada de medicamentos de uso contínuo."
    )
    history.append(MockHistoryItem(bot_reply_t1, is_user=False))

    # Turno 2: Pergunta anafórica/elíptica ("quais vacinas eu tomo la?")
    t2 = execute_turn(real_components, "quais vacinas eu tomo la?", history)
    assert not t2["is_blocked"], "Pergunta sobre vacinas NÃO deve ser bloqueada!"
    assert any(term in t2["contextualized_query"].lower() for term in ["vacina", "ubs", "remedio"]), \
        "Turno 2 deve herdar contexto de vacinas/ubs da conversa anterior!"
    assert len(t2["chunks"]) > 0, "Deve recuperar dados reais de vacinas ou unidades!"

    history.append(MockHistoryItem("quais vacinas eu tomo la?", is_user=True))
    history.append(MockHistoryItem("As vacinas para idosos incluem Influenza (gripe) e Covid-19.", is_user=False))

    # Turno 3: Usuário seleciona '1' (antigo ponto de falha que disparava P=0.507)
    t3 = execute_turn(real_components, "1", history)
    assert not t3["is_blocked"], "Dígito '1' NUNCA deve ser bloqueado como clínico!"
    assert len(t3["chunks"]) > 0, "Deve buscar com o contexto associado à opção '1'!"


# ============================================================================
# PERSONA 2: GESTANTE (Camila, 28 anos, Taguatinga)
# ============================================================================
def test_persona_2_gestante_taguatinga(real_components):
    """Jornada multi-turn de gestante: pré-natal -> vacinas da gravidez -> maternidade."""
    history = []

    # Turno 1: Pré-natal em Taguatinga
    t1 = execute_turn(real_components, "estou gravida onde faco meu pre natal em taguatinga?", history)
    assert not t1["is_blocked"], "Consulta administrativa de pré-natal NÃO é clínica!"
    assert "taguatinga" in t1["contextualized_query"].lower()
    assert len(t1["chunks"]) > 0

    history.append(MockHistoryItem("estou gravida onde faco meu pre natal em taguatinga?", is_user=True))
    history.append(MockHistoryItem(
        "O pré-natal é iniciado na UBS de referência da sua quadra em Taguatinga. "
        "• Vacinas recomendadas na gestação; • Exames de rotina.",
        is_user=False
    ))

    # Turno 2: Vacinas da gravidez
    t2 = execute_turn(real_components, "quais vacinas eu preciso tomar na gravidez?", history)
    assert not t2["is_blocked"]
    assert any(term in t2["contextualized_query"].lower() for term in ["vacina", "gravidez", "gestante"])
    assert len(t2["chunks"]) > 0

    history.append(MockHistoryItem("quais vacinas eu preciso tomar na gravidez?", is_user=True))
    history.append(MockHistoryItem("As gestantes devem receber dTpa, Hepatite B e Influenza nas UBSs.", is_user=False))

    # Turno 3: Maternidade de referência
    t3 = execute_turn(real_components, "qual hospital para ter o bebe?", history)
    assert not t3["is_blocked"]
    assert len(t3["chunks"]) > 0


# ============================================================================
# PERSONA 3: CRIANÇA (Juliana e Enzo, 4 anos, Samambaia)
# ============================================================================
def test_persona_3_crianca_samambaia(real_components):
    """Jornada multi-turn infantil: vacina de 4 anos -> horários -> documentos."""
    history = []

    # Turno 1: Vacinação infantil em Samambaia
    t1 = execute_turn(real_components, "preciso vacinar meu filho de 4 anos em samambaia onde levo?", history)
    assert not t1["is_blocked"]
    assert "samambaia" in t1["contextualized_query"].lower()
    assert len(t1["chunks"]) > 0

    history.append(MockHistoryItem("preciso vacinar meu filho de 4 anos em samambaia onde levo?", is_user=True))
    history.append(MockHistoryItem(
        "Você pode levar na sala de vacinas da UBS mais próxima em Samambaia. "
        "A vacinação ocorre de segunda a sexta-feira.",
        is_user=False
    ))

    # Turno 2: Pergunta anafórica sobre horários
    t2 = execute_turn(real_components, "a ubs funciona ate que horas?", history)
    assert not t2["is_blocked"]
    assert "ubs" in t2["contextualized_query"].lower()
    assert len(t2["chunks"]) > 0

    history.append(MockHistoryItem("a ubs funciona ate que horas?", is_user=True))
    history.append(MockHistoryItem("Geralmente das 7h às 19h nas UBSs de horário estendido.", is_user=False))

    # Turno 3: Documentação exigida
    t3 = execute_turn(real_components, "quais documentos precisa levar?", history)
    assert not t3["is_blocked"]
    assert len(t3["chunks"]) > 0


# ============================================================================
# PERSONA 4: RECÉM-NASCIDO (Lucas, bebê de 15 dias, Gama)
# ============================================================================
def test_persona_4_recem_nascido_gama(real_components):
    """Jornada do recém-nascido: teste do pezinho -> vacinas iniciais -> Cartão SUS."""
    history = []

    # Turno 1: Teste do Pezinho no Gama
    t1 = execute_turn(real_components, "meu bebe nasceu a 15 dias onde faco o teste do pezinho no gama?", history)
    assert not t1["is_blocked"]
    assert "gama" in t1["contextualized_query"].lower()
    assert len(t1["chunks"]) > 0

    history.append(MockHistoryItem("meu bebe nasceu a 15 dias onde faco o teste do pezinho no gama?", is_user=True))
    history.append(MockHistoryItem(
        "A triagem neonatal (teste do pezinho) deve ser feita preferencialmente na primeira semana na UBS de referência do Gama.",
        is_user=False
    ))

    # Turno 2: Vacinas após BCG
    t2 = execute_turn(real_components, "ele ja tomou bcg na maternidade qual e a proxima vacina?", history)
    assert not t2["is_blocked"]
    assert len(t2["chunks"]) > 0

    history.append(MockHistoryItem("ele ja tomou bcg na maternidade qual e a proxima vacina?", is_user=True))
    history.append(MockHistoryItem("Aos 2 meses de vida o bebê toma Pentavalente, Pólio (VIP), Pneumocócica 10 e Rotavírus.", is_user=False))

    # Turno 3: Cartão SUS do bebê
    t3 = execute_turn(real_components, "como faco o cartao sus dele?", history)
    assert not t3["is_blocked"]
    assert len(t3["chunks"]) > 0


# ============================================================================
# PERSONA 5: SUSPEITA DE DENGUE / URGÊNCIA (Marcos, Asa Norte)
# ============================================================================
def test_persona_5_dengue_marcos_asa_norte(real_components):
    """Jornada com sintomas de dengue: teste/hidratação -> UPA/emergência -> Hospital de Base."""
    history = []

    # Turno 1: Tendas e acolhimento na Asa Norte
    t1 = execute_turn(real_components, "onde tem teste de dengue e hidratacao na asa norte?", history)
    assert not t1["is_blocked"]
    assert "asa" in t1["contextualized_query"].lower() or "norte" in t1["contextualized_query"].lower()
    assert len(t1["chunks"]) > 0

    history.append(MockHistoryItem("onde tem teste de dengue e hidratacao na asa norte?", is_user=True))
    history.append(MockHistoryItem(
        "Casos leves com suspeita de dengue são atendidos nas UBSs da Asa Norte e nas tendas de acolhimento e hidratação da SES-DF.",
        is_user=False
    ))

    # Turno 2: Encaminhamento em caso de piora (UPA / emergência)
    t2 = execute_turn(real_components, "se piorar onde tem upa ou hospital aqui perto?", history)
    assert not t2["is_blocked"]
    assert len(t2["chunks"]) > 0

    history.append(MockHistoryItem("se piorar onde tem upa ou hospital aqui perto?", is_user=True))
    history.append(MockHistoryItem("Em caso de sinais de alarme procure a UPA ou o Hospital Regional mais próximo.", is_user=False))

    # Turno 3: Horário do Hospital de Base
    t3 = execute_turn(real_components, "qual horario do hospital de base?", history)
    assert not t3["is_blocked"]
    assert len(t3["chunks"]) > 0
    # Verifica que encontra o bloco do Hospital de Base
    assert any("hospital de base" in c.text.lower() or "base" in c.source.lower() for c in t3["chunks"])
