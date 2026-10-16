"""
Natural Language Inferencer (NLU) — Motor de Inferência Léxica e Semântica para o SUS-DF.
Executa em tempo ultrarrápido (< 2ms) sem dependências externas nem chamadas de rede.
Realiza:
1. Classificação de Intenção do Cidadão
2. Extração Geográfica das 33 Regiões Administrativas do DF e seus setores
3. Identificação de Persona / Demografia (Idoso, Gestante, Recém-Nascido, Criança)
4. Geração de Filtros Estruturados para Busca Vetorial no ChromaDB
5. Query Expansion / Reformulação Semântica Otimizada
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Mapeamento Geográfico das 33 Regiões Administrativas do DF
# ---------------------------------------------------------------------------
RA_DICTIONARY: List[Tuple[str, List[str]]] = [
    ("ceilandia", [
        "ceilandia", "ceilândia", "p sul", "p norte", "setor o", "m norte",
        "qnm", "qnn", "qno", "qnp", "guariroba", "expansao do setor o"
    ]),
    ("taguatinga", [
        "taguatinga", "taguatinga norte", "taguatinga sul", "taguatinga centro",
        "qna", "qnb", "qnc", "qnd", "qne", "qnf", "qng", "qnh", "qnj", "qnl",
        "pistao sul", "pistao norte", "sandu"
    ]),
    ("samambaia", [
        "samambaia", "samambaia norte", "samambaia sul", "qn", "qs", "qr"
    ]),
    ("plano_piloto", [
        "plano piloto", "asa sul", "asa norte",
        "vila planalto", "vila telebrasilia", "vila telebrasília", "w3 sul",
        "w3 norte", "l2 sul", "l2 norte", "sgas", "sqs", "sqn", "sgan"
    ]),
    ("gama", [
        "gama", "setor sul gama", "setor leste gama", "setor oeste gama",
        "setor central gama", "setor norte gama", "ponte alta", "dvo"
    ]),
    ("guara", [
        "guara", "guará", "guara i", "guara ii", "guara 1", "guara 2", "qe", "qi"
    ]),
    ("sobradinho_ii", [
        "sobradinho ii", "sobradinho 2", "ar 13", "ar 02"
    ]),
    ("sobradinho", [
        "sobradinho", "sobradinho i", "sobradinho 1", "grande colorado"
    ]),
    ("planaltina", [
        "planaltina", "arapoanga", "araponga", "vale do amanhecer", "jardim roriz", "estancia"
    ]),
    ("santa_maria", [
        "santa maria", "santa maria norte", "santa maria sul", "porto rico", "total ville"
    ]),
    ("sao_sebastiao", [
        "sao sebastiao", "são sebastião", "vila nova", "crixa", "crixá", "morro da cruz", "bonsucesso"
    ]),
    ("recanto_das_emas", [
        "recanto das emas", "recanto"
    ]),
    ("paranoa", [
        "paranoa", "paranoá", "paranoa parque", "fazenda paranoa"
    ]),
    ("nucleo_bandeirante", [
        "nucleo bandeirante", "núcleo bandeirante", "metropolitana", "vila cauhy", "divineia", "divinéia"
    ]),
    ("brazlandia", [
        "brazlandia", "brazlândia", "incra 8", "vila sao jose", "vila são josé"
    ]),
    ("riacho_fundo_ii", [
        "riacho fundo ii", "riacho fundo 2", "caub"
    ]),
    ("riacho_fundo", [
        "riacho fundo", "riacho fundo i", "riacho fundo 1", "kanegae"
    ]),
    ("cruzeiro", [
        "cruzeiro", "cruzeiro velho", "cruzeiro novo", "sres", "shces"
    ]),
    ("aguas_claras", [
        "aguas claras", "águas claras", "areal"
    ]),
    ("vicente_pires", [
        "vicente pires", "shvp", "rua 3 vicente pires", "rua 4 vicente pires", "rua 12 vicente pires", "colonia agricola samambaia"
    ]),
    ("scia_estrutural", [
        "estrutural", "scia", "santa luzia"
    ]),
    ("sol_nascente_por_do_sol", [
        "sol nascente", "por do sol", "pôr do sol"
    ]),
    ("itapoa", [
        "itapoa", "itapoã", "del lago", "fascal"
    ]),
    ("lago_sul", [
        "lago sul", "shis"
    ]),
    ("lago_norte", [
        "lago norte", "shin", "taquari"
    ]),
    ("candangolandia", [
        "candangolandia", "candangolândia", "qro"
    ]),
    ("sudoeste_octogonal", [
        "sudoeste", "octogonal", "ccsw", "qmsw"
    ]),
    ("varjao", [
        "varjao", "varjão"
    ]),
    ("park_way", [
        "park way", "smpw"
    ]),
    ("jardim_botanico", [
        "jardim botanico", "jardim botânico", "mangueiral", "san diego", "altiplano leste"
    ]),
    ("sia", [
        "sia", "setor de transporte de cargas"
    ]),
    ("fercal", [
        "fercal", "engenho velho", "lages"
    ]),
    ("arniqueira", [
        "arniqueira", "sha", "vereda da cruz"
    ]),
]


def _is_user_item(item: Any) -> bool:
    """Verifica com segurança se o item do histórico de conversa pertence ao usuário."""
    if hasattr(item, "is_user") and callable(getattr(item, "is_user")):
        return bool(item.is_user())
    if isinstance(item, dict):
        if "isUser" in item and item["isUser"] is not None:
            return bool(item["isUser"])
        if "role" in item and item["role"] is not None:
            return str(item["role"]).lower() in ("user", "human", "citizen")
    return True


def _get_item_text(item: Any) -> str:
    """Extrai o texto da mensagem do histórico de forma uniforme."""
    if hasattr(item, "get_text") and callable(getattr(item, "get_text")):
        return str(item.get_text())
    if isinstance(item, dict):
        return str(item.get("text") or item.get("content") or "")
    return str(item)


@dataclass
class NLUInferenceResult:
    original_query: str
    normalized_query: str
    expanded_query: str
    intent: str
    cluster: str
    ra: str
    ra_display: str
    persona: str
    metadata_filter: Optional[Dict[str, Any]] = None
    keywords: List[str] = field(default_factory=list)


class NaturalLanguageInferencer:
    """Motor de NLU de alta performance para o SUS-DF."""

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Remove acentuação e converte para minúsculas."""
        normalized = unicodedata.normalize("NFKD", text).casefold()
        return "".join(char for char in normalized if not unicodedata.combining(char)).strip()

    @classmethod
    def extract_ra(cls, normalized_text: str) -> Tuple[str, str]:
        """Identifica a Região Administrativa a partir do texto normalizado."""
        for ra_id, aliases in RA_DICTIONARY:
            for alias in aliases:
                # Busca por limites de palavra
                pattern = rf"\b{re.escape(alias)}\b"
                if re.search(pattern, normalized_text):
                    # Formatar nome display amigável
                    display = ra_id.replace("_", " ").title()
                    if display.lower() == "plano piloto":
                        display = "Plano Piloto"
                    elif "sol_nascente" in ra_id:
                        display = "Sol Nascente / Pôr do Sol"
                    elif "ii" in ra_id:
                        display = display.replace("Ii", "II")
                    return ra_id, display
        return "geral_df", "Distrito Federal (Geral)"

    @classmethod
    def extract_persona(cls, normalized_text: str) -> str:
        """Identifica a persona ou grupo prioritário."""
        if any(w in normalized_text for w in ["idoso", "idosa", "terceira idade", "vovo", "vovó", "vovô", "aposentado", "60 anos", "melhor idade"]):
            return "idoso"
        if any(w in normalized_text for w in ["gravida", "gestante", "gravidez", "pre natal", "prenatal", "parto", "gestacao"]):
            return "gestante"
        if any(w in normalized_text for w in ["recem nascido", "recem-nascido", "pezinho", "teste do pezinho", "bebe", "bebê", "nenem", "neném", "dias de vida"]):
            return "recem_nascido"
        if any(w in normalized_text for w in ["crianca", "criança", "criancas", "crianças", "infantil", "infantis", "puericultura", "meu filho", "minha filha", "pediatra", "pediatria"]):
            return "crianca"
        return "geral"

    @classmethod
    def extract_intent_and_cluster(cls, normalized_text: str, persona: str) -> Tuple[str, str]:
        """Classifica a intenção primária e o cluster correspondente."""
        # 0. Acidentes com animais (mordedura, peçonhentos): urgência, mesmo que o texto cite "vacina/soro"
        if any(w in normalized_text for w in ["risco de raiva", "animal peconhento", "mordedura", "picada"]):
            return "URGENCIA_SINTOMAS", "urgencia_emergencia"

        # 0b. Doação de leite materno (Banco de Leite Humano): não é pré-natal nem puericultura
        if "banco de leite" in normalized_text or "doar leite" in normalized_text or "doacao de leite" in normalized_text or "coleta de leite" in normalized_text or "leite humano" in normalized_text:
            return "BANCO_DE_LEITE", "saude_materno_infantil"

        # 1. Vacinação
        if any(w in normalized_text for w in ["vacina", "vacinacao", "vacinar", "imunizacao", "gotinha", "doses", "calendario vacinal"]):
            return "VACINACAO", "vacinacao"

        # 2. Saúde Materno-Infantil (Pré-Natal, Puericultura, Teste do Pezinho)
        if any(w in normalized_text for w in ["pre natal", "prenatal", "puericultura", "teste do pezinho", "amamentacao", "leite materno"]) or (
            persona in ("gestante", "recem_nascido") and not any(w in normalized_text for w in ["remedio", "medicamento", "horario"])
        ):
            return "PRE_NATAL_PUERICULTURA", "saude_materno_infantil"

        # 3. Medicamentos e Farmácia
        if any(w in normalized_text for w in ["remedio", "remedios", "medicamento", "medicamentos", "farmacia", "pegar remedio", "retirar remedio", "receita", "lme", "alto custo"]):
            return "MEDICAMENTOS_FARMACIA", "medicamentos_farmacia"

        # 4. Urgência e Sintomas Graves / Dengue
        if any(w in normalized_text for w in ["urgencia", "emergencia", "upa", "pronto socorro", "samu", "192", "socorro", "ambulancia", "urgente", "acidente", "dor no peito", "falta de ar", "desmaio", "convulsao", "dengue", "febre alta", "alerta"]):
            return "URGENCIA_SINTOMAS", "urgencia_emergencia"

        # 5. Horário de Funcionamento
        if any(w in normalized_text for w in ["horario", "horarios", "que horas", "abre", "fecha", "funciona sabado", "saude na hora", "a noite", "plantao"]):
            return "HORARIO_FUNCIONAMENTO", "atencao_primaria"

        # 6. Documentos e Requisitos
        if any(w in normalized_text for w in ["documento", "documentos", "levar", "precisa levar", "cartao sus", "cns", "comprovante"]):
            return "DOCUMENTOS_REQUISITOS", "atencao_primaria"

        # 7. Localizar Unidade / Posto de Saúde (Default de Atenção Básica)
        return "LOCALIZAR_UNIDADE", "atencao_primaria"

    @classmethod
    def infer(cls, query: str, history: Optional[Sequence[Any]] = None) -> NLUInferenceResult:
        """Executa a inferência completa de NLU sobre a pergunta do usuário."""
        from app.rag.conversation import expand_popular_terms  # idempotente: o roteador já envia o texto normalizado

        query = expand_popular_terms(query)
        norm_query = cls.normalize_text(query)

        # 1. Extração Geográfica
        ra_id, ra_display = cls.extract_ra(norm_query)

        # Se não achou na pergunta atual, mas há histórico, verifica o histórico (somente mensagens do usuário para evitar bot poisoning)
        if ra_id == "geral_df" and history:
            for item in reversed(history):
                if not _is_user_item(item):
                    continue
                text = _get_item_text(item)
                hist_ra_id, hist_ra_disp = cls.extract_ra(cls.normalize_text(text))
                if hist_ra_id != "geral_df":
                    ra_id, ra_display = hist_ra_id, hist_ra_disp
                    break

        # 2. Extração de Persona
        persona = cls.extract_persona(norm_query)
        if persona == "geral" and history:
            for item in reversed(history):
                if not _is_user_item(item):
                    continue
                text = _get_item_text(item)
                hist_persona = cls.extract_persona(cls.normalize_text(text))
                if hist_persona != "geral":
                    persona = hist_persona
                    break

        # 3. Classificação de Intenção e Cluster
        intent, cluster = cls.extract_intent_and_cluster(norm_query, persona)

        # 4. Construção do Filtro Estruturado de Metadados para o ChromaDB (Filtro Híbrido com geral_df)
        metadata_filter: Optional[Dict[str, Any]] = None
        if ra_id != "geral_df":
            metadata_filter = {"$or": [{"ra": ra_id}, {"ra": "geral_df"}]}

        # 5. Query Expansion / Reformulação Semântica
        expansion_terms = []
        if ra_id != "geral_df":
            expansion_terms.append(f"{ra_display} DF")
        
        if intent == "VACINACAO":
            expansion_terms.extend(["sala de vacina", "vacinação de rotina", "calendário"])
            if persona == "idoso":
                expansion_terms.extend(["idosos", "gripe influenza", "pneumocócica"])
            elif persona == "gestante":
                expansion_terms.extend(["gestante", "dtpa", "influenza"])
            elif persona in ("recem_nascido", "crianca"):
                expansion_terms.extend(["infantil", "criança", "bebê", "gotinha"])
        elif intent == "PRE_NATAL_PUERICULTURA":
            expansion_terms.extend(["pré-natal gestante", "puericultura criança", "teste do pezinho recém-nascido"])
        elif intent == "MEDICAMENTOS_FARMACIA":
            expansion_terms.extend(["farmácia da UBS", "dispensação de medicamentos básicos", "reme-df"])
        elif intent == "URGENCIA_SINTOMAS":
            if any(w in norm_query for w in ["risco de raiva", "animal peconhento"]):
                pass  # a normalização popular já acrescentou o vocabulário oficial
            elif any(w in norm_query for w in ["samu", "192", "socorro", "ambulancia"]):
                expansion_terms.extend(["SAMU 192 serviço de atendimento móvel de urgência ambulância socorro"])
            else:
                expansion_terms.extend(["UPA 24 horas", "urgência e emergência", "hospital regional"])
        elif intent == "HORARIO_FUNCIONAMENTO":
            expansion_terms.extend(["horário de atendimento", "saúde na hora até 22h", "segunda a sexta"])

        expanded_query = f"{query} {' '.join(expansion_terms)}".strip()

        return NLUInferenceResult(
            original_query=query,
            normalized_query=norm_query,
            expanded_query=expanded_query,
            intent=intent,
            cluster=cluster,
            ra=ra_id,
            ra_display=ra_display,
            persona=persona,
            metadata_filter=metadata_filter,
            keywords=expansion_terms,
        )
