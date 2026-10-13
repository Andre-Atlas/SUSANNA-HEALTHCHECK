"""
Conversational Context Manager — Memória multi-turn, resolução de anáforas e opções interativas.
Garante que mensagens de acompanhamento ("1", "mostre", "e onde fica?") sejam contextualizadas
com o histórico e com o vocabulário popular da saúde do SUS-DF.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Tuple


# Mapeamento de termos populares / coloquiais para terminologia oficial do SUS-DF
POPULAR_SYNONYMS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\bpostinhos?\s+de\s+sa[uú]de\b", re.I), "UBS Unidade Básica de Saúde"),
    (re.compile(r"\bpostinhos?\b", re.I), "UBS Unidade Básica de Saúde"),
    (re.compile(r"\bpostos?\s+de\s+sa[uú]de\b", re.I), "UBS Unidade Básica de Saúde"),
    (re.compile(r"\bupazinhas?\b", re.I), "UPA Unidade de Pronto Atendimento"),
    (re.compile(r"\bfarmacinhas?\b", re.I), "Farmácia da UBS"),
    (re.compile(r"\bpegar\s+rem[eé]dios?\b", re.I), "retirada de medicamentos na Farmácia da UBS e Farmácia de Alto Custo"),
    (re.compile(r"\bretirar\s+rem[eé]dios?\b", re.I), "retirada de medicamentos Farmácia da UBS"),
    (re.compile(r"\bmarcar\s+(m[eé]dico|consulta)\b", re.I), "agendamento e acolhimento na UBS"),
    (re.compile(r"\bpr[eé][- ]natal\b", re.I), "pré-natal da gestante na UBS"),
    (re.compile(r"\bteste\s+do\s+pezinho\b", re.I), "triagem neonatal teste do pezinho na UBS"),
    (re.compile(r"\bcart[aã]o\s+sus\s+do\s+beb[eê]\b", re.I), "cadastro do Cartão Nacional de Saúde recém-nascido na UBS"),
]


def expand_popular_terms(text: str) -> str:
    """Substitui termos populares pelos termos formais equivalentes."""
    result = text
    for pattern, replacement in POPULAR_SYNONYMS:
        result = pattern.sub(replacement, result)
    return result


class ConversationalContextManager:
    """Gerencia a contextualização de perguntas encadeadas em múltiplos turnos."""

    @classmethod
    def extract_numbered_options_from_text(cls, text: str) -> List[str]:
        """
        Extrai opções numeradas ou listadas do texto do assistente.
        Ex: '1. Vacinas disponíveis', '[1] Endereço da UBS', '• Horários'.
        """
        options: List[str] = []
        # Padrão 1: "1. Texto", "1 - Texto", "1) Texto"
        matches = re.findall(r"(?:^|\n)\s*(?:[1-9]\.|\([1-9]\)|[1-9]\)|\[[1-9]\]|[1-9]\s*[-–])\s*([^\n\.\;]+)", text)
        for m in matches:
            cleaned = m.strip()
            if len(cleaned) > 3 and cleaned not in options:
                options.append(cleaned)
        
        # Padrão 2: menções inline tipo "[1] Informamos que... [2] Além disso..."
        if not options:
            inline_matches = re.findall(r"\[(\d+)\]\s*([^\[\]\.\;\n]+)", text)
            for num, opt in inline_matches:
                cleaned = opt.strip()
                if len(cleaned) > 5 and cleaned not in options:
                    options.append(cleaned)

        return options

    @classmethod
    def contextualize(
        cls,
        current_message: str,
        history: Sequence[Any],
    ) -> str:
        """
        Gera uma Standalone Search Query para o RAG com base no histórico.
        Trata:
        - Escolha numérica ("1", "2")
        - Verbos anafóricos ("mostre", "verifique", "explique", "e o horário?")
        - Termos populares ("postinho em ceilândia" -> "UBS Ceilândia")
        """
        raw_msg = current_message.strip()
        expanded_current = expand_popular_terms(raw_msg)

        if not history:
            return expanded_current

        # Encontrar última fala do assistente e última fala do usuário
        last_bot_msg = ""
        last_user_msg = ""
        for m in reversed(history):
            text = m.get_text() if hasattr(m, "get_text") else (m.get("content") or m.get("text", ""))
            is_u = m.is_user() if hasattr(m, "is_user") else (m.get("isUser") or m.get("role") == "user")
            if is_u and not last_user_msg:
                last_user_msg = text
            elif not is_u and not last_bot_msg:
                last_bot_msg = text
            if last_bot_msg and last_user_msg:
                break

        # 1. Tratar escolhas numéricas puras: "1", "2", "3"
        if raw_msg.isdigit():
            idx = int(raw_msg)
            options = cls.extract_numbered_options_from_text(last_bot_msg)
            if 1 <= idx <= len(options):
                chosen_option = options[idx - 1]
                return f"{chosen_option} {last_user_msg}".strip()
            elif last_user_msg:
                # Se não encontrou lista explícita, associa a opção ao tema anterior
                return f"{last_user_msg} detalhe opção {idx}"

        # 2. Tratar verbos curtos anafóricos: "mostre", "verifique", "onde", "qual", "como"
        short_tokens = {"mostre", "verifique", "veja", "exiba", "onde", "como", "qual", "quais", "sim", "ok", "quero"}
        words = raw_msg.lower().split()
        if len(words) <= 3 and any(w in short_tokens for w in words):
            # Sintetizar pergunta contextualizada com o tema anterior
            base_topic = expand_popular_terms(last_user_msg) if last_user_msg else "serviços de saúde SUS-DF"
            return f"{expanded_current} {base_topic}"

        # 3. Tratar perguntas relativas: "e onde fica?", "qual o horário?", "funciona sábado?"
        if any(raw_msg.lower().startswith(p) for p in ["e ", "mas ", "onde ", "qual ", "quando ", "como "]):
            if last_user_msg:
                # Adiciona entidade anterior se não estiver presente
                return f"{expanded_current} {expand_popular_terms(last_user_msg)}"

        return expanded_current

    @classmethod
    def build_interactive_chips(
        cls,
        current_query: str,
        response_text: str,
        retrieved_sources: Sequence[str] = (),
    ) -> List[Dict[str, str]]:
        """
        Gera chips interativos dinâmicos com base no contexto para que o usuário
        possa clicar diretamente em vez de digitar [1] ou [2].
        """
        chips: List[Dict[str, str]] = []
        low_resp = response_text.lower()
        low_query = current_query.lower()

        # 1. Se o assistente listou opções numeradas, gera chips diretos
        numbered_options = cls.extract_numbered_options_from_text(response_text)
        for opt in numbered_options[:3]:
            short_label = opt[:36] + ("..." if len(opt) > 36 else "")
            chips.append({
                "label": f"👉 {short_label}",
                "query": opt,
            })

        # 2. Contexto de Vacinação
        if ("vacina" in low_resp or "vacina" in low_query) and len(chips) < 3:
            if "onde" not in low_query:
                chips.append({
                    "label": "📍 Onde se vacinar?",
                    "query": "onde encontrar salas de vacinação nas UBSs do DF?",
                })
            if "idoso" in low_query:
                chips.append({
                    "label": "💉 Vacinas para idosos",
                    "query": "quais vacinas recomendadas para idosos no SUS-DF?",
                })
            elif "grávida" in low_query or "gestante" in low_query:
                chips.append({
                    "label": "🤰 Vacinas da gestação",
                    "query": "quais vacinas a gestante deve tomar no SUS-DF?",
                })
            elif "criança" in low_query or "bebê" in low_query:
                chips.append({
                    "label": "👶 Vacinas infantis",
                    "query": "quais as vacinas do calendário infantil nas UBSs?",
                })

        # 3. Contexto de UBS / Endereços / Postinhos
        if ("ubs" in low_resp or "unidade básica" in low_resp or "postinho" in low_query) and len(chips) < 3:
            chips.append({
                "label": "⏰ Horários de atendimento",
                "query": "qual o horário de funcionamento das UBSs no DF?",
            })
            chips.append({
                "label": "📋 Documentos necessários",
                "query": "quais documentos levar para atendimento na UBS?",
            })

        # 4. Contexto de Medicamentos / Farmácia
        if ("medicamento" in low_resp or "remédio" in low_resp or "farmácia" in low_resp) and len(chips) < 3:
            chips.append({
                "label": "💊 Como retirar remédios",
                "query": "como retirar medicamentos gratuitos na farmácia da UBS?",
            })

        # 5. Contexto de Dengue / Urgência
        if ("dengue" in low_resp or "sintoma" in low_resp or "febre" in low_resp) and len(chips) < 3:
            chips.append({
                "label": "💧 Tendas de hidratação",
                "query": "onde ficam as tendas de hidratação para dengue no DF?",
            })
            chips.append({
                "label": "🚨 Quando ir à UPA?",
                "query": "quais os sinais de alarme da dengue para ir à UPA?",
            })

        return chips[:4]
