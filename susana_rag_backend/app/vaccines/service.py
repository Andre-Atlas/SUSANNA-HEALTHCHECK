"""
Serviço do Calendário e Guia Nacional de Imunização (PNI / SES-DF)
=================================================================
Dados 100% fidedignos às normas do Ministério da Saúde e da Secretaria de Saúde do DF.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from app.vaccines.schemas import (
    PersonalizedVaccineRecommendation,
    VaccineGuideResponse,
    VaccineItem,
)

OFFICIAL_PNI_VACCINES: List[dict] = [
    # 1. Recém-Nascido / Ao Nascer
    {
        "id": "vac_bcg",
        "nome": "BCG (Bacilo Calmette-Guérin)",
        "sigla": "BCG",
        "faixa_etaria": "recem_nascido",
        "faixa_etaria_display": "Ao Nascer (Recém-Nascido)",
        "idade_recomendada": "Ao nascer (preferencialmente nas primeiras 12 horas)",
        "doses": "Dose única",
        "doencas_prevenidas": "Formas graves de tuberculose (miliar e meníngea)",
        "orientacoes": "Aplicada por via intradérmica no braço direito. Deixa cicatriz vacinal característica.",
    },
    {
        "id": "vac_hepb_rn",
        "nome": "Hepatite B (Recombinante)",
        "sigla": "Hep B",
        "faixa_etaria": "recem_nascido",
        "faixa_etaria_display": "Ao Nascer (Recém-Nascido)",
        "idade_recomendada": "Nas primeiras 24 horas de vida",
        "doses": "Dose ao nascer",
        "doencas_prevenidas": "Hepatite B e transmissão vertical materno-infantil",
        "orientacoes": "Fundamental para prevenção da cronificação da infecção por hepatite B.",
    },
    # 2. Criança (2 a 12 meses)
    {
        "id": "vac_penta_2m",
        "nome": "Pentavalente (DTP/Hib/Hep B)",
        "sigla": "Penta",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (2, 4 e 6 meses)",
        "idade_recomendada": "Aos 2, 4 e 6 meses de vida",
        "doses": "3 doses (intervalo de 60 dias)",
        "doencas_prevenidas": "Difteria, Tétano, Coqueluche, Meningite por Hib e Hepatite B",
        "orientacoes": "Proteção combinada essencial no primeiro semestre de vida.",
    },
    {
        "id": "vac_vip_2m",
        "nome": "Poliomielite 1, 2 e 3 (Inativada - VIP)",
        "sigla": "VIP",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (2, 4 e 6 meses)",
        "idade_recomendada": "Aos 2, 4 e 6 meses de vida",
        "doses": "3 doses injetáveis",
        "doencas_prevenidas": "Paralisia Infantil (Poliomielite)",
        "orientacoes": "Vacina injetável 100% inativada, segura e de alta eficácia.",
    },
    {
        "id": "vac_pneumo10_2m",
        "nome": "Pneumocócica 10-Valente (Conjugada)",
        "sigla": "Pneumo 10V",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (2, 4 e 12 meses)",
        "idade_recomendada": "Aos 2 e 4 meses, com reforço aos 12 meses",
        "doses": "2 doses + 1 reforço",
        "doencas_prevenidas": "Pneumonia, meningite e otite causadas por 10 sorotipos de pneumococo",
        "orientacoes": "Protege os pulmões e o sistema nervoso central contra infecções bacterianas graves.",
    },
    {
        "id": "vac_rotavirus_2m",
        "nome": "Rotavírus Humano G1P1 (Atenuada)",
        "sigla": "VRH",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (2 e 4 meses)",
        "idade_recomendada": "Aos 2 meses (limite até 3m15d) e 4 meses (limite até 7m29d)",
        "doses": "2 doses orais (gotinha)",
        "doencas_prevenidas": "Diarreia grave e desidratação por rotavírus",
        "orientacoes": "Vacina oral. Respeitar rigorosamente a idade máxima permitida.",
    },
    {
        "id": "vac_meningo_c_3m",
        "nome": "Meningocócica C (Conjugada)",
        "sigla": "Meningo C",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (3, 5 e 12 meses)",
        "idade_recomendada": "Aos 3 e 5 meses, com reforço aos 12 meses",
        "doses": "2 doses + 1 reforço",
        "doencas_prevenidas": "Meningite meningocócica do sorogrupo C",
        "orientacoes": "Evita sequelas neurológicas graves causadas pelo meningococo.",
    },
    {
        "id": "vac_fa_9m",
        "nome": "Febre Amarela (Atenuada)",
        "sigla": "FA",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (9 meses e 4 anos)",
        "idade_recomendada": "Aos 9 meses de vida, com reforço aos 4 anos",
        "doses": "1 dose + 1 reforço",
        "doencas_prevenidas": "Febre Amarela silvestre e urbana",
        "orientacoes": "Área de recomendação em todo o Distrito Federal e Centro-Oeste.",
    },
    {
        "id": "vac_triplice_viral_12m",
        "nome": "Tríplice Viral (Sarampo, Caxumba, Rubéola)",
        "sigla": "SCR",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (12 e 15 meses)",
        "idade_recomendada": "Aos 12 meses (Dose 1) e 15 meses (Tetra Viral ou SCR + Varicela)",
        "doses": "2 doses",
        "doencas_prevenidas": "Sarampo, Caxumba e Rubéola",
        "orientacoes": "Indispensável para manter o DF livre do sarampo e rubéola congênita.",
    },
    {
        "id": "vac_hepa_15m",
        "nome": "Hepatite A",
        "sigla": "Hep A",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (15 meses)",
        "idade_recomendada": "Aos 15 meses de vida",
        "doses": "Dose única",
        "doencas_prevenidas": "Hepatite infecciosa do tipo A",
        "orientacoes": "Proteção hepática de longa duração.",
    },
    {
        "id": "vac_dtp_reforco",
        "nome": "DTP (Tríplice Bacteriana Infantil)",
        "sigla": "DTP",
        "faixa_etaria": "crianca",
        "faixa_etaria_display": "Criança (15 meses e 4 anos)",
        "idade_recomendada": "Reforços aos 15 meses e aos 4 anos",
        "doses": "2 reforços",
        "doencas_prevenidas": "Difteria, Tétano e Coqueluche",
        "orientacoes": "Garante a imunidade adquirida no primeiro ano de vida.",
    },
    # 3. Adolescentes
    {
        "id": "vac_hpv_adol",
        "nome": "HPV Quadrivalente (Papilomavírus Humano)",
        "sigla": "HPV",
        "faixa_etaria": "adolescente",
        "faixa_etaria_display": "Adolescentes (9 a 14 anos)",
        "idade_recomendada": "Meninas e meninos de 9 a 14 anos",
        "doses": "Dose única (novo protocolo PNI/MS 2024+)",
        "doencas_prevenidas": "Câncer de colo do útero, pênis, ânus, orofaringe e verrugas genitais",
        "orientacoes": "Prevenção oncológica de alta eficácia antes do início da vida sexual.",
    },
    {
        "id": "vac_meningo_acwy_adol",
        "nome": "Meningocócica ACWY (Conjugada)",
        "sigla": "Meningo ACWY",
        "faixa_etaria": "adolescente",
        "faixa_etaria_display": "Adolescentes (11 a 14 anos)",
        "idade_recomendada": "Adolescentes de 11 a 14 anos",
        "doses": "Dose de reforço",
        "doencas_prevenidas": "Meningite e infecções graves por 4 sorogrupos de meningococo",
        "orientacoes": "Amplia o espectro de proteção conferido na infância contra os tipos A, W e Y.",
    },
    # 4. Adultos e Idosos
    {
        "id": "vac_dt_adulto",
        "nome": "Dupla Adulto (dT - Difteria e Tétano)",
        "sigla": "dT",
        "faixa_etaria": "adulto",
        "faixa_etaria_display": "Adultos e Idosos",
        "idade_recomendada": "A cada 10 anos ao longo de toda a vida adulta",
        "doses": "Reforço decenal",
        "doencas_prevenidas": "Tétano e Difteria",
        "orientacoes": "Em caso de ferimentos profundos ou perfurocortantes, antecipar reforço se > 5 anos.",
    },
    {
        "id": "vac_influenza_anual",
        "nome": "Influenza Trivalente / Tetravalente (Gripe)",
        "sigla": "Influenza",
        "faixa_etaria": "idoso",
        "faixa_etaria_display": "Idosos (60+ anos), Crianças e Grupos Prioritários",
        "idade_recomendada": "Anualmente durante a Campanha de Vacinação do DF",
        "doses": "Dose anual",
        "doencas_prevenidas": "Formas graves e internações por vírus da Gripe (H1N1, H3N2 e Influenza B)",
        "orientacoes": "Composição atualizada anualmente com as cepas circulantes.",
    },
    {
        "id": "vac_pneumo23_idoso",
        "nome": "Pneumocócica 23-Valente (Polissacarídica)",
        "sigla": "Pneumo 23V",
        "faixa_etaria": "idoso",
        "faixa_etaria_display": "Idosos (60+ anos) Institucionalizados ou com Comorbidades",
        "idade_recomendada": "Pessoas a partir de 60 anos institucionalizadas ou imunossuprimidas",
        "doses": "1 dose + 1 reforço após 5 anos",
        "doencas_prevenidas": "Pneumonia bacteriana invasiva e septicemia por pneumococo",
        "orientacoes": "Disponibilizada nos Centros de Referência de Imunobiológicos Especiais (CRIE) e UBSs.",
    },
    # 5. Gestantes
    {
        "id": "vac_dtpa_gestante",
        "nome": "dTpa (Tríplice Bacteriana Acelular do Adulto)",
        "sigla": "dTpa",
        "faixa_etaria": "gestante",
        "faixa_etaria_display": "Gestantes",
        "idade_recomendada": "A cada gestação a partir da 20ª semana",
        "doses": "1 dose por gravidez",
        "doencas_prevenidas": "Difteria, Tétano e Coqueluche no recém-nascido",
        "orientacoes": "Transfere anticorpos protetores da mãe para o bebê via placenta, protegendo o recém-nascido.",
    },
    {
        "id": "vac_hepb_gestante",
        "nome": "Hepatite B (Recombinante Gestante / Adulto)",
        "sigla": "Hep B",
        "faixa_etaria": "gestante",
        "faixa_etaria_display": "Gestantes e Adultos",
        "idade_recomendada": "Em qualquer período gestacional se não imunizada previamente",
        "doses": "3 doses (esquema 0, 1 e 6 meses)",
        "doencas_prevenidas": "Hepatite B e prevenção de transmissão vertical para o bebê",
        "orientacoes": "Avaliação de sorologia Anti-HBs no pré-natal e vacinação imediata se suscetível.",
    },
]

CAMPANHAS_ATIVAS_DF = [
    {
        "titulo": "Campanha Distrital de Vacinação contra a Influenza 2026",
        "publico": "Crianças de 6m a 5 anos, gestantes, puérperas, idosos (60+) e trabalhadores da saúde",
        "local": "Salas de vacina das UBSs do DF (segunda a sexta, das 07h às 19h)",
        "status": "Em andamento",
    },
    {
        "titulo": "Mobilização contra a Dengue e Hidratação Precoce",
        "publico": "Toda a população com sintomas de febre alta, dores no corpo e atrás dos olhos",
        "local": "Tendas de acolhimento e UBSs com atendimento estendido Saúde na Hora",
        "status": "Permanente",
    },
]


class VaccineGuideService:
    def get_vaccines(self, faixa_etaria: Optional[str] = None) -> VaccineGuideResponse:
        items = [VaccineItem(**v) for v in OFFICIAL_PNI_VACCINES]
        if faixa_etaria and faixa_etaria.lower() not in ("todas", "todos", ""):
            f_norm = faixa_etaria.lower().strip()
            items = [v for v in items if v.faixa_etaria == f_norm]

        return VaccineGuideResponse(
            total=len(items),
            faixa_etaria_filtro=faixa_etaria,
            vacinas=items,
            campanhas_ativas=CAMPANHAS_ATIVAS_DF,
        )

    def get_personalized_recommendation(
        self,
        birth_date_str: str,
        is_pregnant: bool = False,
    ) -> PersonalizedVaccineRecommendation:
        try:
            d = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            hoje = date.today()
            idade = hoje.year - d.year - ((hoje.month, hoje.day) < (d.month, d.day))
        except Exception:
            idade = 30

        if idade < 1:
            faixa = "recem_nascido"
        elif idade < 11:
            faixa = "crianca"
        elif idade < 20:
            faixa = "adolescente"
        elif idade < 60:
            faixa = "adulto"
        else:
            faixa = "idoso"

        all_items = [VaccineItem(**v) for v in OFFICIAL_PNI_VACCINES]
        recommended: List[VaccineItem] = []

        if is_pregnant:
            recommended.extend([v for v in all_items if v.faixa_etaria == "gestante"])
            recommended.extend([v for v in all_items if v.id == "vac_influenza_anual"])
        else:
            recommended = [v for v in all_items if v.faixa_etaria in (faixa, "adulto" if faixa == "idoso" else faixa)]

        alerta = None
        if is_pregnant:
            alerta = "Gestante: agendar dose de dTpa a partir da 20ª semana na UBS de referência."
        elif faixa == "recem_nascido":
            alerta = "Bebê: verificar doses de BCG e Hepatite B e preparar vacinas dos 2 meses."
        elif faixa == "idoso":
            alerta = "Idoso (60+): conferir vacinação anual contra Influenza e reforço de dT."

        return PersonalizedVaccineRecommendation(
            idade_anos=idade,
            faixa_etaria=faixa,
            gestante=is_pregnant,
            vacinas_recomendadas=recommended,
            proxima_dose_alerta=alerta,
        )
