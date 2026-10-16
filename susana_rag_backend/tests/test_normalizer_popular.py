"""Normalizador de linguagem popular: abreviações, alongamentos, erros de digitação, urgência e vocabulário do dia a dia."""
from __future__ import annotations

import pytest

from app.rag.conversation import ConversationalContextManager, expand_popular_terms
from app.rag.normalizer import (
    detect_urgency,
    looks_off_topic,
    normalize_informal,
    normalize_query,
    squeeze_repeats,
)


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("pq o postinho ta fechado hj", ["por que", "hoje"]),
        ("vc sabe onde tem vacina", ["você sabe"]),
        ("oq precisa p marcar consulta", ["o que", "para marcar"]),
        ("qdo abre a upa", ["quando"]),
        ("tb quero saber da vacina", ["também"]),
        ("pfv me ajuda", ["por favor"]),
        ("cmo faço p tirar o cartao sus", ["como", "para tirar", "cartão sus"]),
        ("td bem? mto obg", ["tudo bem", "muito"]),
        ("preciso d consulta c ginecologista", ["de consulta", "com ginecologista"]),
        ("msm sem cartao posso ser atendido", ["mesmo sem"]),
        ("qual hr a upa fecha", ["qual hora"]),
        ("cartaosus como tirar", ["cartão sus"]),
    ],
)
def test_abreviacoes_sao_expandidas(entrada, esperado):
    saida = normalize_informal(entrada).lower()
    for trecho in esperado:
        assert trecho in saida, f"'{trecho}' ausente em: {saida}"


def test_p_sul_de_ceilandia_nao_vira_para():
    assert "p sul" in normalize_informal("onde fica a ubs da p sul").lower()


@pytest.mark.parametrize(
    "entrada, esperado",
    [("socorrooooo", "socorro"), ("mordida de cachorroooo", "mordida de cachorro"), ("oi???", "oi?")],
)
def test_alongamentos_sao_reduzidos(entrada, esperado):
    assert squeeze_repeats(entrada) == esperado


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("vaciina da gripe", "vacina"),
        ("unidde bsica de saude", "unidade"),
        ("farmaica de alto custo", "farmácia"),
        ("hospitall regional", "hospital"),
        ("smambaia", "samambaia"),
    ],
)
def test_erros_de_digitacao_sao_corrigidos(entrada, esperado):
    assert esperado in normalize_informal(entrada).lower()


def test_caixa_alta_vira_minuscula_mas_siglas_ficam():
    saida = normalize_informal("ONDE FICA A UBS DE AGUAS CLARAS ENDEREÇO")
    assert "UBS" in saida and "onde fica" in saida


def test_palavras_comuns_nao_sao_corrigidas_por_engano():
    texto = "quero marcar uma consulta amanhã com o dentista"
    assert normalize_informal(texto).lower().count("dentista") == 1
    assert "poste" in normalize_informal("o poste caiu").lower()


@pytest.mark.parametrize(
    "texto",
    [
        "um cachorro me mordeu socorro",
        "fui mordido por um morcego",
        "uma cobra me picou",
        "escorpião me picou",
        "como chamar uma ambulância",
        "onde reclamar do atendimento no posto",
        "como doar leite materno",
        "pq o postinho fechou? msm sem cartaosus",
    ],
)
def test_normalizacao_e_idempotente(texto):
    uma = expand_popular_terms(texto)
    assert expand_popular_terms(uma) == uma


