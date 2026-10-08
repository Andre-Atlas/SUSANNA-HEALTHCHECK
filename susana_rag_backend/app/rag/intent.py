"""
Intent Router — Resolve a intenção e a ambiguidade antes do RAG.
Roda em milissegundos usando heurísticas estruturadas (sem LLM).
"""
import re

# Padrões que indicam perguntas genéricas demais sobre entidades vastas
VAGUE_PROGRAM_PATTERN = re.compile(r"^(o que (é|são) )?(o|os) programas? do (sus|governo)", re.I)

class IntentRouter:
    @staticmethod
    def classify(message: str, has_history: bool = False) -> str:
        """
        Retorna o tipo de intenção:
        - 'VAGUE_PROGRAM': A pergunta é muito ampla e precisa de clarificação.
        - 'NEEDS_HISTORY': A pergunta é muito curta e provável dependente de contexto.
        - 'SPECIFIC': A pergunta parece boa para ir para o RAG.
        """
        msg_clean = message.strip().lower()
        word_count = len(msg_clean.split())

        # 1. Checa ambiguidade direta
        if VAGUE_PROGRAM_PATTERN.search(msg_clean):
            return "VAGUE_PROGRAM"

        # 3. Checa dependência de histórico (se muito curta e sem palavras fortes)
        # Ex: "me explique melhor", "como assim", "sim", "não"
        if word_count <= 4 and has_history:
            return "NEEDS_HISTORY"
            
        # 4. Checa pedido de localização relativa ("perto de mim")
        if any(term in msg_clean for term in ["perto de mim", "onde estou", "mais próxim", "mais perto", "minha casa"]):
            return "NEEDS_LOCATION"
            
        # Para saudações ou mensagens curtíssimas sem contexto (ex: "tudo bem?")
        if word_count <= 3 and not has_history:
             if msg_clean not in ["sus", "upas", "vacinas", "samu", "ajuda"]:
                 return "GREETING_OR_TOO_SHORT"

        return "SPECIFIC"
