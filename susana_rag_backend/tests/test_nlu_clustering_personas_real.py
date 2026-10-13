"""
Suíte de Testes Reais de Expansão, Clusterização, NLU e Personas do SUS-DF.
Execução 100% real contra o ChromaDB persistido em data/chroma_db (2.365 blocos).
Sem mocks de dados. Valida todas as personas em turnos conversacionais encadeados
em múltiplas Regiões Administrativas do Distrito Federal.
"""
import json
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.rag.embeddings import Embedder
from app.rag.retriever import ChromaRetriever, is_relevant
from app.rag.nlu import NaturalLanguageInferencer
from app.rag.conversation import ConversationalContextManager


@pytest.fixture(scope="module")
def real_rag_components():
    settings = get_settings()
    embedder = Embedder(settings.embedding_model, settings.embedding_max_seq_length)
    retriever = ChromaRetriever(embedder, settings.chroma_dir)
    return embedder, retriever, settings


class TestNLUAndClusteringReal:
    """Valida o motor de NLU e a clusterização de metadados das 33 Regiões Administrativas."""

    def test_nlu_geographic_coverage_33_ras(self):
        """Testa o reconhecimento das 33 Regiões Administrativas do Distrito Federal."""
        test_cases = [
            ("onde tem ubs na ceilandia norte?", "ceilandia", "Ceilandia"),
            ("vacina da gripe em taguatinga sul", "taguatinga", "Taguatinga"),
            ("posto de saude em samambaia norte", "samambaia", "Samambaia"),
            ("unidade de saude na asa sul", "plano_piloto", "Plano Piloto"),
            ("pre natal no gama setor oeste", "gama", "Gama"),
            ("posto de saude no guara ii", "guara", "Guara"),
            ("atendimento em sobradinho ii ar 13", "sobradinho_ii", "Sobradinho II"),
            ("atendimento de urgencia em sobradinho", "sobradinho", "Sobradinho"),
            ("teste do pezinho em planaltina", "planaltina", "Planaltina"),
            ("upa de santa maria", "santa_maria", "Santa Maria"),
            ("ubs na vila nova em sao sebastiao", "sao_sebastiao", "Sao Sebastiao"),
            ("posto de saude no recanto das emas", "recanto_das_emas", "Recanto das Emas"),
            ("atendimento no paranoa parque", "paranoa", "Paranoa"),
            ("ubs no nucleo bandeirante metropolitana", "nucleo_bandeirante", "Nucleo Bandeirante"),
            ("posto de saude em brazlandia", "brazlandia", "Brazlandia"),
            ("unidade basica no riacho fundo ii", "riacho_fundo_ii", "Riacho Fundo II"),
            ("posto de saude no riacho fundo i", "riacho_fundo", "Riacho Fundo"),
            ("ubs no cruzeiro novo sres", "cruzeiro", "Cruzeiro"),
            ("onde vacinar em aguas claras", "aguas_claras", "Aguas Claras"),
            ("posto de saude em vicente pires", "vicente_pires", "Vicente Pires"),
            ("posto de saude na estrutural scia", "scia_estrutural", "Estrutural"),
            ("atendimento no sol nascente trecho 1", "sol_nascente_por_do_sol", "Sol Nascente"),
            ("posto de saude no del lago itapoa", "itapoa", "Itapoa"),
            ("atendimento no lago sul shis", "lago_sul", "Lago Sul"),
            ("ubs no lago norte shin taquari", "lago_norte", "Lago Norte"),
            ("posto de saude na candangolandia", "candangolandia", "Candangolandia"),
            ("unidade no sudoeste octogonal", "sudoeste_octogonal", "Sudoeste"),
            ("posto de saude no varjao", "varjao", "Varjao"),
            ("atendimento de saude no park way", "park_way", "Park Way"),
            ("ubs no mangueiral jardim botanico", "jardim_botanico", "Jardim Botanico"),
            ("unidade de saude no sia", "sia", "Sia"),
            ("ubs na fercal lages", "fercal", "Fercal"),
            ("posto de saude em arniqueira", "arniqueira", "Arniqueira"),
        ]
        assert len(test_cases) == 33, f"Necessário testar exatamente as 33 RAs do DF (encontrado: {len(test_cases)})"
        for query, expected_ra, expected_display in test_cases:
            res = NaturalLanguageInferencer.infer(query)
            assert res.ra == expected_ra, f"Falha para query: '{query}' -> esperado {expected_ra}, obteve {res.ra}"
            assert expected_display.lower() in res.ra_display.lower()

    def test_nlu_generic_brasilia_maps_to_geral_df(self):
        """Garante que 'Brasília' genérico sem bairros do Plano Piloto mapeie para geral_df."""
        res = NaturalLanguageInferencer.infer("como funciona o atendimento do sus em brasilia?")
        assert res.ra == "geral_df"
        assert res.metadata_filter is None

    def test_nlu_bot_poisoning_isolation(self):
        """Garante que mensagens do assistente no histórico não contaminem a inferência de RA ou Persona."""
        # O usuário perguntou sobre Ceilândia. O assistente respondeu citando Taguatinga e Gama como alternativas.
        history = [
            {"role": "user", "text": "quais as ubs em ceilandia norte?"},
            {"role": "assistant", "text": "Temos unidades na Ceilândia, mas você também pode ir a Taguatinga ou Gama se preferir."},
        ]
        # O usuário apenas pergunta o horário em seguida (sem citar cidade)
        res = NaturalLanguageInferencer.infer("e qual o horario de atendimento?", history=history)
        # Deve manter Ceilândia da fala do usuário, e NÃO Taguatinga/Gama da fala do bot!
        assert res.ra == "ceilandia"

    def test_nlu_persona_and_intent_extraction(self):
        """Valida se as personas e intenções são detectadas em milissegundos."""
        # 1. Idoso
        res_idoso = NaturalLanguageInferencer.infer("sou idoso de 68 anos e preciso retirar meus remedios de diabetes")
        assert res_idoso.persona == "idoso"
        assert res_idoso.intent == "MEDICAMENTOS_FARMACIA"
        assert res_idoso.cluster == "medicamentos_farmacia"

        # 2. Gestante
        res_gestante = NaturalLanguageInferencer.infer("estou gravida de 8 semanas, como iniciar o pre natal?")
        assert res_gestante.persona == "gestante"
        assert res_gestante.intent == "PRE_NATAL_PUERICULTURA"
        assert res_gestante.cluster == "saude_materno_infantil"

        # 3. Recém-Nascido
        res_rn = NaturalLanguageInferencer.infer("meu bebe nasceu faz 4 dias, onde faz o teste do pezinho?")
        assert res_rn.persona == "recem_nascido"
        assert res_rn.intent == "PRE_NATAL_PUERICULTURA"
        assert res_rn.cluster == "saude_materno_infantil"

        # 4. Vacinação
        res_vacina = NaturalLanguageInferencer.infer("quais vacinas infantis estao disponiveis?")
        assert res_vacina.persona == "crianca"
        assert res_vacina.intent == "VACINACAO"
        assert res_vacina.cluster == "vacinacao"

        # 5. Urgência / Dengue
        res_urg = NaturalLanguageInferencer.infer("estou com suspeita de dengue, febre muito alta e dor forte na barriga")
        assert res_urg.intent == "URGENCIA_SINTOMAS"
        assert res_urg.cluster == "urgencia_emergencia"


