"""
Normalizador de linguagem popular para o SUS-DF.

Transforma a escrita do cidadão (abreviações de chat, alongamentos, erros de digitação,
palavras de urgência, vocabulário do dia a dia) em termos que existem nos documentos
oficiais, antes de a pergunta chegar ao guardrail, à NLU e aos embeddings.

Tudo é determinístico e roda em microssegundos; não há chamada de rede nem de modelo.
As funções são idempotentes: aplicar duas vezes não muda o resultado.
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from typing import List, Tuple


def fold(text: str) -> str:
    """Minúsculas e sem acentos (para comparar)."""
    n = unicodedata.normalize("NFKD", text).casefold()
    return "".join(c for c in n if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# 1. Abreviações e gírias de chat (chave já sem acento, em minúsculas)
# ---------------------------------------------------------------------------
ABBREVIATIONS = {
    "pq": "por que", "porq": "por que", "pqe": "por que",
    "vc": "você", "vcs": "vocês", "voce": "você", "cê": "você",
    "tb": "também", "tbm": "também", "tmb": "também",
    "oq": "o que", "oque": "o que", "q": "que", "qq": "qualquer",
    "qdo": "quando", "qnd": "quando", "quand": "quando",
    "hj": "hoje", "amanha": "amanhã", "dps": "depois", "agr": "agora",
    "hr": "hora", "hrs": "horas", "hs": "horas",
    "msm": "mesmo", "mto": "muito", "mt": "muito", "mta": "muita",
    "td": "tudo", "tds": "todos", "ngm": "ninguém", "alg": "algum",
    "cmo": "como", "cm": "como", "c": "com", "cmg": "comigo", "ctg": "contigo",
    "pfv": "por favor", "pf": "por favor", "pfvr": "por favor", "plmds": "por favor",
    "obg": "obrigado", "vlw": "obrigado", "blz": "beleza",
    "p": "para", "pra": "para", "pro": "para o", "pq?": "por que",
    "d": "de", "dq": "de que", "ne": "né",
    "hosp": "hospital", "farm": "farmácia", "unid": "unidade", "atend": "atendimento",
    "ps": "pronto socorro", "vac": "vacina", "cns": "Cartão Nacional de Saúde",
    "nº": "número", "n°": "número",
    "ola": "olá",
}

# Palavras coladas pelo teclado do celular
GLUED = {
    "cartaosus": "cartão sus", "cartaodosus": "cartão do sus", "cartaonacional": "cartão nacional",
    "upa24h": "upa 24h", "upa24": "upa 24h", "postodesaude": "posto de saúde",
    "unidadebasica": "unidade básica", "pronto-socorro": "pronto socorro",
}

# Vocabulário do domínio para corrigir erros de digitação (sem acento)
DOMAIN_VOCAB = [
    "vacina", "vacinas", "vacinacao", "vacinar", "unidade", "unidades", "basica", "saude",
    "farmacia", "hospital", "atendimento", "ambulancia", "medicamento", "medicamentos",
    "remedio", "remedios", "consulta", "gestante", "gravida", "idoso", "idosa", "crianca",
    "emergencia", "urgencia", "horario", "horarios", "endereco", "telefone", "documentos",
    "cartao", "agendamento", "agendar", "marcar", "exame", "exames", "cirurgia", "dengue",
    "gripe", "influenza", "sarampo", "febre", "amarela", "posto", "postinho", "regional",
    "ceilandia", "taguatinga", "samambaia", "sobradinho", "planaltina", "brazlandia",
    "gama", "guara", "santa", "maria", "recanto", "paranoa", "itapoa", "estrutural",
    "ouvidoria", "reclamacao", "mordeu", "mordida", "picada", "picou", "cachorro", "morcego",
    "escorpiao", "cobra", "aranha", "soro", "raiva", "pezinho", "prenatal", "puericultura",
    "pronto", "socorro", "samu", "mordido", "mordidos", "picado", "picada", "picados", "plantao", "funcionamento", "disponivel", "disponiveis",
    "psicologo", "psicologia", "psiquiatria", "tratamento", "doacao", "leite", "materno",
]
_VOCAB_SET = set(DOMAIN_VOCAB)
ACRONYMS = {
    "ubs", "upa", "sus", "samu", "hran", "hrt", "hrs", "hrg", "hrc", "hrsm", "hrp", "hrbz", "hrl", "hmib", "hub",
    "caps", "ceaf", "lme", "cns", "reme", "sisreg", "ses", "cta", "ist", "ists", "hiv", "aids", "df", "ra",
    "covid", "hpv", "bcg", "dtpa", "tríplice", "srag", "uti", "cpf", "rg",
}
_FUZZY_CUTOFF = 0.84
_FUZZY_MIN_LEN = 5


def _fuzzy(token: str) -> str:
    """Corrige um erro de digitação provável usando o vocabulário do domínio."""
    if len(token) < _FUZZY_MIN_LEN or token in _VOCAB_SET or token.rstrip("s") in _VOCAB_SET:
        return token
    if not token.isalpha():
        return token
    best = difflib.get_close_matches(token, DOMAIN_VOCAB, n=1, cutoff=_FUZZY_CUTOFF)
    return best[0] if best else token


# Escrita sem acento é comum no celular, mas os documentos oficiais e o modelo de embeddings
# são sensíveis a ela ("cartao" afasta a busca de "cartão"). Restaura a acentuação do vocabulário do domínio.
DIACRITICS = {w: a for w, a in {
    "cartao": "cartão", "saude": "saúde", "farmacia": "farmácia", "farmacias": "farmácias", "basica": "básica",
    "medico": "médico", "medica": "médica", "medicos": "médicos", "vacinacao": "vacinação", "ambulancia": "ambulância",
    "emergencia": "emergência", "urgencia": "urgência", "endereco": "endereço", "horario": "horário",
    "horarios": "horários", "gravida": "grávida", "crianca": "criança", "criancas": "crianças", "atencao": "atenção",
    "remedio": "remédio", "remedios": "remédios", "pre-natal": "pré-natal", "prenatal": "pré-natal",
    "reclamacao": "reclamação", "informacao": "informação", "informacoes": "informações", "regulacao": "regulação",
    "ceilandia": "Ceilândia", "aguas": "Águas", "brazlandia": "Brazlândia", "guara": "Guará", "paranoa": "Paranoá",
    "itapoa": "Itapoã", "sao": "São", "sebastiao": "Sebastião", "nucleo": "Núcleo", "jardim botanico": "Jardim Botânico",
    "escorpiao": "escorpião", "peconhento": "peçonhento", "peconhentos": "peçonhentos", "onibus": "ônibus",
    "disponivel": "disponível", "disponiveis": "disponíveis", "doacao": "doação", "psicologica": "psicológica",
    "psicologo": "psicólogo", "obrigatorio": "obrigatório", "comprovante": "comprovante", "residencia": "residência",
    "acolhimento": "acolhimento", "pediatria": "pediatria", "ginecologia": "ginecologia", "hospitais": "hospitais",
    "sabado": "sábado", "domingo": "domingo", "proximo": "próximo", "proxima": "próxima", "numero": "número",
    "consultorio": "consultório", "consultorios": "consultórios", "secretaria": "secretaria", "unica": "única",
    "hidratacao": "hidratação", "vacinacao": "vacinação", "internacao": "internação", "orientacao": "orientação",
    "tambem": "também", "ja": "já", "la": "lá", "nao": "não", "voce": "você", "esta": "está", "sao": "são",
}.items() if w != a}
# palavras que são válidas sem acento em outro sentido ("esta", "la", "ja", "sao") ficam de fora
for _amb in ("esta", "la", "ja", "sao", "nao", "voce", "tambem"):
    DIACRITICS.pop(_amb, None)

_REPEAT = re.compile(r"(.)\1{2,}")
_TOKEN = re.compile(r"[A-Za-zÀ-ÿ0-9ºª°]+|[^\sA-Za-zÀ-ÿ0-9ºª°]+|\s+")


def squeeze_repeats(text: str) -> str:
    """'socorrooooo' -> 'socorro'; '???' -> '?' (≥3 repetições viram 1)."""
    return _REPEAT.sub(r"\1", text)


def normalize_informal(text: str) -> str:
    """Expande abreviações, junta/separa palavras coladas, tira alongamentos e corrige erros de digitação."""
    s = squeeze_repeats(text.strip())
    out: List[str] = []
    for tok in _TOKEN.findall(s):
        if not tok.strip() or not any(c.isalnum() for c in tok):
            out.append(tok)
            continue
        key = fold(tok)
        if key in GLUED:
            out.append(GLUED[key])
        elif key in ABBREVIATIONS:
            out.append(ABBREVIATIONS[key])
        elif tok.isupper() and len(tok) >= 3 and key not in ACRONYMS:
            # CAIXA ALTA gritada vira minúscula; siglas conhecidas (UBS, UPA, HRAN...) ficam
            out.append(_fuzzy(key) if key not in _VOCAB_SET else tok.lower())
        else:
            fixed = _fuzzy(key)
            if fixed in DIACRITICS and (fixed != key or tok == key):
                fixed = DIACRITICS[fixed]
            out.append(tok if fixed == key else fixed)
    joined = "".join(out)
    # "p sul" / "p norte" são nomes de setores de Ceilândia, não "para"
    return re.sub(r"\bpara (sul|norte)\b", r"p \1", joined)


# ---------------------------------------------------------------------------
# 2. Urgência
# ---------------------------------------------------------------------------
# Sinais fortes: bastam para tratar como urgência de saúde
_STRONG_URGENCY = re.compile(
    r"\b(ambulancia|samu|192|desmai\w+|sangrand\w+|hemorragia|convuls\w+|afogand\w+|engasg\w+|"
    r"infart\w+|avc|derrame|parou de respirar|nao (esta )?respirando|nao consegue respirar|"
    r"inconsciente|overdose|atropel\w+|queimad\w+ grave|emergencia)\b"
)
# Sinais fracos: só contam junto de contexto de saúde
_WEAK_URGENCY = re.compile(r"\b(socorro|urgente|urgencia|help|ajuda|rapido|agora|imediat\w+|acidente(?! com animal))\b")
_HEALTH_CONTEXT = re.compile(
    r"\b(mord\w+|pic(ou|ada|ado)|ferid\w+|machuc\w+|doente|doendo|dor|sangue|hospital|upa|pronto socorro|"
    r"atendimento|medico|enfermeir\w+|saude|filho|filha|mae|pai|bebe|crianca|idos[oa]|gravida|"
    r"cobra|escorpiao|aranha|cachorro|gato|morcego|veneno|queimou|caiu|bateu|pista|transito|"
    r"ambulancia|vacina)\b"
)

URGENCY_EXPANSION = "urgência emergência SAMU 192 UPA 24 horas pronto-socorro"


_SPECIFIC_TOPIC = re.compile(r"animal pe[cç]onhento|risco de raiva")


def add_urgency_terms(expanded: str, original: str) -> str:
    """Acrescenta SAMU/UPA quando o texto é uma urgência e nenhum tema mais específico (animais, raiva) já foi resolvido."""
    f = fold(expanded)
    if "samu 192" in f or _SPECIFIC_TOPIC.search(f) or not detect_urgency(original):
        return expanded
    return f"{expanded} {URGENCY_EXPANSION}"


def detect_urgency(text: str) -> bool:
    f = fold(squeeze_repeats(text))
    if _STRONG_URGENCY.search(f):
        return True
    return bool(_WEAK_URGENCY.search(f) and _HEALTH_CONTEXT.search(f))


# ---------------------------------------------------------------------------
# 3. Vocabulário popular -> termos do corpus oficial
#    (gatilho, expansão, marcador de idempotência). A expansão é ANEXADA e a palavra
#    original continua na consulta, o que ajuda a busca vetorial e a lexical.
# ---------------------------------------------------------------------------
_BITE = r"(mord\w+|arranh\w+|ataca\w+|lambeu|lambeu)"
_PET = r"(cachorr\w+|cao|caes|cachorrinh\w+|gat[oa]s?|gatinh\w+|morceg\w+|macac\w+|raposa|sagui|animal|animais|bicho)"

CONTEXT_RULES: List[Tuple[re.Pattern, str, str]] = [
    # Mordedura/arranhão por mamíferos: o corpus fala em "risco de raiva", HRAN/HRT e soro/vacina antirrábica
    (re.compile(rf"\b{_PET}\b.*\b{_BITE}\b|\b{_BITE}\b.*\b{_PET}\b|\bmordedura\b|\braiva\b|\bantirrab\w+\b"),
     "acidente com animal mordedura risco de raiva soro antirrábico HRAN HRT", "risco de raiva|animal peçonhento"),
    # Peçonhentos
    (re.compile(r"\b(cobras?|serpentes?|jararacas?|cascav[eé]is|cascavel|surucucu)\b"),
     "acidente com animal peçonhento soro antiofídico HRAN HRT", "animal peçonhento"),
    (re.compile(r"\bescorpi(ao|oes)\b"),
     "acidente com animal peçonhento soro antiescorpiônico HRAN HRT", "animal peçonhento"),
    (re.compile(r"\baranhas?\b"), "acidente com animal peçonhento HRAN HRT", "animal peçonhento"),
    # Serviços
    (re.compile(r"\b(ambulancia|chamar (o )?samu|telefone do samu|numero do samu)\b"),
     "SAMU 192 serviço de atendimento móvel de urgência", "samu 192"),
    (re.compile(r"\b(reclam\w+|denunci\w+|elogi\w+|ouvidor\w*)\b.*\b(atendimento|posto|ubs|hospital|upa|medico|saude)\b|\b(atendimento|posto|ubs|hospital|upa|medico)\b.*\b(reclam\w+|denunci\w+)\b"),
     "Ouvidoria SES-DF 162 registrar reclamação", "ouvidoria ses-df"),
    (re.compile(r"\b(vaga|fila|lista de espera|marcar|agendar)\b.*\bcirurgi\w+\b|\bcirurgi\w+\b.*\b(vaga|fila|lista de espera|espera)\b"),
     "regulação cirurgia eletiva SISREG lista de espera", "regulação cirurgia"),
    (re.compile(r"\b(doar|doacao|doador\w*)\b.*\bleite\b|\bleite materno\b.*\b(doar|doacao)\b"),
     "Banco de Leite Humano posto de coleta doação de leite materno", "banco de leite"),
    (re.compile(r"\b(tir\w+|faz\w*|emit\w+|consegu\w+|ped\w+|segunda via|perdi|perdeu|novo)\b.*\bcartao (do )?sus\b|\bcartao (do )?sus\b.*\b(tir\w+|faz\w*|emit\w+|como|novo|perdi|perdeu|segunda via)\b"),
     "emitir Cartão Nacional de Saúde CNS cadastro na UBS", "cartão nacional de saúde"),
    (re.compile(r"\b(exame|teste|testagem)\b.*\b(hiv|aids|sifilis|ist)\b|\b(hiv|aids|sifilis)\b.*\b(exame|teste|testagem)\b"),
     "testagem de HIV e ISTs doenças infecciosas CTA UBS", "testagem de hiv"),
    (re.compile(r"\b(psicolog\w+|psiquiatr\w+|saude mental|ansiedade|depress\w+)\b.*\b(gratis|sus|atendimento|onde)\b"),
     "CAPS Centro de Atenção Psicossocial saúde mental atendimento no SUS", "caps centro"),
    (re.compile(r"\bremedio (caro|de alto custo|do governo)\b|\balto custo\b"),
     "Farmácia de Alto Custo CEAF LME medicamento especializado", "farmácia de alto custo"),
    (re.compile(r"\b(whats\w*|zap|internet|online|app|aplicativo)\b.*\b(marcar|agendar|consulta)\b|\b(marcar|agendar)\b.*\b(whats\w*|zap|internet|online)\b"),
     "agendamento de consulta na UBS acolhimento Saúde Digital DF", "agendamento de consulta"),
]

# Exclusões: "cobra de brinquedo", "aranha-homem"...
_NOT_ANIMAL_BITE = re.compile(r"\b(brinquedo|pelucia|loja|comprar|filme|serie|jogo|desenho|tatuagem|homem|fantasia)\b")


def _already(expansion_marker: str, text_fold: str) -> bool:
    return any(fold(m) in text_fold for m in expansion_marker.split("|"))


def apply_context_rules(text: str) -> str:
    """Anexa ao final os termos oficiais correspondentes ao vocabulário popular detectado."""
    f = fold(text)
    extra: List[str] = []
    for pat, expansion, marker in CONTEXT_RULES:
        if not pat.search(f) or _already(marker, f):
            continue
        if "peçonhento" in marker and _NOT_ANIMAL_BITE.search(f):
            continue
        extra.append(expansion)
    return f"{text} {' '.join(extra)}".strip() if extra else text


def context_expansions(text: str) -> List[str]:
    """Expansões oficiais que o vocabulário popular do texto aciona (para uma busca focada, sem o ruído da pergunta)."""
    f = fold(text)
    out: List[str] = []
    for pat, expansion, _marker in CONTEXT_RULES:
        if pat.search(f) and not ("peçonhento" in expansion and _NOT_ANIMAL_BITE.search(f)):
            out.append(expansion)
    return out


def normalize_query(text: str) -> str:
    """Pipeline completo: informal -> vocabulário popular -> urgência."""
    s = normalize_informal(text)
    s = apply_context_rules(s)
    return add_urgency_terms(s, text)


# ---------------------------------------------------------------------------
# 4. Fora do domínio: o embedding aproxima "socorro meu celular quebrou" do SAMU e
#    "receita de bolo" da lista de medicamentos. Um sinal explícito de outro assunto,
#    sem nenhum contexto de saúde, encerra a busca antes dela.
# ---------------------------------------------------------------------------
_OFF_TOPIC = re.compile(
    r"\b(celular|iphone|android|notebook|computador|wi-?fi|bolo|receita de (bolo|comida|torta|pao)|futebol|"
    r"flamengo|palmeiras|corinthians|jogo do|campeonato|previsao do tempo|vai chover|imposto de renda|"
    r"detran|cnh|carteira de motorista|cartorio|registro civil|certidao de (nascimento|casamento|obito)|"
    r"loteria|bitcoin|criptomoeda|emprestimo|financiamento|filme|novela|serie|musica|show|passagem aerea|"
    r"senha|pix|boleto|cartao de credito|conta (bancaria|corrente)|nubank|caixa economica|banco do brasil|matematica|dever de casa|redacao|horoscopo|signo|brinquedo|pelucia|ceu e azul)\b"
)
_HEALTH_ANCHOR = re.compile(
    r"\b(saude|ubs|upa|hospital|medic\w+|remedio\w*|vacin\w+|samu|ambulancia|doenc\w+|dengue|gripe|exame\w*|"
    r"consulta|enfermeir\w+|posto de saude|postinho|farmacia|gestante|gravida|pre.?natal|sus|cartao sus|"
    r"atendimento (medico|de saude)|ses-?df|caps|mordeu|picou|ferimento|sintoma\w*)\b"
)


_HEALTH_EXTRA = re.compile(
    r"\b(soro|antiof\w+|antirrab\w+|peconhent\w+|droga\w*|bebida|alcool\w*|vicio|psic\w+|ansiedade|depress\w+|"
    r"dor|doen\w+|ferid\w*|sangue|pressao|diabetes|gravidez|parto|cirurgia|dente|dentista|odonto\w+|hiv|raiva|"
    r"animal|animais|tratamento|vacin\w+|hran|hrt|caps|leite|pezinho|medic\w+)\b"
)
# Vocabulário de serviços de saúde do DF: a pergunta do cidadão (ou a conversa anterior) precisa de pelo
# menos um destes sinais para chegar à busca. Evidência positiva, não uma lista de assuntos proibidos.
_SERVICE_SIGNAL = re.compile(
    r"\b(unidade\w*|posto\w*|regional|regionais|atendimento|atender|atendid\w+|agend\w+|marcar|marcacao|consulta\w*|consultorio\w*|exame\w*|"
    r"cartao|cns|ouvidoria|regulacao|sisreg|policlinica\w*|maternidade|laboratorio|farmac\w+|clinica\w*|especialidade\w*|"
    r"idos[oa]\w*|crianca\w*|bebe|recem|nascid\w+|filh[oa]|paciente|enfermagem|odonto\w*|fisioterapia|cirurgi\w+|"
    r"pre.?natal|puericultura|amamenta\w+|banco de leite|hemocentro|doacao de sangue|testagem|ist|hiv|sifilis|"
    r"covid|sarampo|hpv|febre amarela|influenza|vacinac\w+|imuniza\w+|calendario vacinal|saude na hora|"
    r"hospital|hospitais|hmib|hbdf|hub|samu|upa|ubs|caps|ceaf|lme|reme|alto custo|medicamento\w*|remedio\w*)\b"
)
_STRONG_WEAK = re.compile(r"\b(socorro|urgente|urgencia|emergencia|help|ajuda)\b")


def looks_off_topic(text: str) -> bool:
    f = fold(text)
    has_signal = bool(
        _HEALTH_ANCHOR.search(f) or _HEALTH_CONTEXT.search(f) or _HEALTH_EXTRA.search(f) or _SERVICE_SIGNAL.search(f)
    )
    if has_signal:
        return False
    if _OFF_TOPIC.search(f):
        return True
    n_words = len(re.findall(r"[a-z0-9]+", f))
    if not _STRONG_WEAK.search(f) and n_words >= 4:
        # sem nenhum termo de serviço ou saúde: o embedding aproxima qualquer "horário" ou "onde fica" dos documentos
        return True
    # "socorro meu carro quebrou": palavra de urgência, frase longa e nenhum termo de saúde.
    # Frases curtas ("socorro", "preciso de ajuda urgente") seguem para a resposta de emergência.
    return bool(_STRONG_WEAK.search(f)) and len(re.findall(r"[a-z0-9]+", f)) >= 5
