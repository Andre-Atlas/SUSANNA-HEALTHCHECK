# `answer_policy.py`

Contém verificações determinísticas usadas para controlar respostas: detecta instruções suspeitas dentro de fontes, normaliza e valida citações, identifica abstenções, separa parágrafos e valida o resultado estruturado do revisor.

`server.py` aplica essas funções antes de devolver uma resposta. Elas ajudam a rejeitar problemas de formato e de referência, mas não substituem revisão humana nem provam que uma informação de saúde é verdadeira.
