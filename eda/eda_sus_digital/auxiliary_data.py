import pandas as pd

# Tabela de população por RA (Censo 2022 IBGE)
populacao_ra_2022 = pd.DataFrame([
    {"RA": "Ceilândia", "Populacao": 287023},
    {"RA": "Samambaia", "Populacao": 218840},
    {"RA": "Plano Piloto", "Populacao": 198697},
    {"RA": "Taguatinga", "Populacao": 193367},
    {"RA": "Planaltina", "Populacao": 179960},
    {"RA": "Gama", "Populacao": 139467},
    {"RA": "Águas Claras", "Populacao": 128486},
    {"RA": "Guará", "Populacao": 120641},
    {"RA": "Santa Maria", "Populacao": 116622},
    {"RA": "Recanto das Emas", "Populacao": 115550},
    {"RA": "Riacho Fundo II", "Populacao": 105210},
    {"RA": "Sol Nascente/Pôr do Sol", "Populacao": 101866},
    {"RA": "São Sebastião", "Populacao": 98612},
    {"RA": "Vicente Pires", "Populacao": 96871},
    {"RA": "Sobradinho II", "Populacao": 82785},
    {"RA": "Jardim Botânico", "Populacao": 77767},
    {"RA": "Sobradinho", "Populacao": 72273},
    {"RA": "Itapoã", "Populacao": 65408},
    {"RA": "Riacho Fundo", "Populacao": 65658},
    {"RA": "Paranoá", "Populacao": 63923},
    {"RA": "Brazlândia", "Populacao": 55561},
    {"RA": "Sudoeste/Octogonal", "Populacao": 44354},
    {"RA": "Arniqueira", "Populacao": 42320},
    {"RA": "SCIA", "Populacao": 36042},
    {"RA": "Lago Norte", "Populacao": 32379},
    {"RA": "Lago Sul", "Populacao": 26244},
    {"RA": "Cruzeiro", "Populacao": 25741},
    {"RA": "Park Way", "Populacao": 22289},
    {"RA": "Núcleo Bandeirante", "Populacao": 21636},
    {"RA": "Candangolândia", "Populacao": 14040},
    {"RA": "Fercal", "Populacao": 10268},
    {"RA": "Varjão", "Populacao": 8609},
    {"RA": "SIA", "Populacao": 5131}
])

# De-Para: RA -> Região de Saúde
de_para_regioes = {
    "Central": ["Plano Piloto", "Cruzeiro", "Sudoeste/Octogonal", "Lago Norte", "Lago Sul", "Varjão"],
    "Centro-Sul": ["Candangolândia", "Guará", "Park Way", "Núcleo Bandeirante", "Riacho Fundo", "Riacho Fundo II", "SIA", "SCIA"],
    "Norte": ["Planaltina", "Sobradinho", "Sobradinho II", "Fercal"], # Arapoanga incluso em Planaltina no censo
    "Oeste": ["Ceilândia", "Brazlândia", "Sol Nascente/Pôr do Sol"],
    "Sul": ["Gama", "Santa Maria"],
    "Sudoeste": ["Taguatinga", "Samambaia", "Águas Claras", "Vicente Pires", "Recanto das Emas", "Arniqueira"],
    "Leste": ["Paranoá", "Itapoã", "São Sebastião", "Jardim Botânico"]
}

# Consolidar a população por Região de Saúde
pop_regiao_saude = []
for regiao, ras in de_para_regioes.items():
    pop_total = populacao_ra_2022[populacao_ra_2022['RA'].isin(ras)]['Populacao'].sum()
    pop_regiao_saude.append({"Regiao_Saude": regiao, "Populacao_2022": pop_total})

df_pop_regiao = pd.DataFrame(pop_regiao_saude)

