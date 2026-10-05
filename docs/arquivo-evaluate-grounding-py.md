# `evaluate_grounding.py`

Executa casos sintéticos contra a função de revisão documental (`verify_grounding`) do servidor. Os cenários verificam, por exemplo, paráfrases sustentadas, negações, alegações extras e conflitos.

Usa o Ollama para revisar os casos e grava um relatório em `evaluation/`. É uma avaliação do comportamento do revisor, não uma avaliação clínica nem parte automática de toda conversa.
