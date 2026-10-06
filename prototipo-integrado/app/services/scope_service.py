import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class ScopeDecision:
    scope: str
    intent: str


class ScopeService:
    IN_SCOPE_TERMS = (
        "sus", "ubs", "upa", "hospital", "caps", "vacina", "imuniza", "medicamento",
        "remedio", "farmacia", "encaminhamento", "regulacao", "consulta", "saude",
        "atendimento", "unidade", "posto", "samu", "emergencia", "urgencia",
        "cartao sus", "cns", "hiv", "ist", "aids", "transmitido", "transmissao",
        "contagio", "prevencao", "doenca", "doencas", "sintoma", "sintomas",
        "infeccao", "tratamento", "exame", "testagem", "preservativo", "camisinha",
        "dengue", "gripe",
    )
    CLINICAL_PATTERNS = (
        r"qual doença eu tenho",
        r"qual doenca eu tenho",
        r"meu diagnostico",
        r"meu diagnóstico",
        r"faça meu diagnostico",
        r"faca meu diagnostico",
        r"qual remedio devo tomar",
        r"qual remédio devo tomar",
        r"qual dose devo tomar",
        r"o que eu tenho",
        r"qual tratamento devo",
        r"qual tratamento eu devo",
        r"qual medicamento.*para meus sintomas",
    )
    RA_ALIASES = {
        "samambaia": "Samambaia",
        "ceilandia": "Ceilândia",
        "ceilândia": "Ceilândia",
        "taguatinga": "Taguatinga",
        "plano piloto": "Plano Piloto",
        "planopiloto": "Plano Piloto",
        "gama": "Gama",
        "recanto das emas": "Recanto das Emas",
        "recanto": "Recanto das Emas",
        "sobradinho": "Sobradinho",
        "guara": "Guará",
        "guará": "Guará",
        "santa maria": "Santa Maria",
        "paranoa": "Paranoá",
        "paranoá": "Paranoá",
        "brazlandia": "Brazlândia",
        "brazlândia": "Brazlândia",
    }

    def normalize(self, value: str) -> str:
        value = unicodedata.normalize("NFD", value.lower())
        value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
        return re.sub(r"\s+", " ", value).strip()

    def extract_ra(self, message: str) -> str | None:
        normalized = self.normalize(message)
        for alias, canonical in sorted(self.RA_ALIASES.items(), key=lambda pair: -len(pair[0])):
            if alias in normalized:
                return canonical
        return None

    def classify(self, message: str, previous_intent: str | None = None) -> ScopeDecision:
        normalized = self.normalize(message)

        if any(re.search(pattern, normalized) for pattern in self.CLINICAL_PATTERNS):
            return ScopeDecision("out_of_scope", "clinical")

        if normalized in {"e no sabado", "e no sábado", "e domingo", "e segunda", "e la", "e ai"}:
            if previous_intent:
                return ScopeDecision("in_scope", previous_intent)
            return ScopeDecision("needs_clarification", "unknown")

        if any(re.search(rf"\b{re.escape(term)}\b", normalized) for term in self.IN_SCOPE_TERMS):
            if any(term in normalized for term in ("vacina", "vacinacao", "imuniza")):
                return ScopeDecision("in_scope", "vaccination")
            if any(term in normalized for term in ("ubs", "upa", "hospital", "caps", "posto de saude", "posto")):
                if any(term in normalized for term in ("servico", "oferece", "atende")):
                    return ScopeDecision("in_scope", "unit_services")
                return ScopeDecision("in_scope", "unit_search")
            if any(term in normalized for term in ("medicamento", "remedio", "farmacia")):
                return ScopeDecision("in_scope", "medication_service")
            if any(term in normalized for term in ("encaminhamento", "regulacao")):
                return ScopeDecision("in_scope", "referral")
            if "consulta" in normalized:
                return ScopeDecision("in_scope", "consultation")
            return ScopeDecision("in_scope", "sus_information")

        if previous_intent:
            return ScopeDecision("in_scope", previous_intent)

        return ScopeDecision("needs_clarification", "unknown")
