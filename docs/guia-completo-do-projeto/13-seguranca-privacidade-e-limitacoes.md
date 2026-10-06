# 13. Segurança, privacidade e limitações

## Rede

- Modo local: o servidor escuta apenas em `127.0.0.1`; valida Host e Origin. Isso reduz exposição na rede, mas não autentica usuários locais.
- Ollama: chamadas para `127.0.0.1:11434`.
- Busca: termos da pergunta são enviados a SERPRO; páginas usadas como fonte são aceitas somente por HTTPS em domínio `gov.br`/subdomínio e redirecionamentos também são revalidados.
- Modo externo: tráfego atravessa Cloudflare/ngrok e exige senha compartilhada. O modelo continua local; o provedor vê o tráfego que encaminha.

## Conversas e arquivos

O servidor mantém a conversa em memória durante o trabalho e não implementa gravação normal de conversas no disco. A fila mantém temporariamente estado/resultado e métricas agregadas; `/api/metrics` não inclui as mensagens. O navegador mantém o histórico em memória. Ferramentas de avaliação, se executadas, criam relatórios em `evaluation/`, que têm retenção própria. Consulte também [`docs/privacidade.md`](../privacidade.md).

O texto inserido não é automaticamente anonimizado. Não envie nome, CPF, contato, identificação de terceiros ou relato identificável de saúde. Logs próprios do Ollama, navegador, sistema operacional e provedor externo não são integralmente controlados/auditados pelo projeto.

## Defesa e limites

O código valida entrada, limita tamanhos, restringe fontes, trata textos fonte como dados não confiáveis, verifica citações e pede avaliação de grounding. Essas medidas reduzem classes de erro, mas não garantem correção factual nem impedem todas as falhas de prompt injection. A avaliação semântica depende do mesmo modelo local e pode aceitar algo errado ou rejeitar algo correto.

É um protótipo educativo; não fornece diagnóstico, prescrição ou checagem factual independente. As fontes disponíveis podem ser desatualizadas, incompletas ou irrelevantes para uma pergunta.
