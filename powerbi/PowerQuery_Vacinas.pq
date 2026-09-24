let
    Fonte = Csv.Document(
        File.Contents("dados_vacinas_aplicadas-24092026-anos_2026-meses_08.csv"),
        [Delimiter = ",", Columns = 27, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(
        Cabecalhos,
        {
            {"i_ano_compt", Int64.Type},
            {"i_mes_compt", Int64.Type},
            {"i_estab_cnes", Int64.Type},
            {"i_sigla_estab_cnes", type text},
            {"i_ra_ses_desc", type text},
            {"i_desc_regiao_saude", type text},
            {"i_ine", type text},
            {"i_tipo_equipe", type text},
            {"i_desc_equipe", type text},
            {"i_tipo_ficha", type text},
            {"i_cat_prof", type text},
            {"i_desc_cbo", type text},
            {"i_imunobiologico", type text},
            {"i_estrategia_vacinacao", type text},
            {"i_dose_imunobiologico", type text},
            {"i_lote", type text},
            {"i_fabricante", type text},
            {"i_tipo_origem", type text},
            {"i_dt_inicial_atendimento", type date},
            {"i_dt_final_atendimento", type date},
            {"i_local_atendimento", type text},
            {"i_faixa_etaria", type text},
            {"i_sexo", type text},
            {"i_viajante", Int64.Type},
            {"i_comunicante_hanseniase", type number},
            {"i_gestante", type number},
            {"i_puerpera", type number}
        },
        "pt-BR"
    ),
    TextoVazioComoNulo = Table.ReplaceValue(
        Tipos,
        "",
        null,
        Replacer.ReplaceValue,
        {"i_ine", "i_desc_equipe", "i_fabricante", "i_lote", "i_gestante", "i_puerpera"}
    )
in
    TextoVazioComoNulo