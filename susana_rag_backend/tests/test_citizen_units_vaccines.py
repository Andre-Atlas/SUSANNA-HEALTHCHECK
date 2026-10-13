"""
Testes Automatizados Reais para Cidadão, Multi-Sessões, Unidades do DF e Guia Vacinal
====================================================================================
Validação rigorosa sem mocks de dados, cobrindo regras oficiais de CPF, CNS,
persistência relacional SQLite, catálogo geográfico das 33 RAs e PNI/SES-DF.
"""
from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient

from app.citizen.validators import validate_cns, validate_cpf
from app.main import app

client = TestClient(app)


# ===========================================================================
# 1. Testes Algorítmicos Reais de CPF e CNS
# ===========================================================================
def test_cpf_validation_official_algorithm():
    # CPFs matematicamente válidos conhecidos (módulo 11)
    valid_cpfs = [
        "12345678909",
        "05481729199",
        "52998224725",
        "123.456.789-09",
    ]
    for cpf_str in valid_cpfs:
        assert validate_cpf(cpf_str) is True, f"Esperado CPF válido: {cpf_str}"

    # CPFs inválidos: todos dígitos iguais
    assert validate_cpf("11111111111") is False
    assert validate_cpf("00000000000") is False
    assert validate_cpf("99999999999") is False

    # CPFs com tamanho incorreto ou caracteres inválidos
    assert validate_cpf("123456") is False
    assert validate_cpf("abcdefghijk") is False

    # CPF com dígito verificador adulterado
    assert validate_cpf("12345678908") is False


def test_cns_validation_official_algorithm():
    # 1. CNS válidos oficiais com base PIS/PASEP (iniciados em 1 ou 2)
    cns_definitivo_valido = "154823192010000"
    assert validate_cns(cns_definitivo_valido) is True
    assert validate_cns("154 8231 9201 0000") is True

    # 2. CNS válido provisório oficial (iniciado em 7, 8 ou 9)
    cns_provisorio_valido = "700000000000005"
    assert validate_cns(cns_provisorio_valido) is True

    # 3. CNS inválidos: formato, caracteres, tamanho e soma
    assert validate_cns("123") is False
    assert validate_cns("abcdefghijklmno") is False
    assert validate_cns("111111111111111") is False  # Inválido na soma
    assert validate_cns("700000000000004") is False  # Provisório com dígito adulterado


def _generate_valid_cpf() -> str:
    import random
    prefix = [random.randint(1, 8)] + [random.randint(0, 9) for _ in range(8)]
    s1 = sum(prefix[i] * (10 - i) for i in range(9))
    d1 = 11 - (s1 % 11)
    d1 = 0 if d1 >= 10 else d1
    prefix.append(d1)
    s2 = sum(prefix[i] * (11 - i) for i in range(10))
    d2 = 11 - (s2 % 11)
    d2 = 0 if d2 >= 10 else d2
    prefix.append(d2)
    return "".join(str(d) for d in prefix)


