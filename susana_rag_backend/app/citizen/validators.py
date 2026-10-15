"""
Módulo de Validação Oficial de Documentos do SUS — Cidadão
===========================================================
Validação algorítmica rigorosa (sem dados arbitrários):
1. CPF: Algoritmo oficial da Receita Federal (Módulo 11 para 1º e 2º dígitos verificadores).
2. CNS (Cartão Nacional de Saúde / DATASUS):
   - Inicia com 1 ou 2: algoritmo ponderado de base PIS/PASEP (pesos 15 a 2).
   - Inicia com 7, 8 ou 9: algoritmo ponderado para cartões provisórios.
"""
from __future__ import annotations

import re


def validate_cpf(cpf: str) -> bool:
    """Valida um CPF brasileiro segundo o algoritmo oficial de dois dígitos verificadores (Módulo 11)."""
    # Remove qualquer caracter não numérico
    clean_cpf = re.sub(r"\D", "", cpf or "")
    if len(clean_cpf) != 11:
        return False

    # Elimina sequências inválidas conhecidas (ex: 111.111.111-11, 000.000.000-00)
    if clean_cpf == clean_cpf[0] * 11:
        return False

    # 1. Cálculo do primeiro dígito verificador
    soma = sum(int(clean_cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    d1 = 0 if resto == 10 else resto
    if d1 != int(clean_cpf[9]):
        return False

    # 2. Cálculo do segundo dígito verificador
    soma = sum(int(clean_cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    d2 = 0 if resto == 10 else resto
    if d2 != int(clean_cpf[10]):
        return False

    return True


def validate_cns(cns: str) -> bool:
    """
    Valida o Cartão Nacional de Saúde (CNS) conforme as normas técnicas oficiais do DATASUS.
    Suporta CNS definitivos (iniciados em 1 ou 2) e provisórios (iniciados em 7, 8 ou 9).
    """
    clean_cns = re.sub(r"\D", "", cns or "")
    if len(clean_cns) != 15:
        return False

    first_digit = clean_cns[0]

    # Cartão Nacional de Saúde Definitivo (Base PIS/PASEP: 1 ou 2)
    if first_digit in ("1", "2"):
        pis = clean_cns[:11]
        soma = sum(int(pis[i]) * (15 - i) for i in range(11))
        resto = soma % 11
        dv = 11 - resto
        resultado = ""
        if dv == 11:
            dv = 0
        if dv == 10:
            soma += 2
            resto = soma % 11
            dv = 11 - resto
            resultado = f"{pis}001{dv}"
        else:
            resultado = f"{pis}000{dv}"
        return clean_cns == resultado

    # Cartão Nacional de Saúde Provisório (Iniciado em 7, 8 ou 9)
    elif first_digit in ("7", "8", "9"):
        soma = sum(int(clean_cns[i]) * (15 - i) for i in range(15))
        resto = soma % 11
        return resto == 0

    return False