class TestPersonasMultiturnRealScenarios:
    """Testes reais de ponta a ponta com as personas nas Regiões Administrativas do DF."""

    def test_persona_idoso_taguatinga_real(self, real_rag_components):
        """Persona Idoso: Acesso a medicamentos de diabetes e vacina da gripe em Taguatinga."""
        embedder, retriever, settings = real_rag_components

        # Turno 1: Encontrar UBS em Taguatinga para doente crônico
        q1 = "sou idoso com diabetes, onde tem posto de saude em Taguatinga?"
        nlu_1 = NaturalLanguageInferencer.infer(q1)
        assert nlu_1.ra == "taguatinga"
        assert nlu_1.persona == "idoso"

        vec1 = embedder.encode_queries([nlu_1.expanded_query])[0]
        chunks1 = retriever.search(vec1, k=3, query_text=nlu_1.expanded_query, where_filter=nlu_1.metadata_filter)
        assert len(chunks1) > 0
        assert is_relevant(chunks1, nlu_1.expanded_query, settings.similarity_threshold, settings.relevance_confident_threshold)
        assert any("Taguatinga" in c.text for c in chunks1)

        # Turno 2: Pergunta encadeada sobre horário de atendimento (Saúde na Hora)
        q2 = "e qual o horario de atendimento?"
        history = [
            {"role": "user", "text": q1},
            {"role": "assistant", "text": chunks1[0].text[:200]}
        ]
        contextualized_2 = ConversationalContextManager.contextualize(q2, history)
        nlu_2 = NaturalLanguageInferencer.infer(contextualized_2, history=history)
        assert nlu_2.ra == "taguatinga"

        vec2 = embedder.encode_queries([nlu_2.expanded_query])[0]
        chunks2 = retriever.search(vec2, k=3, query_text=nlu_2.expanded_query, where_filter=nlu_2.metadata_filter)
        assert len(chunks2) > 0
        assert any("horário" in c.text.lower() or "07:00" in c.text for c in chunks2)

    def test_persona_gestante_ceilandia_real(self, real_rag_components):
        """Persona Gestante: Consulta de pré-natal e vacinação na Ceilândia."""
        embedder, retriever, settings = real_rag_components

        # Turno 1: Pré-natal na Ceilândia
        q1 = "descobri que estou gravida, onde faco o pre natal em Ceilandia?"
        nlu_1 = NaturalLanguageInferencer.infer(q1)
        assert nlu_1.ra == "ceilandia"
        assert nlu_1.persona == "gestante"

        vec1 = embedder.encode_queries([nlu_1.expanded_query])[0]
        chunks1 = retriever.search(vec1, k=3, query_text=nlu_1.expanded_query, where_filter=nlu_1.metadata_filter)
        assert len(chunks1) > 0
        assert is_relevant(chunks1, nlu_1.expanded_query, settings.similarity_threshold, settings.relevance_confident_threshold)
        assert any("Ceilândia" in c.text and "pré-natal" in c.text.lower() for c in chunks1)

        # Turno 2: Encadeado - Maternidade ou urgência da gestante
        q2 = "se eu tiver um sangramento ou comecar o parto, pra onde vou?"
        history = [
            {"role": "user", "text": q1},
            {"role": "assistant", "text": chunks1[0].text[:200]}
        ]
        contextualized_2 = ConversationalContextManager.contextualize(q2, history)
        nlu_2 = NaturalLanguageInferencer.infer(contextualized_2, history=history)
        assert nlu_2.ra == "ceilandia"

        vec2 = embedder.encode_queries([nlu_2.expanded_query])[0]
        chunks2 = retriever.search(vec2, k=3, query_text=nlu_2.expanded_query, where_filter=nlu_2.metadata_filter)
        assert len(chunks2) > 0
        assert any("HRC" in c.text or "Hospital Regional de Ceilândia" in c.text or "UPA" in c.text for c in chunks2)

    def test_persona_recem_nascido_samambaia_real(self, real_rag_components):
        """Persona Recém-Nascido: Teste do pezinho e primeiras vacinas em Samambaia."""
        embedder, retriever, settings = real_rag_components

        # Turno 1: Teste do pezinho
        q1 = "meu bebe acabou de nascer, onde faz o teste do pezinho em Samambaia?"
        nlu_1 = NaturalLanguageInferencer.infer(q1)
        assert nlu_1.ra == "samambaia"
        assert nlu_1.persona == "recem_nascido"

        vec1 = embedder.encode_queries([nlu_1.expanded_query])[0]
        chunks1 = retriever.search(vec1, k=3, query_text=nlu_1.expanded_query, where_filter=nlu_1.metadata_filter)
        assert len(chunks1) > 0
        assert is_relevant(chunks1, nlu_1.expanded_query, settings.similarity_threshold, settings.relevance_confident_threshold)
        assert any("teste do pezinho" in c.text.lower() for c in chunks1)
        assert any("Samambaia" in c.text for c in chunks1)

        # Turno 2: Encadeado - Primeiras vacinas (BCG e Hepatite B)
        q2 = "e quais as primeiras vacinas que ele precisa tomar na sala de vacina?"
        history = [
            {"role": "user", "text": q1},
            {"role": "assistant", "text": chunks1[0].text[:200]}
        ]
        contextualized_2 = ConversationalContextManager.contextualize(q2, history)
        nlu_2 = NaturalLanguageInferencer.infer(contextualized_2, history=history)
        assert nlu_2.ra == "samambaia"
        assert nlu_2.intent == "VACINACAO"

        vec2 = embedder.encode_queries([nlu_2.expanded_query])[0]
        chunks2 = retriever.search(vec2, k=3, query_text=nlu_2.expanded_query, where_filter=nlu_2.metadata_filter)
        assert len(chunks2) > 0
        assert any("vacina" in c.text.lower() or "bcg" in c.text.lower() or "hepatite" in c.text.lower() for c in chunks2)

    def test_persona_crianca_sobradinho_real(self, real_rag_components):
        """Persona Criança: Sala de vacinas e acompanhamento infantil em Sobradinho."""
        embedder, retriever, settings = real_rag_components

        # Turno 1: Vacinas infantis
        q1 = "onde levar minha filha para tomar as vacinas infantis em Sobradinho?"
        nlu_1 = NaturalLanguageInferencer.infer(q1)
        assert nlu_1.ra == "sobradinho"
        assert nlu_1.persona == "crianca"

        vec1 = embedder.encode_queries([nlu_1.expanded_query])[0]
        chunks1 = retriever.search(vec1, k=3, query_text=nlu_1.expanded_query, where_filter=nlu_1.metadata_filter)
        assert len(chunks1) > 0
        assert is_relevant(chunks1, nlu_1.expanded_query, settings.similarity_threshold, settings.relevance_confident_threshold)
        assert any("vacina" in c.text.lower() for c in chunks1)
        assert any("Sobradinho" in c.text for c in chunks1)

        # Turno 2: Encadeado - Puericultura e acompanhamento de crescimento
        q2 = "e para fazer a consulta de rotina do crescimento (puericultura)?"
        history = [
            {"role": "user", "text": q1},
            {"role": "assistant", "text": chunks1[0].text[:200]}
        ]
        contextualized_2 = ConversationalContextManager.contextualize(q2, history)
        nlu_2 = NaturalLanguageInferencer.infer(contextualized_2, history=history)
        assert nlu_2.ra == "sobradinho"

        vec2 = embedder.encode_queries([nlu_2.expanded_query])[0]
        chunks2 = retriever.search(vec2, k=3, query_text=nlu_2.expanded_query, where_filter=nlu_2.metadata_filter)
        assert len(chunks2) > 0
        assert any("puericultura" in c.text.lower() or "criança" in c.text.lower() or "ubs" in c.text.lower() for c in chunks2)

    def test_persona_urgencia_dengue_gama_real(self, real_rag_components):
        """Persona Urgência: Febre alta, sinais de alarme e busca por UPA no Gama."""
        embedder, retriever, settings = real_rag_components

        # Turno 1: Suspeita de dengue no Gama
        q1 = "estou com sintomas fortes de dengue e muita dor no corpo no Gama, onde tem atendimento?"
        nlu_1 = NaturalLanguageInferencer.infer(q1)
        assert nlu_1.ra == "gama"

        vec1 = embedder.encode_queries([nlu_1.expanded_query])[0]
        chunks1 = retriever.search(vec1, k=3, query_text=nlu_1.expanded_query, where_filter=nlu_1.metadata_filter)
        assert len(chunks1) > 0
        assert is_relevant(chunks1, nlu_1.expanded_query, settings.similarity_threshold, settings.relevance_confident_threshold)
        assert any("Gama" in c.text and ("UPA" in c.text or "Hospital Regional do Gama" in c.text or "UBS" in c.text) for c in chunks1)

        # Turno 2: Encadeado - Sinais de alarme (urgência imediata UPA 24h)
        q2 = "se comecar a vomitar sem parar e ter dor forte na barriga, a UPA atende de noite?"
        history = [
            {"role": "user", "text": q1},
            {"role": "assistant", "text": chunks1[0].text[:200]}
        ]
        contextualized_2 = ConversationalContextManager.contextualize(q2, history)
        nlu_2 = NaturalLanguageInferencer.infer(contextualized_2, history=history)
        assert nlu_2.ra == "gama"
        assert nlu_2.intent == "URGENCIA_SINTOMAS"

        vec2 = embedder.encode_queries([nlu_2.expanded_query])[0]
        chunks2 = retriever.search(vec2, k=3, query_text=nlu_2.expanded_query, where_filter=nlu_2.metadata_filter)
        assert len(chunks2) > 0
        assert any("UPA" in c.text or "24 horas" in c.text or "emergência" in c.text.lower() for c in chunks2)


class TestRealChatEndpointsIntegration:
    """Valida os endpoints /api/chat e /api/chat/stream em ambiente real integrado."""

    def test_real_chat_post_and_stream_endpoints(self):
        with TestClient(app) as client:
            # 1. Endpoint /api/chat (batch)
            res_chat = client.post("/api/chat", json={"message": "quais as ubs em ceilandia?"})
            assert res_chat.status_code == 200
            data_chat = res_chat.json()
            assert "response" in data_chat
            assert len(data_chat["response"]) > 20
            assert data_chat["is_blocked"] is False

            # 2. Endpoint /api/chat/stream (NDJSON streaming)
            res_stream = client.post(
                "/api/chat/stream",
                json={
                    "message": "onde vacinar contra a gripe em taguatinga?",
                    "history": []
                }
            )
            assert res_stream.status_code == 200
            lines = [line.strip() for line in res_stream.text.split("\n") if line.strip()]
            assert len(lines) >= 2  # Pelo menos chunks e evento done

            events = [json.loads(line) for line in lines]
            done_events = [e for e in events if e.get("type") == "done"]
            assert len(done_events) == 1
            assert done_events[0].get("is_blocked") is False
            assert "options" in done_events[0]