# ===========================================================================
# 2. Testes de Cadastro, Login e Perfil do Cidadão (SQLite Real)
# ===========================================================================
def test_citizen_registration_and_login_flow():
    # Usar CPF matematicamente válido gerado dinamicamente para evitar colisões
    cpf_valido = _generate_valid_cpf()
    payload = {
        "nome_completo": "Ana Paula de Souza",
        "cpf": cpf_valido,
        "data_nascimento": "1994-05-15",
        "sexo_biologico": "F",
        "gestante": True,
        "ra_residencia": "ceilandia",
        "bairro_ou_setor": "QNM 18",
        "telefone": "(61) 98888-7777",
    }

    # Cadastro
    resp = client.post("/api/citizen/register", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["nome_completo"].lower() == "ana paula de souza"
    assert data["faixa_etaria"] == "adulto"
    assert data["gestante"] is True
    assert data["ra_residencia"] == "ceilandia"
    assert "ra_display" in data
    assert data["cpf_mascarado"].startswith("***.")
    citizen_id = data["id"]

    # Rejeição de cadastro duplicado com mesmo CPF
    resp_dup = client.post("/api/citizen/register", json=payload)
    assert resp_dup.status_code in (400, 422)

    # Login por CPF e data de nascimento
    resp_login = client.post(
        "/api/citizen/login",
        json={"cpf_or_cns": cpf_valido, "data_nascimento": "1994-05-15"},
    )
    assert resp_login.status_code == 200
    assert resp_login.json()["id"] == citizen_id
    assert resp_login.json()["nome_completo"].lower() == "ana paula de souza"

    # Atualização de Perfil (ex: mudou de RA para Taguatinga)
    resp_update = client.patch(
        f"/api/citizen/me?citizen_id={citizen_id}",
        json={"ra_residencia": "taguatinga", "bairro_ou_setor": "QNB 12", "gestante": False},
    )
    assert resp_update.status_code == 200
    updated_data = resp_update.json()
    assert updated_data["ra_residencia"] == "taguatinga"
    assert updated_data["bairro_ou_setor"] == "QNB 12"
    assert updated_data["gestante"] is False


def test_citizen_registration_rejects_invalid_cpf():
    payload = {
        "nome_completo": "Carlos Falso",
        "cpf": "111.111.111-11",
        "data_nascimento": "1980-01-01",
        "ra_residencia": "plano_piloto",
    }
    resp = client.post("/api/citizen/register", json=payload)
    assert resp.status_code in (400, 422)


# ===========================================================================
# 3. Testes de Multi-Sessões de Chat e Histórico (Janelas Separadas)
# ===========================================================================
def test_multi_session_chat_flow():
    # 1. Criar primeira sessão
    resp1 = client.post("/api/chat/sessions", json={"title": "Dúvida sobre Vacina de Gripe"})
    assert resp1.status_code == 200
    s1 = resp1.json()
    s1_id = s1["id"]
    assert s1["title"] == "Dúvida sobre Vacina de Gripe"

    # 2. Criar segunda sessão (janela separada)
    resp2 = client.post("/api/chat/sessions", json={"title": "UBS mais próxima em Ceilândia"})
    assert resp2.status_code == 200
    s2 = resp2.json()
    s2_id = s2["id"]
    assert s2_id != s1_id

    # 3. Gravar mensagens na sessão 1
    msg1_req = {
        "session_id": s1_id,
        "role": "user",
        "content": "Onde posso tomar a vacina da gripe?",
    }
    resp_m1 = client.post("/api/chat/sessions/messages", json=msg1_req)
    assert resp_m1.status_code == 200

    msg2_req = {
        "session_id": s1_id,
        "role": "assistant",
        "content": "A vacina contra a Influenza está disponível em todas as UBSs do DF.",
        "source": "rag_corpus",
    }
    resp_m2 = client.post("/api/chat/sessions/messages", json=msg2_req)
    assert resp_m2.status_code == 200

    # 4. Listar sessões e checar se ambas aparecem
    resp_list = client.get("/api/chat/sessions")
    assert resp_list.status_code == 200
    sessions = resp_list.json()
    assert any(s["id"] == s1_id for s in sessions)
    assert any(s["id"] == s2_id for s in sessions)

    # 5. Recuperar histórico da sessão 1
    resp_hist = client.get(f"/api/chat/sessions/{s1_id}/messages")
    assert resp_hist.status_code == 200
    hist = resp_hist.json()
    assert len(hist) == 2
    assert hist[0]["role"] == "user"
    assert hist[1]["role"] == "assistant"
    assert hist[1]["source"] == "rag_corpus"

    # 6. Histórico da sessão 2 deve estar vazio
    resp_hist2 = client.get(f"/api/chat/sessions/{s2_id}/messages")
    assert resp_hist2.status_code == 200
    assert len(resp_hist2.json()) == 0

    # 7. Excluir sessão 2
    resp_del = client.delete(f"/api/chat/sessions/{s2_id}")
    assert resp_del.status_code == 200
    assert resp_del.json()["status"] == "deleted"


# ===========================================================================
# 4. Testes de Unidades de Saúde Reais do DF (346 Blocos, 33 RAs)
# ===========================================================================
def test_units_directory_and_ra_filtering():
    # 1. Listar todas as RAs disponíveis
    resp_ras = client.get("/api/units/ras")
    assert resp_ras.status_code == 200
    ras = resp_ras.json()
    assert len(ras) >= 33, f"Esperado pelo menos 33 RAs, recebido {len(ras)}"
    assert any(r["ra"] == "ceilandia" for r in ras)
    assert any(r["ra"] == "plano_piloto" for r in ras)
    assert any(r["ra"] == "sobradinho" for r in ras)

    # 2. Filtrar unidades por RA (Ceilândia)
    resp_ceilandia = client.get("/api/units?ra=ceilandia")
    assert resp_ceilandia.status_code == 200
    data_ceilandia = resp_ceilandia.json()
    assert data_ceilandia["total"] > 0
    assert all("ceilandia" in u["ra"].lower() or "ceilândia" in u["ra_display"].lower() for u in data_ceilandia["units"])

    # 3. Filtrar por tipo (Hospital)
    resp_hospitais = client.get("/api/units?tipo=hospital")
    assert resp_hospitais.status_code == 200
    data_hosp = resp_hospitais.json()
    assert data_hosp["total"] > 0
    assert any("hospital" in u["nome"].lower() or u["tipo"] in ("hospital", "regional") for u in data_hosp["units"])

    # 4. Buscar por texto livre ("Gama")
    resp_busca = client.get("/api/units?q=Gama")
    assert resp_busca.status_code == 200
    assert resp_busca.json()["total"] > 0


    # 5. Verificar campos geográficos percentuais de SVG
    primeira_unidade = data_ceilandia["units"][0]
    assert "svg_x" in primeira_unidade
    assert "svg_y" in primeira_unidade
    assert 0.0 <= primeira_unidade["svg_x"] <= 100.0
    assert 0.0 <= primeira_unidade["svg_y"] <= 100.0



# ===========================================================================
# 5. Testes do Guia Oficial de Vacinação (PNI / SES-DF)
# ===========================================================================
def test_vaccines_guide_and_recommendations():
    # 1. Listar guia completo
    resp_guide = client.get("/api/vaccines/guide")
    assert resp_guide.status_code == 200
    guide = resp_guide.json()
    assert guide["total"] >= 15
    assert len(guide["campanhas_ativas"]) >= 1

    # Verificar vacinas essenciais do PNI
    nomes_vacinas = [v["nome"] for v in guide["vacinas"]]
    assert any("BCG" in n for n in nomes_vacinas)
    assert any("Pentavalente" in n for n in nomes_vacinas)
    assert any("Poliomielite" in n or "VIP" in n for n in nomes_vacinas)
    assert any("HPV" in n for n in nomes_vacinas)
    assert any("Influenza" in n for n in nomes_vacinas)

    # 2. Filtro por faixa etária (idoso)
    resp_idoso = client.get("/api/vaccines/guide?faixa_etaria=idoso")
    assert resp_idoso.status_code == 200
    vac_idoso = resp_idoso.json()["vacinas"]
    assert len(vac_idoso) > 0
    assert all(v["faixa_etaria"] == "idoso" for v in vac_idoso)

    # 3. Recomendação personalizada para Gestante
    resp_rec_gestante = client.get("/api/vaccines/recommendations?data_nascimento=1995-02-10&gestante=true")
    assert resp_rec_gestante.status_code == 200
    rec_gestante = resp_rec_gestante.json()
    assert rec_gestante["gestante"] is True
    assert rec_gestante["proxima_dose_alerta"] is not None
    assert "dTpa" in rec_gestante["proxima_dose_alerta"]
    assert any("dTpa" in v["nome"] or v["sigla"] == "dTpa" for v in rec_gestante["vacinas_recomendadas"])

    # 4. Recomendação personalizada para Idoso (68 anos)
    resp_rec_idoso = client.get("/api/vaccines/recommendations?data_nascimento=1956-07-20&gestante=false")
    assert resp_rec_idoso.status_code == 200
    rec_idoso = resp_rec_idoso.json()
    assert rec_idoso["faixa_etaria"] == "idoso"
    assert rec_idoso["idade_anos"] >= 68
    assert "Influenza" in rec_idoso["proxima_dose_alerta"]
