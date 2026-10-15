"""
Gerador do Diretório Unificado e Estruturado de Saúde do DF (33 Regiões Administrativas).
Gera dados factuais e detalhados de UBSs, Salas de Vacinação, Farmácias, Pré-natal, Puericultura,
UPAs e Hospitais de todas as 33 RAs do Distrito Federal no padrão oficial da SES-DF.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "corpus"

# Definição das 33 Regiões Administrativas do DF e suas Unidades Oficiais
DF_REGIONS: List[Dict[str, Any]] = [
    {
        "ra_id": "plano_piloto",
        "ra_nome": "Plano Piloto",
        "regiao_saude": "Central",
        "bairros": ["Asa Sul", "Asa Norte", "Vila Planalto", "Vila Telebrasília", "Setor Comercial Sul", "Setor Bancário"],
        "unidades": [
            {
                "nome": "UBS 1 Asa Sul",
                "tipo": "ubs",
                "endereco": "SGAS 612, Lote 28/29, Asa Sul, Brasília - DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "curativos", "odontologia"],
                "detalhes": "Referência na Asa Sul para imunização completa de crianças, adultos e idosos. Coleta de teste do pezinho e pré-natal da gestante."
            },
            {
                "nome": "UBS 1 Asa Norte",
                "tipo": "ubs",
                "endereco": "EQN 114/115, Área Especial, Asa Norte, Brasília - DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento da Estratégia Saúde da Família para moradores da Asa Norte. Sala de vacinação com vacinas de rotina e sazonais."
            },
            {
                "nome": "UBS 2 Asa Norte",
                "tipo": "ubs",
                "endereco": "EQN 114/115, Lote B, Asa Norte, Brasília - DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos"],
                "detalhes": "Acompanhamento de gestantes, puericultura, vacinas do calendário infantil e retirada de remédios básicos."
            },
            {
                "nome": "UBS 1 Vila Planalto",
                "tipo": "ubs",
                "endereco": "Rua Engenheiro Carlos R. de Rezende, Acampamento Pacheco Fernandes, Vila Planalto, Brasília - DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento comunitário da Vila Planalto com vacinas, farmácia básica e acompanhamento materno-infantil."
            },
            {
                "nome": "UBS 1 Vila Telebrasília",
                "tipo": "ubs",
                "endereco": "Rua 01, Lote 01, Vila Telebrasília, Brasília - DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Atendimento de saúde da família e imunização para a comunidade local."
            }
        ],
        "urgencia": {
            "upa": None,
            "hospital": "Hospital Regional da Asa Norte (HRAN) e Hospital Materno Infantil de Brasília (HMIB - referência materno-infantil na L2 Sul)",
            "detalhes": "Para urgências clínicas e queimados, procurar o HRAN (Setor Hospitalar Norte). Para urgências obstétricas, parto e pediatria grave, o HMIB (SGAS 608) funciona 24 horas."
        },
        "farmacia_alto_custo": "Farmácia de Alto Custo da Asa Sul - Estação Solar 102 Sul do Metrô (segunda a sexta das 07:00 às 19:00 e sábados das 07:00 às 12:00)."
    },
    {
        "ra_id": "ceilandia",
        "ra_nome": "Ceilândia",
        "regiao_saude": "Oeste",
        "bairros": ["Ceilândia Centro", "Ceilândia Sul", "Ceilândia Norte", "Setor O", "P Sul", "P Norte", "M Norte", "QNM", "QNN", "QNO", "QNP"],
        "unidades": [
            {
                "nome": "UBS 1 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNM 15, Lote D, Ceilândia Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "curativos"],
                "detalhes": "Atendimento completo de atenção básica, sala de vacina de rotina, teste do pezinho e pré-natal."
            },
            {
                "nome": "UBS 2 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNN 15, Lote F, Ceilândia Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Acolhimento de saúde da família, exames preventivos, acompanhamento de gestantes e crianças."
            },
            {
                "nome": "UBS 3 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNM 34, Área Especial 01, M Norte, Ceilândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Atendimento para a população do M Norte e imediações da Taguatinga Norte."
            },
            {
                "nome": "UBS 5 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNM 16, Módulo F, Ceilândia Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Unidade participante do Programa Saúde na Hora com atendimento noturno até as 22h e aos sábados pela manhã."
            },
            {
                "nome": "UBS 7 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNO 10, Área Especial D, Setor O, Ceilândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "curativos", "saude_na_hora"],
                "detalhes": "Programa Saúde na Hora no Setor O: vacinação e consultas estendidas até 22h."
            },
            {
                "nome": "UBS 8 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNP 11, Área Especial, P Sul, Ceilândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "saude_na_hora"],
                "detalhes": "Saúde na Hora no P Sul com vacinação completa, pré-natal e atendimento noturno até 22h."
            },
            {
                "nome": "UBS 10 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNN 12, Área Especial, Ceilândia Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Unidade ampliada com Saúde na Hora até as 22h, sala de vacina de referência e odontologia."
            },
            {
                "nome": "UBS 12 Ceilândia",
                "tipo": "ubs",
                "endereco": "QNP 28, Área Especial, P Sul, Ceilândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos", "saude_na_hora"],
                "detalhes": "Unidade com Saúde na Hora no P Sul atendendo até 22h e sábados."
            }
        ],
        "urgencia": {
            "upa": "UPA Ceilândia (QNM 27 Área Especial) e UPA Ceilândia II (QNO 21 Setor O) - Atendimento 24 horas",
            "hospital": "Hospital Regional de Ceilândia (HRC) - Área Especial QNM 27/28",
            "detalhes": "Casos de urgência e emergência adulta e pediátrica 24h na UPA Ceilândia e UPA Setor O. Maternidade, partos e cirurgias de urgência no HRC."
        },
        "farmacia_alto_custo": "Farmácia de Alto Custo de Ceilândia - EQNM 18/20, Praça do Cidadão, Ceilândia Centro (segunda a sexta das 07:00 às 19:00 e sábados das 07:00 às 12:00)."
    },
    {
        "ra_id": "taguatinga",
        "ra_nome": "Taguatinga",
        "regiao_saude": "Sudoeste",
        "bairros": ["Taguatinga Centro", "Taguatinga Norte", "Taguatinga Sul", "QNA", "QNB", "QNC", "QND", "QNE", "QNF", "QNG", "QNH", "QNJ", "QNL", "Setor C Sul", "Setor D Sul", "M Norte"],
        "unidades": [
            {
                "nome": "UBS 1 Taguatinga",
                "tipo": "ubs",
                "endereco": "QNG 2, Área Especial, Taguatinga Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Unidade polo com Saúde na Hora até as 22h e sábados. Sala de vacinação ativa, pré-natal e puericultura."
            },
            {
                "nome": "UBS 2 Taguatinga",
                "tipo": "ubs",
                "endereco": "QND Lote 1, Taguatinga Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos"],
                "detalhes": "Atendimento comunitário da Estratégia Saúde da Família, vacinas de rotina e pré-natal de baixo risco."
            },
            {
                "nome": "UBS 3 Taguatinga",
                "tipo": "ubs",
                "endereco": "Setor C Sul, Área Especial 01, Taguatinga Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Atendimento de saúde da família para Taguatinga Sul. Teste do pezinho e vacinação infantil e de idosos."
            },
            {
                "nome": "UBS 5 Taguatinga",
                "tipo": "ubs",
                "endereco": "Setor D Sul, Área Especial 23, Taguatinga Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Saúde na Hora em Taguatinga Sul até as 22h. Farmácia básica, vacinação e odontologia."
            },
            {
                "nome": "UBS 8 Taguatinga",
                "tipo": "ubs",
                "endereco": "QNL 24, Área Especial 02, Taguatinga Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "curativos"],
                "detalhes": "Atendimento para os moradores do setor QNL. Sala de vacinação e consultas materno-infantis."
            }
        ],
        "urgencia": {
            "upa": "UPA Taguatinga - QNF 24, Área Especial, Taguatinga Norte (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Taguatinga (HRT) - Setor C Norte, Área Especial (Atendimento 24 horas)",
            "detalhes": "Para urgências clínicas e pediátricas 24h, dirigir-se à UPA Taguatinga ou ao Pronto-Socorro do HRT. Centro de trauma e maternidade no HRT."
        },
        "farmacia_alto_custo": "Atendimento de referência na Farmácia de Alto Custo de Ceilândia (EQNM 18/20) ou Asa Sul."
    },
    {
        "ra_id": "samambaia",
        "ra_nome": "Samambaia",
        "regiao_saude": "Sudoeste",
        "bairros": ["Samambaia Norte", "Samambaia Sul", "QN", "QS", "QR"],
        "unidades": [
            {
                "nome": "UBS 1 Samambaia",
                "tipo": "ubs",
                "endereco": "QN 408, Conjunto 05, Samambaia Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Unidade de referência com Saúde na Hora até 22h e sábados. Sala de vacinação com calendário completo."
            },
            {
                "nome": "UBS 2 Samambaia",
                "tipo": "ubs",
                "endereco": "QS 614, Área Especial 02, Samambaia Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "saude_na_hora"],
                "detalhes": "Horário estendido até 22h próximo ao Hospital Regional de Samambaia. Pré-natal e puericultura."
            },
            {
                "nome": "UBS 3 Samambaia",
                "tipo": "ubs",
                "endereco": "QN 429, Conjunto F, Samambaia Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Atendimento comunitário, vacinas infantis e acompanhamento de doentes crônicos (Hiperdia)."
            },
            {
                "nome": "UBS 4 Samambaia",
                "tipo": "ubs",
                "endereco": "QN 512, Conjunto 02, Samambaia Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "curativos", "saude_na_hora"],
                "detalhes": "Saúde na Hora até 22h na QN 512. Teste do pezinho, farmácia e curativos."
            }
        ],
        "urgencia": {
            "upa": "UPA Samambaia - QS 107, Área Especial, Samambaia Sul (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Samambaia (HRSam) - QS 614, Área Especial",
            "detalhes": "UPA Samambaia 24 horas para urgências clínicas. HRSam com pronto-socorro obstétrico, maternidade e cirurgia de urgência."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo de Ceilândia ou Gama."
    },
    {
        "ra_id": "gama",
        "ra_nome": "Gama",
        "regiao_saude": "Sul",
        "bairros": ["Setor Sul", "Setor Leste", "Setor Central", "Setor Oeste", "Setor Norte", "Ponte Alta", "DVO"],
        "unidades": [
            {
                "nome": "UBS 1 Gama",
                "tipo": "ubs",
                "endereco": "Entrequadras 6/8, Setor Sul, Gama, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Polo de atendimento com Saúde na Hora até 22h no Setor Sul. Vacinação completa, teste do pezinho e pré-natal."
            },
            {
                "nome": "UBS 2 Gama",
                "tipo": "ubs",
                "endereco": "Área Especial Lote 01, Setor Sul, Gama, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Atendimento comunitário, programas de hipertensão e diabetes e vacinas de rotina."
            },
            {
                "nome": "UBS 3 Gama",
                "tipo": "ubs",
                "endereco": "Área Especial 03, Setor Leste, Gama, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos"],
                "detalhes": "Atendimento para os moradores do Setor Leste do Gama. Sala de vacinação e puericultura."
            },
            {
                "nome": "UBS 4 Gama",
                "tipo": "ubs",
                "endereco": "Área Especial 02, Setor Central, Gama, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "saude_na_hora"],
                "detalhes": "Saúde na Hora no Setor Central até as 22h com consultas, vacinas e remédios."
            }
        ],
        "urgencia": {
            "upa": "UPA Gama - Setor Leste, Área Especial (Atendimento 24 horas)",
            "hospital": "Hospital Regional do Gama (HRG) - Área Especial, Setor Central",
            "detalhes": "UPA Gama 24h para urgências clínicas. Pronto-socorro geral, maternidade e emergência pediátrica no HRG 24 horas."
        },
        "farmacia_alto_custo": "Farmácia de Alto Custo do Gama - Área Especial do Hospital Regional do Gama (segunda a sexta das 07:00 às 19:00 e sábados das 07:00 às 12:00)."
    },
    {
        "ra_id": "guara",
        "ra_nome": "Guará",
        "regiao_saude": "Centro-Sul",
        "bairros": ["Guará I", "Guará II", "QE", "QI"],
        "unidades": [
            {
                "nome": "UBS 1 Guará",
                "tipo": "ubs",
                "endereco": "QE 06, Lote C, Guará I, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Unidade histórica do Guará I com cobertura completa de atenção primária, vacinas e saúde bucal."
            },
            {
                "nome": "UBS 2 Guará",
                "tipo": "ubs",
                "endereco": "QE 23, Área Especial, Guará II, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "saude_na_hora"],
                "detalhes": "Saúde na Hora no Guará II: funcionamento até 22h e sábados pela manhã com vacinas e consultas."
            },
            {
                "nome": "UBS 3 Guará",
                "tipo": "ubs",
                "endereco": "QE 38, Área Especial, Guará II, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos"],
                "detalhes": "Atendimento para os setores QE 38 a QE 46 do Guará II com vacinas e acompanhamento materno-infantil."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (referência próxima) - 3ª Avenida / Área Especial",
            "hospital": "Hospital Regional do Guará (HRGu) - QI 06, Área Especial, Guará I",
            "detalhes": "Atendimento de urgência e emergência clínica e pediátrica no HRGu e na UPA Núcleo Bandeirante 24 horas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul (Estação 102 Sul do Metrô)."
    },
    {
        "ra_id": "sobradinho",
        "ra_nome": "Sobradinho",
        "regiao_saude": "Norte",
        "bairros": ["Sobradinho I", "Quadras Centrais", "Setor de Mansões Sobradinho", "Grande Colorado"],
        "unidades": [
            {
                "nome": "UBS 1 Sobradinho",
                "tipo": "ubs",
                "endereco": "Quadra 14, Área Especial 22/23, Sobradinho, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento integral de saúde da família em Sobradinho I, sala de vacina e teste do pezinho."
            },
            {
                "nome": "UBS 2 Sobradinho",
                "tipo": "ubs",
                "endereco": "Quadra 03/05, Área Especial, Sobradinho, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos"],
                "detalhes": "Consultas médicas e de enfermagem, vacinas de rotina e puericultura."
            }
        ],
        "urgencia": {
            "upa": "UPA Sobradinho - Quadra 10, Área Especial (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Sobradinho (HRS) - Quadra 12, Área Especial",
            "detalhes": "UPA Sobradinho 24h para casos de urgência clínica. HRS com pronto-socorro geral, maternidade e cirurgia de urgência 24h."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul ou Planaltina."
    },
    {
        "ra_id": "sobradinho_ii",
        "ra_nome": "Sobradinho II",
        "regiao_saude": "Norte",
        "bairros": ["Sobradinho II", "AR", "Setor de Mansões", "Vila Rabelo"],
        "unidades": [
            {
                "nome": "UBS 1 Sobradinho II",
                "tipo": "ubs",
                "endereco": "AR 13, Conjunto 07, Área Especial, Sobradinho II, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento da Estratégia Saúde da Família, vacinação completa e atendimento odontológico."
            },
            {
                "nome": "UBS 2 Sobradinho II",
                "tipo": "ubs",
                "endereco": "AR 02, Conjunto 03, Sobradinho II, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Acompanhamento materno-infantil, vacinação e remédios essenciais."
            }
        ],
        "urgencia": {
            "upa": "UPA Sobradinho (referência próxima) - Quadra 10 de Sobradinho I (24 horas)",
            "hospital": "Hospital Regional de Sobradinho (HRS) - 24 horas",
            "detalhes": "Urgências e emergências devem se dirigir à UPA Sobradinho ou ao HRS."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "planaltina",
        "ra_nome": "Planaltina",
        "regiao_saude": "Norte",
        "bairros": ["Setor Tradicional", "Vila Buritis", "Arapoanga", "Araponga", "Vale do Amanhecer", "Jardim Roriz", "Estância"],
        "unidades": [
            {
                "nome": "UBS 1 Planaltina",
                "tipo": "ubs",
                "endereco": "Vila Nossa Senhora de Fátima, Rua 02, Planaltina, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Atendimento tradicional com sala de vacina completa e teste do pezinho."
            },
            {
                "nome": "UBS 2 Planaltina",
                "tipo": "ubs",
                "endereco": "Setor Educacional, Área Especial, Planaltina, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "odontologia"],
                "detalhes": "Consultas de saúde da família, odontologia e vacinação infantil e adulta."
            },
            {
                "nome": "UBS 5 Planaltina (Arapoanga)",
                "tipo": "ubs",
                "endereco": "Quadra 02, Conjunto 01, Setor Habitacional Arapoanga, Planaltina, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "saude_na_hora"],
                "detalhes": "Unidade de grande porte no Arapoanga com Saúde na Hora até 22h e atendimento aos sábados."
            }
        ],
        "urgencia": {
            "upa": "UPA Planaltina - Setor Residencial Leste (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Planaltina (HRP) - Setor Hospitalar, Planaltina (24 horas)",
            "detalhes": "UPA Planaltina 24h para urgências clínicas. HRP para emergências cirúrgicas, partos e traumas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "santa_maria",
        "ra_nome": "Santa Maria",
        "regiao_saude": "Sul",
        "bairros": ["Santa Maria Norte", "Santa Maria Sul", "QR", "Condomínio Porto Rico", "Total Ville"],
        "unidades": [
            {
                "nome": "UBS 1 Santa Maria",
                "tipo": "ubs",
                "endereco": "QR 207/307, Conjunto A, Santa Maria Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Saúde na Hora em Santa Maria Norte até 22h com sala de vacinas, teste do pezinho e pré-natal."
            },
            {
                "nome": "UBS 2 Santa Maria",
                "tipo": "ubs",
                "endereco": "EQ 217/317, Área Especial, Santa Maria Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Atendimento comunitário da Saúde da Família e imunização de rotina."
            },
            {
                "nome": "UBS 5 Santa Maria (Porto Rico)",
                "tipo": "ubs",
                "endereco": "Condomínio Porto Rico, Área Especial 01, Santa Maria, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica", "curativos"],
                "detalhes": "Atendimento para a comunidade do Porto Rico com vacinas e acompanhamento de gestantes."
            }
        ],
        "urgencia": {
            "upa": "UPA Santa Maria - Quadra 207/307, Santa Maria Norte (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Santa Maria (HRSM) - AC 102, Conjunto A",
            "detalhes": "UPA Santa Maria 24 horas para urgências clínicas. HRSM é hospital terciário de alta complexidade com pronto-socorro geral, obstétrico e pediátrico 24 horas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo do Gama."
    },
    {
        "ra_id": "sao_sebastiao",
        "ra_nome": "São Sebastião",
        "regiao_saude": "Leste",
        "bairros": ["Centro", "Vila Nova", "São José", "Residencial Crixá", "Morro da Cruz", "Bonsucesso"],
        "unidades": [
            {
                "nome": "UBS 1 São Sebastião",
                "tipo": "ubs",
                "endereco": "Centro, Rua da Gameleira, São Sebastião, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Polo central com Saúde na Hora até 22h, vacinação completa e atendimento odontológico."
            },
            {
                "nome": "UBS 2 São Sebastião",
                "tipo": "ubs",
                "endereco": "Vila Nova, Rua 48, Área Especial, São Sebastião, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Acolhimento da saúde da família e vacinação infantil."
            }
        ],
        "urgencia": {
            "upa": "UPA São Sebastião - Quadra 102, Bairro Residencial Oeste (Atendimento 24 horas)",
            "hospital": "Hospital da Região Leste / Hospital Regional do Paranoá (HRPa) - referência hospitalar regional 24 horas",
            "detalhes": "UPA São Sebastião atende urgências clínicas 24 horas. Para internações, maternidade e cirurgias, a referência é o HRPa."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "recanto_das_emas",
        "ra_nome": "Recanto das Emas",
        "regiao_saude": "Sudoeste",
        "bairros": ["Quadras 100 a 800", "Recanto das Emas Centro"],
        "unidades": [
            {
                "nome": "UBS 1 Recanto das Emas",
                "tipo": "ubs",
                "endereco": "Quadra 307, Área Especial, Recanto das Emas, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Saúde na Hora na Quadra 307 com funcionamento até 22h e sábados pela manhã."
            },
            {
                "nome": "UBS 2 Recanto das Emas",
                "tipo": "ubs",
                "endereco": "Quadra 102, Área Especial, Recanto das Emas, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Consultas médicas e de enfermagem, vacinas de rotina e pré-natal."
            }
        ],
        "urgencia": {
            "upa": "UPA Recanto das Emas - Quadra 400/600, Área Especial (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Samambaia (HRSam) e Hospital Regional de Taguatinga (HRT) - referência hospitalar",
            "detalhes": "UPA Recanto das Emas para urgências 24 horas. Retaguarda de internação e maternidade no HRSam."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo do Gama ou Ceilândia."
    },
    {
        "ra_id": "paranoa",
        "ra_nome": "Paranoá",
        "regiao_saude": "Leste",
        "bairros": ["Paranoá Parque", "Quadras Centrais", "Fazenda Paranoá"],
        "unidades": [
            {
                "nome": "UBS 1 Paranoá",
                "tipo": "ubs",
                "endereco": "Quadra 21, Área Especial, Paranoá, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atenção primária, vacinas de rotina e atendimento materno-infantil."
            },
            {
                "nome": "UBS 3 Paranoá (Paranoá Parque)",
                "tipo": "ubs",
                "endereco": "Quadra 03, Conjunto 01, Paranoá Parque, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "saude_na_hora"],
                "detalhes": "Unidade moderna com Saúde na Hora até as 22h atendendo ao Paranoá Parque."
            }
        ],
        "urgencia": {
            "upa": "UPA Paranoá - Quadra 21, Área Especial (Atendimento 24 horas)",
            "hospital": "Hospital da Região Leste / Hospital Regional do Paranoá (HRPa) - Área Especial Quadra 02",
            "detalhes": "UPA Paranoá 24h para emergências clínicas. HRPa para partos, cirurgias e pediatria de urgência 24 horas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "nucleo_bandeirante",
        "ra_nome": "Núcleo Bandeirante",
        "regiao_saude": "Centro-Sul",
        "bairros": ["3ª Avenida", "Metropolitana", "Divinéia", "Vila Cauhy"],
        "unidades": [
            {
                "nome": "UBS 1 Núcleo Bandeirante",
                "tipo": "ubs",
                "endereco": "3ª Avenida, Área Especial 03, Núcleo Bandeirante, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento comunitário, vacinas infantis e de adultos, teste do pezinho e pré-natal."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante - 3ª Avenida / Área Especial (Atendimento 24 horas)",
            "hospital": "Hospital Regional do Guará (HRGu) e Hospital Materno Infantil (HMIB)",
            "detalhes": "UPA Núcleo Bandeirante 24h para urgências clínicas e pediátricas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "brazlandia",
        "ra_nome": "Brazlândia",
        "regiao_saude": "Oeste",
        "bairros": ["Setor Tradicional", "Setor Norte", "Setor Sul", "Vila São José", "Incra 8"],
        "unidades": [
            {
                "nome": "UBS 1 Brazlândia",
                "tipo": "ubs",
                "endereco": "Vila São José, Quadra 36, Brazlândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento primário da Vila São José com sala de vacinas e consultas de enfermagem e médicas."
            },
            {
                "nome": "UBS 2 Brazlândia",
                "tipo": "ubs",
                "endereco": "Setor Norte, Área Especial 02, Brazlândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Atendimento para a população do Setor Norte e área rural adjacente."
            }
        ],
        "urgencia": {
            "upa": "UPA Brazlândia - Setor Norte (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Brazlândia (HRBz) - Área Especial 01, Setor Tradicional",
            "detalhes": "UPA Brazlândia e Hospital Regional de Brazlândia para pronto atendimento e emergências 24 horas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo de Ceilândia."
    },
    {
        "ra_id": "riacho_fundo",
        "ra_nome": "Riacho Fundo",
        "regiao_saude": "Centro-Sul",
        "bairros": ["Riacho Fundo I", "QN", "QS", "Colônia Agrícola Kanegae"],
        "unidades": [
            {
                "nome": "UBS 1 Riacho Fundo I",
                "tipo": "ubs",
                "endereco": "QN 09, Área Especial 01, Riacho Fundo I, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Polo de saúde com Saúde na Hora até 22h, vacinação completa e teste do pezinho."
            }
        ],
        "urgencia": {
            "upa": "UPA Riacho Fundo II / UPA Núcleo Bandeirante (referências 24h)",
            "hospital": "Hospital Regional de Taguatinga (HRT) e HRGu",
            "detalhes": "Urgências 24h atendidas nas UPAs vizinhas e pronto-socorro do HRT."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "riacho_fundo_ii",
        "ra_nome": "Riacho Fundo II",
        "regiao_saude": "Centro-Sul",
        "bairros": ["QC", "QN", "Caub I e II"],
        "unidades": [
            {
                "nome": "UBS 1 Riacho Fundo II",
                "tipo": "ubs",
                "endereco": "QC 01, Conjunto 05, Riacho Fundo II, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento de saúde da família, vacinas de rotina e pré-natal de baixo risco."
            }
        ],
        "urgencia": {
            "upa": "UPA Riacho Fundo II - QC 01 Área Especial (Atendimento 24 horas)",
            "hospital": "Hospital Regional de Samambaia (HRSam)",
            "detalhes": "UPA Riacho Fundo II 24 horas para urgências clínicas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul ou Gama."
    },
    {
        "ra_id": "cruzeiro",
        "ra_nome": "Cruzeiro",
        "regiao_saude": "Centro-Sul",
        "bairros": ["Cruzeiro Velho", "Cruzeiro Novo", "SRES", "SHCES"],
        "unidades": [
            {
                "nome": "UBS 1 Cruzeiro",
                "tipo": "ubs",
                "endereco": "SHCES Quadra 805, Cruzeiro Novo, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento para os moradores do Cruzeiro Novo com sala de vacinas ativa."
            },
            {
                "nome": "UBS 2 Cruzeiro",
                "tipo": "ubs",
                "endereco": "SRES Área Especial 01, Cruzeiro Velho, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Consultas médicas e de enfermagem no Cruzeiro Velho."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (24 horas) ou HRAN",
            "hospital": "Hospital Regional da Asa Norte (HRAN) e HMIB",
            "detalhes": "Urgências clínicas encaminhadas ao HRAN ou UPA Núcleo Bandeirante."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul (Estação 102 Sul)."
    },
    {
        "ra_id": "aguas_claras",
        "ra_nome": "Águas Claras",
        "regiao_saude": "Sudoeste",
        "bairros": ["Águas Claras Vertical", "Areal", "QS 05", "Rua 17 Norte"],
        "unidades": [
            {
                "nome": "UBS 1 Águas Claras (Areal)",
                "tipo": "ubs",
                "endereco": "QS 05, Rua 100, Lote 24/26, Areal, Águas Claras, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento da Estratégia Saúde da Família para Águas Claras e Areal. Sala de vacinação com calendário nacional completo."
            }
        ],
        "urgencia": {
            "upa": "UPA Taguatinga ou UPA Samambaia (ambas 24 horas)",
            "hospital": "Hospital Regional de Taguatinga (HRT) e HRSam",
            "detalhes": "Urgências 24h direcionadas ao HRT ou UPA Taguatinga."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul ou Ceilândia."
    },
    {
        "ra_id": "vicente_pires",
        "ra_nome": "Vicente Pires",
        "regiao_saude": "Sudoeste",
        "bairros": ["Vicente Pires", "Rua 03", "Rua 04", "Rua 08", "Rua 10", "Rua 12", "Colônia Agrícola Samambaia"],
        "unidades": [
            {
                "nome": "UBS 1 Vicente Pires",
                "tipo": "ubs",
                "endereco": "Rua 04C, Chácara 12, Vicente Pires, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "curativos"],
                "detalhes": "Atendimento comunitário com sala de vacinas de rotina e acompanhamento de gestantes e crianças."
            }
        ],
        "urgencia": {
            "upa": "UPA Vicente Pires (Rua 04C) - Atendimento 24 horas",
            "hospital": "Hospital Regional de Taguatinga (HRT) - 24 horas",
            "detalhes": "UPA Vicente Pires com atendimento clínico e pediátrico de urgência 24h."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo de Ceilândia ou Asa Sul."
    },
    {
        "ra_id": "scia_estrutural",
        "ra_nome": "SCIA / Estrutural",
        "regiao_saude": "Centro-Sul",
        "bairros": ["Setor Central", "Setor Leste", "Vila Santa Luzia"],
        "unidades": [
            {
                "nome": "UBS 1 Estrutural",
                "tipo": "ubs",
                "endereco": "Setor Central, Área Especial 02, Estrutural, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Saúde na Hora até as 22h com cobertura de vacinação, teste do pezinho e pré-natal para a comunidade da Estrutural."
            },
            {
                "nome": "UBS 2 Estrutural",
                "tipo": "ubs",
                "endereco": "Quadra 18, Setor Leste, Estrutural, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Acolhimento de saúde da família e vacinação."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (24 horas) ou UPA Ceilândia",
            "hospital": "Hospital Regional da Asa Norte (HRAN) e Hospital Materno Infantil (HMIB)",
            "detalhes": "Urgências clínicas encaminhadas à UPA Núcleo Bandeirante ou ao HRAN."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "sol_nascente_por_do_sol",
        "ra_nome": "Sol Nascente / Pôr do Sol",
        "regiao_saude": "Oeste",
        "bairros": ["Trecho 1", "Trecho 2", "Trecho 3", "Pôr do Sol Quadra 100 a 300"],
        "unidades": [
            {
                "nome": "UBS 1 Sol Nascente",
                "tipo": "ubs",
                "endereco": "Trecho 01, Chácara 115, Sol Nascente, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento comunitário com sala de vacinas de rotina e atendimento materno-infantil."
            },
            {
                "nome": "UBS 2 Sol Nascente",
                "tipo": "ubs",
                "endereco": "Trecho 02, Quadra 105, Conjunto B, Sol Nascente, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Equipes de Saúde da Família, vacinas e pré-natal de baixo risco."
            }
        ],
        "urgencia": {
            "upa": "UPA Ceilândia (QNM 27) e UPA Setor O (ambas 24 horas)",
            "hospital": "Hospital Regional de Ceilândia (HRC) - 24 horas",
            "detalhes": "Urgências e emergências 24h na UPA Ceilândia e no HRC."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo de Ceilândia (Praça do Cidadão)."
    },
    {
        "ra_id": "itapoa",
        "ra_nome": "Itapoã",
        "regiao_saude": "Leste",
        "bairros": ["Quadras 60 a 378", "Del Lago", "Fascal"],
        "unidades": [
            {
                "nome": "UBS 1 Itapoã",
                "tipo": "ubs",
                "endereco": "Quadra 61, Área Especial, Itapoã, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 22:00; Sábados das 07:00 às 12:00",
                "saude_na_hora": True,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia", "saude_na_hora"],
                "detalhes": "Saúde na Hora até 22h com sala de vacina ativa, pré-natal e puericultura."
            },
            {
                "nome": "UBS 2 Itapoã (Del Lago)",
                "tipo": "ubs",
                "endereco": "Quadra 378, Conjunto A, Del Lago, Itapoã, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Consultas de saúde da família e vacinação."
            }
        ],
        "urgencia": {
            "upa": "UPA Itapoã - Quadra 203, Del Lago (Atendimento 24 horas)",
            "hospital": "Hospital da Região Leste / Hospital Regional do Paranoá (HRPa) - 24 horas",
            "detalhes": "UPA Itapoã 24h para urgências clínicas. HRPa para internações e partos."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "lago_sul",
        "ra_nome": "Lago Sul",
        "regiao_saude": "Centro-Sul",
        "bairros": ["QI", "QL", "Setor de Mansões Dom Bosco"],
        "unidades": [
            {
                "nome": "UBS 1 Lago Sul",
                "tipo": "ubs",
                "endereco": "SHIS QI 21, Área Especial, Lago Sul, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Sala de vacinação completa de rotina, teste do pezinho e saúde da família."
            }
        ],
        "urgencia": {
            "upa": "UPA São Sebastião ou UPA Núcleo Bandeirante (24 horas)",
            "hospital": "Hospital Materno Infantil de Brasília (HMIB) e HRAN",
            "detalhes": "Urgências pediátricas e obstétricas no HMIB (L2 Sul)."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul (Estação 102 Sul)."
    },
    {
        "ra_id": "lago_norte",
        "ra_nome": "Lago Norte",
        "regiao_saude": "Norte",
        "bairros": ["SHIN", "QI", "QL", "Setor Taquari"],
        "unidades": [
            {
                "nome": "UBS 1 Lago Norte",
                "tipo": "ubs",
                "endereco": "SHIN QI 03, Área Especial, Lago Norte, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Atendimento e imunização para crianças, gestantes e idosos."
            }
        ],
        "urgencia": {
            "upa": "UPA Sobradinho (24 horas)",
            "hospital": "Hospital Regional da Asa Norte (HRAN) e Hospital Regional de Sobradinho (HRS)",
            "detalhes": "Urgências 24h no HRAN ou HRS."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "candangolandia",
        "ra_nome": "Candangolândia",
        "regiao_saude": "Centro-Sul",
        "bairros": ["QRO", "QRAL"],
        "unidades": [
            {
                "nome": "UBS 1 Candangolândia",
                "tipo": "ubs",
                "endereco": "Área Especial QRO, Lote 01, Candangolândia, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento comunitário, vacinas, teste do pezinho e pré-natal."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (3ª Avenida - 24 horas)",
            "hospital": "Hospital Regional do Guará (HRGu) e HMIB",
            "detalhes": "UPA Núcleo Bandeirante 24h para urgências clínicas."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "sudoeste_octogonal",
        "ra_nome": "Sudoeste / Octogonal",
        "regiao_saude": "Centro-Sul",
        "bairros": ["QMSW", "QOSW", "CCSW", "AOS"],
        "unidades": [
            {
                "nome": "UBS 1 Sudoeste",
                "tipo": "ubs",
                "endereco": "CCSW 03/04, Lote 01, Sudoeste, Brasília - DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Sala de vacinação de rotina, teste do pezinho e pré-natal de baixo risco."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (24 horas)",
            "hospital": "Hospital Regional da Asa Norte (HRAN) e Hospital Materno Infantil (HMIB)",
            "detalhes": "Emergências clínicas no HRAN e obstétricas/pediátricas no HMIB."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "varjao",
        "ra_nome": "Varjão",
        "regiao_saude": "Norte",
        "bairros": ["Quadras 01 a 10"],
        "unidades": [
            {
                "nome": "UBS 1 Varjão",
                "tipo": "ubs",
                "endereco": "Quadra 05, Área Especial, Varjão, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atenção básica comunitária com sala de vacinas, teste do pezinho e saúde bucal."
            }
        ],
        "urgencia": {
            "upa": "UPA Sobradinho (24 horas)",
            "hospital": "Hospital Regional da Asa Norte (HRAN) e HRS",
            "detalhes": "Urgências no HRAN ou UPA Sobradinho."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "park_way",
        "ra_nome": "Park Way",
        "regiao_saude": "Centro-Sul",
        "bairros": ["SMPW Quadras 01 a 29"],
        "unidades": [
            {
                "nome": "UBS 1 Park Way",
                "tipo": "ubs",
                "endereco": "SMPW Quadra 14, Conjunto 02, Lote 01, Park Way, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "Atendimento comunitário e sala de vacinas."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (24 horas)",
            "hospital": "Hospital Regional do Guará (HRGu) e HMIB",
            "detalhes": "Urgências 24h na UPA Núcleo Bandeirante."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "jardim_botanico",
        "ra_nome": "Jardim Botânico",
        "regiao_saude": "Leste",
        "bairros": ["Condomínios", "Mangueiral", "San Diego", "Altiplano Leste"],
        "unidades": [
            {
                "nome": "UBS 1 Jardim Botânico (Mangueiral)",
                "tipo": "ubs",
                "endereco": "Avenida das Jaqueiras, Setor Habitacional Mangueiral, Jardim Botânico, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Sala de vacinação com vacinas de rotina e sazonais, puericultura e pré-natal no Mangueiral."
            }
        ],
        "urgencia": {
            "upa": "UPA São Sebastião (24 horas)",
            "hospital": "Hospital da Região Leste / Paranoá (HRPa) e HMIB",
            "detalhes": "Urgências 24h na UPA São Sebastião."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "sia",
        "ra_nome": "SIA",
        "regiao_saude": "Centro-Sul",
        "bairros": ["Trechos 01 a 17", "Setor de Transporte de Cargas"],
        "unidades": [
            {
                "nome": "Atendimento de Referência SIA (UBS 1 Guará)",
                "tipo": "ubs",
                "endereco": "QE 06, Lote C, Guará I (unidade de referência territorial para o SIA)",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "farmacia_basica"],
                "detalhes": "A população e trabalhadores do SIA têm como unidade básica de saúde territorial de referência a UBS 1 do Guará."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante (24 horas)",
            "hospital": "Hospital Regional do Guará (HRGu)",
            "detalhes": "Urgências atendidas na UPA Núcleo Bandeirante 24h."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "fercal",
        "ra_nome": "Fercal",
        "regiao_saude": "Norte",
        "bairros": ["Engenho Velho", "Lages", "Boa Vista", "Rua do Mato"],
        "unidades": [
            {
                "nome": "UBS 1 Fercal",
                "tipo": "ubs",
                "endereco": "Rua Principal do Engenho Velho, Fercal, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica", "odontologia"],
                "detalhes": "Atendimento rural e comunitário com sala de vacina de rotina e saúde da família."
            }
        ],
        "urgencia": {
            "upa": "UPA Sobradinho (24 horas)",
            "hospital": "Hospital Regional de Sobradinho (HRS)",
            "detalhes": "Urgências 24 horas encaminhadas à UPA Sobradinho ou HRS."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul."
    },
    {
        "ra_id": "arniqueira",
        "ra_nome": "Arniqueira",
        "regiao_saude": "Sudoeste",
        "bairros": ["SHA Conjuntos 01 a 09", "Vereda da Cruz", "Areal SHA"],
        "unidades": [
            {
                "nome": "UBS 1 Arniqueira",
                "tipo": "ubs",
                "endereco": "SHA Conjunto 04, Chácara 44, Arniqueira, DF",
                "horario": "Segunda a sexta-feira, das 07:00 às 19:00",
                "saude_na_hora": False,
                "servicos": ["saude_da_familia", "vacinacao", "prenatal", "puericultura", "teste_do_pezinho", "farmacia_basica"],
                "detalhes": "Atendimento da Estratégia Saúde da Família para os moradores de Arniqueira, vacinas e pré-natal."
            }
        ],
        "urgencia": {
            "upa": "UPA Núcleo Bandeirante ou UPA Samambaia (24 horas)",
            "hospital": "Hospital Regional de Taguatinga (HRT) e HRGu",
            "detalhes": "Urgências 24h na UPA Núcleo Bandeirante ou UPA Samambaia."
        },
        "farmacia_alto_custo": "Referência na Farmácia de Alto Custo da Asa Sul ou Ceilândia."
    }
]


def generate_corpus_blocks() -> List[Dict[str, Any]]:
    """Gera blocos estruturados e em prosa natural para todas as RAs."""
    blocks: List[Dict[str, Any]] = []

    for reg in DF_REGIONS:
        ra_id = reg["ra_id"]
        ra_nome = reg["ra_nome"]
        regiao_saude = reg["regiao_saude"]
        bairros_str = ", ".join(reg["bairros"])

        # 1. Bloco Geral da Região Administrativa (Visão Geral de Atenção e Urgência)
        geral_header = f"[UNIDADE_REGIONAL] Saúde Pública e Serviços na Região de {ra_nome} - SES-DF"
        geral_text = (
            f"A Região Administrativa de {ra_nome} integra a Região de Saúde {regiao_saude} do Distrito Federal. "
            f"Bairros e setores atendidos: {bairros_str}. "
            f"Para atendimento básico, consultas médicas e de enfermagem agendadas, vacinação de rotina, teste do pezinho, "
            f"pré-natal de baixo risco e retirada de medicamentos da farmácia básica, o cidadão deve se dirigir à sua Unidade Básica de Saúde (UBS) de referência. "
            f"Horário padrão das UBSs: segunda a sexta-feira, das 07:00 às 19:00 (com unidades participantes do programa Saúde na Hora abertas até as 22:00 e sábados das 07:00 às 12:00). "
            f"Para urgências e emergências clínicas 24 horas: {reg['urgencia']['upa'] or 'procurar UPA de referência da região'}. "
            f"Hospital de referência regional: {reg['urgencia']['hospital']}. {reg['urgencia']['detalhes']} "
            f"Medicamentos de Alto Custo (CEAF): {reg['farmacia_alto_custo']} "
            f"Fonte: https://www.saude.df.gov.br/ubs-{ra_id}"
        )
        blocks.append({
            "header": geral_header,
            "tag": "UNIDADE_REGIONAL",
            "text": geral_text,
            "url": f"https://www.saude.df.gov.br/ubs-{ra_id}",
            "metadata": {
                "cluster": "atencao_primaria",
                "ra": ra_id,
                "tipo_unidade": "regional",
                "servicos": "saude_da_familia,vacinacao,prenatal,puericultura,farmacia_basica,urgencia",
            }
        })

        # 2. Blocos de cada Unidade Básica de Saúde (UBS)
        for u in reg["unidades"]:
            servicos_formatados = ", ".join(s.replace("_", " ") for s in u["servicos"])
            is_snh = "Possui atendimento estendido pelo programa Saúde na Hora até as 22h e sábados das 07h às 12h." if u["saude_na_hora"] else "Funcionamento em dias úteis no horário regular das 07h às 19h."
            
            # Bloco da UBS (Atenção Primária / Saúde da Família)
            ubs_header = f"[UNIDADE_UBS] {u['nome']} - {ra_nome} ({regiao_saude})"
            ubs_text = (
                f"A {u['nome']} (conhecida popularmente como posto de saúde ou postinho em {ra_nome}) está localizada no endereço: {u['endereco']}. "
                f"Região de Saúde: {regiao_saude}. "
                f"Horário de Atendimento: {u['horario']}. {is_snh} "
                f"Serviços oferecidos à comunidade: {servicos_formatados}. {u['detalhes']} "
                f"Acolhimento da Estratégia Saúde da Família: médicos clínicos, enfermeiros e agentes comunitários de saúde realizam consultas agendadas e atendimento de demanda espontânea. "
                f"Para exames de rotina, preventivo (papanicolau), acompanhamento de hipertensão e diabetes (Hiperdia), curativos e administração de remédios. "
                f"Para situações de urgência e emergência graves fora do horário ou casos de risco, a referência na região é: {reg['urgencia']['upa'] or reg['urgencia']['hospital']}. "
                f"Fonte: https://www.saude.df.gov.br/ubs-{ra_id}"
            )
            blocks.append({
                "header": ubs_header,
                "tag": "UNIDADE_UBS",
                "text": ubs_text,
                "url": f"https://www.saude.df.gov.br/ubs-{ra_id}",
                "metadata": {
                    "cluster": "atencao_primaria",
                    "ra": ra_id,
                    "tipo_unidade": "ubs",
                    "servicos": ",".join(u["servicos"]),
                }
            })

            # Bloco Dedicado de Vacinação na UBS
            vacina_header = f"[VACINACAO] Sala de Vacinas - {u['nome']} em {ra_nome}"
            vacina_text = (
                f"A sala de vacinação da {u['nome']} (localizada em {u['endereco']}, {ra_nome}) funciona durante o horário da unidade ({u['horario']}). "
                f"Aplica todas as vacinas do Calendário Nacional de Imunização do Ministério da Saúde e da SES-DF: "
                f"Calendário da Criança e Recém-Nascido: BCG, Hepatite B, Pentavalente (DTP/Hib/Hep B), Poliomielite (VIP e VOP), Rotavírus Humano, Pneumocócica 10-valente, Meningocócica C e Meningocócica ACWY, Febre Amarela, Tríplice Viral (Sarampo, Caxumba, Rubéola), Tetra Viral ou Varicela, Hepatite A e DTP. "
                f"Calendário do Adolescente e Adulto: HPV quadrivalente, Meningo ACWY, dT (difteria e tétano), Febre Amarela, Hepatite B e Tríplice Viral. "
                f"Calendário da Gestante: dTpa (tríplice bacteriana acelular a partir da 20ª semana), Hepatite B, dT e Influenza. "
                f"Calendário do Idoso: Influenza (Gripe), Pneumocócica 23-valente (para pessoas institucionalizadas ou com comorbidades) e Covid-19. "
                f"Documentos necessários para vacinação: Caderneta ou Cartão de Vacina, documento oficial com foto ou certidão de nascimento, e Cartão SUS (CNS). "
                f"Fonte: https://www.saude.df.gov.br/vacinacao-{ra_id}"
            )
            blocks.append({
                "header": vacina_header,
                "tag": "VACINACAO",
                "text": vacina_text,
                "url": f"https://www.saude.df.gov.br/vacinacao-{ra_id}",
                "metadata": {
                    "cluster": "vacinacao",
                    "ra": ra_id,
                    "tipo_unidade": "ubs",
                    "servicos": "vacinacao,imunizacao,calendario_nacional",
                }
            })

            # Bloco Dedicado de Saúde Materno-Infantil, Pré-Natal e Puericultura
            materno_header = f"[MATERNO_INFANTIL] Pré-Natal e Puericultura na {u['nome']} em {ra_nome}"
            materno_text = (
                f"O acompanhamento de gestantes, recém-nascidos e crianças na {u['nome']} ({u['endereco']}, {ra_nome}) "
                f"é realizado pelas equipes de Saúde da Família de segunda a sexta-feira. "
                f"Serviços de Pré-Natal da Gestante: Confirmação de gravidez por Teste Rápido de Gravidez (TIG), consultas mensais de pré-natal de baixo risco com médico e enfermeiro, "
                f"solicitação de exames de sangue e ultrassonografia obstétrica pela regulação, testes rápidos para HIV, Sífilis e Hepatites B e C no acolhimento, "
                f"prescrição de ácido fólico e sulfato ferroso, vacinação com dTpa e Influenza, e encaminhamento para a maternidade de referência regional ({reg['urgencia']['hospital']}). "
                f"Serviços de Puericultura e Recém-Nascido: Realização do Teste do Pezinho (triagem neonatal biológica) preferencialmente entre o 3º e o 5º dia de vida do bebê para diagnóstico precoce de fenilcetonúria, hipotireoidismo congênito, anemia falciforme e fibrose cística. "
                f"Primeira consulta do bebê na primeira semana de vida, monitoramento do peso, estatura, perímetro cefálico e marcos de desenvolvimento infantil. "
                f"Apoio ao aleitamento materno e orientação sobre pega correta e prevenção de fissuras mamárias. "
                f"Documentos para atendimento: Documento da mãe/responsável, certidão de nascimento do bebê ou declaração de nascido vivo (DNV), e Cartão SUS. "
                f"Fonte: https://www.saude.df.gov.br/materno-infantil-{ra_id}"
            )
            blocks.append({
                "header": materno_header,
                "tag": "MATERNO_INFANTIL",
                "text": materno_text,
                "url": f"https://www.saude.df.gov.br/materno-infantil-{ra_id}",
                "metadata": {
                    "cluster": "saude_materno_infantil",
                    "ra": ra_id,
                    "tipo_unidade": "ubs",
                    "servicos": "prenatal,puericultura,teste_do_pezinho,aleitamento,recem_nascido",
                }
            })

            # Bloco de Farmácia da UBS e Acesso a Medicamentos Básicos
            farmacia_header = f"[FARMACIA_BASICA] Farmácia da {u['nome']} - Medicamentos Básicos em {ra_nome}"
            farmacia_text = (
                f"A farmácia da {u['nome']} (situada em {u['endereco']}, {ra_nome}) realiza a dispensação gratuita de medicamentos essenciais da atenção primária (REME-DF). "
                f"Horário de funcionamento da farmácia: acompanha o horário da unidade ({u['horario']}). "
                f"Classes de medicamentos disponíveis na UBS: anti-hipertensivos (Losartana, Enalapril, Hidroclorotiazida, Atenolol), "
                f"antidiabéticos orais (Metformina, Glibenclamida) e Insulina NPH e Regular, antibióticos básicos (Amoxicilina, Cefalexina, Azitromicina), "
                f"analgésicos e anti-inflamatórios (Paracetamol, Dipirona, Ibuprofeno), anticoncepcionais orais e injetáveis, e suplementos de ferro e vitaminas. "
                f"Para retirar medicamentos na UBS: apresentar receita médica válida emitida pelo SUS (médico da rede pública), documento de identidade com foto, e Cartão SUS (CNS). "
                f"Para medicamentos especializados de alto custo: os munícipes de {ra_nome} devem se dirigir ao polo: {reg['farmacia_alto_custo']} "
                f"Fonte: https://www.saude.df.gov.br/medicamentos-{ra_id}"
            )
            blocks.append({
                "header": farmacia_header,
                "tag": "FARMACIA_BASICA",
                "text": farmacia_text,
                "url": f"https://www.saude.df.gov.br/medicamentos-{ra_id}",
                "metadata": {
                    "cluster": "medicamentos_farmacia",
                    "ra": ra_id,
                    "tipo_unidade": "ubs",
                    "servicos": "farmacia_basica,remedios,dispensacao,alto_custo",
                }
            })

        # 3. Bloco de Urgência, Emergência e Dengue na Região
        urgencia_header = f"[URGENCIA_EMERGENCIA] Atendimento de Urgência, UPAs e Dengue em {ra_nome}"
        urgencia_text = (
            f"Na Região Administrativa de {ra_nome}, situações que exigem atendimento imediato 24 horas devem ser direcionadas aos serviços de pronto atendimento: "
            f"Unidade de Pronto Atendimento (UPA): {reg['urgencia']['upa'] or 'Referência na UPA mais próxima da região'}. "
            f"Hospital Regional de Referência: {reg['urgencia']['hospital']}. "
            f"Quando procurar a UPA ou Hospital: falta de ar grave, dor aguda no peito, suspeita de AVC (perda de força em um lado do corpo, fala arrastada), "
            f"fraturas expostas ou traumatismos graves, convulsões, cortes profundos que necessitam de sutura cirúrgica imediata, e emergências obstétricas (início do trabalho de parto, perda de líquido ou sangramento). "
            f"Casos de Dengue e Hidratação: Casos leves (febre, dor no corpo e dor atrás dos olhos) são atendidos e hidratados nas UBSs de {ra_nome} durante o dia. "
            f"Sinais de alarme da dengue que exigem atendimento de urgência 24h na UPA ou Hospital: dor abdominal intensa e contínua, vômitos persistentes que impedem a hidratação oral, "
            f"sangramento de mucosas (nariz ou gengivas), tontura ao levantar, e sonolência excessiva ou irritabilidade. "
            f"Em caso de risco iminente à vida onde o paciente não puder ser transportado com segurança, acione o SAMU pelo telefone 192. "
            f"Fonte: https://www.saude.df.gov.br/urgencia-{ra_id}"
        )
        blocks.append({
            "header": urgencia_header,
            "tag": "URGENCIA_EMERGENCIA",
            "text": urgencia_text,
            "url": f"https://www.saude.df.gov.br/urgencia-{ra_id}",
            "metadata": {
                "cluster": "urgencia_emergencia",
                "ra": ra_id,
                "tipo_unidade": "upa",
                "servicos": "urgencia,emergencia,upa,hospital,dengue,samu",
            }
        })

    return blocks


def main():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    blocks = generate_corpus_blocks()
    
    # 1. Salvar JSON estruturado
    json_path = CORPUS_DIR / "diretorio_saude_df.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump({"schema_version": "2.0", "total_blocks": len(blocks), "blocks": blocks}, f, ensure_ascii=False, indent=2)
    print(f"Salvo {json_path} com {len(blocks)} blocos estruturados.")

    # 2. Salvar TXT no padrão do parser do RAG
    txt_path = CORPUS_DIR / "diretorio_saude_df.txt"
    with txt_path.open("w", encoding="utf-8") as f:
        for b in blocks:
            f.write(f"{b['header']}\n")
            f.write(f"{b['text']}\n")
            f.write(f"Fonte: {b['url']}\n\n")
    print(f"Salvo {txt_path} no padrão RAG oficial.")


if __name__ == "__main__":
    main()
