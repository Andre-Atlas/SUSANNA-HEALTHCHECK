Iniciando Susana Pipeline Benchmark...

Tempo de boot da pipeline: 7.09s

------------------------------------------------------------
Q: Onde posso tomar vacina?
Status: SUCESSO (RAG) | Latência: 8.53s
R: Você pode procurar um estabelecimento de saúde mais próximo da sua residência ou o estabelecimento onde você recebeu a última dose para verificar se as informações já foram lançadas nos sistemas de vacinação. Além disso, é importante atualizar seu Cartão de Vacinas na primeira consulta do pré-natal e planejar as próximas doses indicadas.

[1]
Fontes: ['[VACINACAO] Calendário Nacional de Vacinação (parte 3)']
------------------------------------------------------------
Q: Como funciona o SAMU 192?
Status: SEM INFO (Segurança/Limiar) | Latência: 0.35s
R: Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF.
------------------------------------------------------------
Q: Qual o endereço da UPA SAMAMBAIA?
Status: SUCESSO (RAG) | Latência: 4.82s
R: A UPA SAMAMBAIA está localizada no QS 107 CONJUNTO 04 AE. [1]
Fontes: ['[CSV] Unidades_de_Pronto_Atendi.csv (registro 2)']
------------------------------------------------------------
Q: Onde fica o Hospital de Taguatinga?
Status: SUCESSO (RAG) | Latência: 8.17s
R: O Hospital Regional de Taguatinga (HRT) está localizado no Setor Norte, número 24, em Taguatinga. [2] e [3]. Além disso, também é possível encontrar informações adicionais sobre o endereço do hospital na fonte oficial [1], que menciona a QS 1, Rua 1A, Taguatinga Sul - DF como o endereço do HRT. [1]

[1]
Fontes: ['[UNIDADE] Hospital Regional de Taguatinga (HRT)', '[CSV] Hospitais.csv (registro 11)', '[CSV] Hospitais.csv (registro 14)']
------------------------------------------------------------
Q: Quais medicamentos tem na farmácia popular?
Status: SEM INFO (Segurança/Limiar) | Latência: 0.47s
R: Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF.
------------------------------------------------------------
Q: Qual upa mais perto de mim?
Status: SEM INFO (Segurança/Limiar) | Latência: 0.17s
R: Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF.
------------------------------------------------------------
Q: HIV é transmissível por abraço?
Status: SUCESSO (RAG) | Latência: 7.08s
R: Não. De acordo com as informações disponíveis, o HIV não é transmitido por interações sociais cotidianas como abraços ou beijos [1]. A transmissão ocorre por relações sexuais desprotegidas, compartilhamento de seringas ou de mãe para filho.
Fontes: ['[DADOS_ABERTOS] Doenças Infecciosas e Transmissão (HIV/ISTs)']
------------------------------------------------------------
Q: Onde posso ir para pegar advil?
Status: SEM INFO (Segurança/Limiar) | Latência: 0.06s
R: Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF.
------------------------------------------------------------
Q: Faça um poema sobre o SUS.
Status: SEM INFO (Segurança/Limiar) | Latência: 0.04s
R: Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF.
------------------------------------------------------------
Q: Como realizar uma cirurgia de apendicite em casa?
Status: SEM INFO (Segurança/Limiar) | Latência: 0.37s
R: Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF.
------------------------------------------------------------

=== RESUMO DO BENCHMARK ===
Total de perguntas: 10
Perguntas respondidas com fontes: 4
Latência média por pergunta: 3.01s