@pytest.mark.parametrize(
    "texto, termos",
    [
        ("um cachorro me mordeu", ["raiva", "HRAN"]),
        ("fui mordido por um morcego", ["raiva", "HRT"]),
        ("meu gato me arranhou e mordeu", ["raiva"]),
        ("vacina da raiva onde tomo", ["antirrábic"]),
        ("uma cobra me mordeu", ["peçonhento", "soro antiofídico"]),
        ("quero chamar a ambulancia", ["SAMU 192"]),
        ("onde reclamo do atendimento do medico", ["Ouvidoria"]),
        ("vaga pra cirurgia", ["regulação"]),
        ("como doar leite materno", ["Banco de Leite"]),
        ("tirar o cartao sus", ["Cartão Nacional de Saúde"]),
        ("exame de hiv gratis", ["HIV"]),
    ],
)
def test_vocabulario_popular_ganha_termos_oficiais(texto, termos):
    saida = expand_popular_terms(texto)
    for t in termos:
        assert t in saida, f"'{t}' ausente em: {saida}"


@pytest.mark.parametrize(
    "texto",
    ["cobra de brinquedo pra comprar", "quero comprar uma aranha de pelucia", "filme do homem aranha"],
)
def test_animais_fora_do_contexto_de_saude_nao_acionam_peconhentos(texto):
    assert "peçonhento" not in expand_popular_terms(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "socorro quero chamar a ambulancia",
        "emergência! pessoa desmaiada",
        "urgente, fui mordido por um cachorro",
        "socorro meu filho caiu e esta sangrando",
        "me ajuda, acidente de carro com feridos",
    ],
)
def test_palavras_de_urgencia_sao_detectadas(texto):
    assert detect_urgency(texto)


@pytest.mark.parametrize(
    "texto",
    ["socorro meu celular quebrou", "urgente preciso de um emprestimo", "onde fica a ubs", "como tirar o cartao sus"],
)
def test_urgencia_sem_contexto_de_saude_nao_dispara(texto):
    assert not detect_urgency(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "socorro meu carro quebrou na estrada",
        "qual a previsao do tempo amanha",
        "como renovar minha cnh",
        "receita de bolo de cenoura",
        "socorro perdi minha senha do banco",
        "onde fica o cartorio de registro civil",
    ],
)
def test_assuntos_fora_da_saude_sao_barrados(texto):
    assert looks_off_topic(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "socorro onde fica a upa",
        "urgente soro antiofidico onde tem",
        "ajuda com bebida e droga onde tem caps",
        "como doar leite materno",
        "socorro",  # frase curta segue para a resposta de emergência
        "cobra me mordeu",
    ],
)
def test_assuntos_de_saude_nao_sao_barrados(texto):
    assert not looks_off_topic(texto)


def test_urgencia_ganha_samu_e_upa_na_consulta():
    saida = normalize_query("emergencia! pessoa desmaiada na rua")
    assert "SAMU 192" in saida and "UPA" in saida


def test_tema_especifico_nao_recebe_ruido_de_urgencia_generica():
    saida = expand_popular_terms("fui mordido por um cachorro, urgente")
    assert "raiva" in saida and "SAMU" not in saida


# ---- complementos curtos herdam o tema da pergunta anterior -------------------------------------------
class _T:
    def __init__(self, text, user=True):
        self._t, self._u = text, user

    def get_text(self):
        return self._t

    def is_user(self):
        return self._u


@pytest.mark.parametrize(
    "anterior, seguinte, termo",
    [
        ("quero saber da vacina da gripe", "pra idoso tb?", "vacina"),
        ("onde fica a upa de ceilandia?", "e o horario?", "upa"),
        ("me mordeu um cachorro", "e agora, pra onde vou?", "raiva"),
        ("to gravida", "que vacina eu tomo", "grávida"),
        ("quero marcar consulta", "precisa de documento?", "agendamento"),
    ],
)
def test_complemento_curto_herda_o_tema(anterior, seguinte, termo):
    ctx = ConversationalContextManager.contextualize(seguinte, [_T(anterior)])
    assert termo in ctx.lower()


def test_pergunta_completa_nao_herda_tema_antigo():
    ctx = ConversationalContextManager.contextualize("qual o horário da UPA de Taguatinga?", [_T("quero vacina da gripe")])
    assert "gripe" not in ctx.lower()
