import re


class ScopeService:
    IN_SCOPE_TERMS = (
        "sus", "ubs", "upa", "hospital", "caps", "vacina", "vacinação",
        "medicamento", "farmácia", "encaminhamento", "regulação", "consulta",
        "saúde", "atendimento",
    )
    CLINICAL_TERMS = (
        "qual doença eu tenho", "meu diagnóstico", "faça meu diagnóstico",
        "qual remédio devo tomar", "qual dose devo tomar", "o que eu tenho",
    )

    def classify(self, message: str) -> tuple[str, str]:
        normalized = re.sub(r"\s+", " ", message.lower()).strip()
        if any(term in normalized for term in self.CLINICAL_TERMS):
            return "out_of_scope", "clinical"
        if any(term in normalized for term in self.IN_SCOPE_TERMS):
            if any(term in normalized for term in ("vacina", "vacinação")):
                return "in_scope", "vaccination"
            if any(term in normalized for term in ("ubs", "upa", "hospital", "caps")):
                return "in_scope", "unit_search"
            if "medicamento" in normalized or "farmácia" in normalized:
                return "in_scope", "medication_service"
            if "encaminhamento" in normalized or "regulação" in normalized:
                return "in_scope", "referral"
            return "in_scope", "sus_information"
        return "needs_clarification", "unknown"
