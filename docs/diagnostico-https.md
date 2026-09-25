# Diagnóstico HTTPS — 25/09/2026

Destino: `be54-164-41-98-2.ngrok-free.app:443`.

Verificações realizadas sem senha, token ou perguntas:

- O log ngrok registra sessão estabelecida e túnel iniciado.
- DNS resolve e TCP 443 conecta. Uma tentativa curl sofreu reset no handshake.
- Em uma tentativa OpenSSL, o certificado apresentado tem assunto
  `CN=*.ngrok-free.app` e emissor `O=Fortinet`,
  `CN=FG3K2D3Z16800349`.
- Validação OpenSSL: código 21, `unable to verify the first certificate`,
  com erro 20, `unable to get local issuer certificate`.
- O Chrome também apresenta `NET::ERR_CERT_AUTHORITY_INVALID` e identifica Fortinet.

As evidências confirmam certificado apresentado por Fortinet e falha de confiança
na cadeia nesse acesso. Não comprovam que o domínio está autorizado no filtro:
mesmo após corrigir a confiança pode haver uma política de bloqueio a verificar.

## Encaminhamento ao administrador

Solicitação: verificar a política de acesso ao domínio acima e a cadeia de
certificados da inspeção HTTPS no Mac PBIA01. Se a inspeção é autorizada, fornecer
ou distribuir por gestão institucional a CA correta, com fingerprint SHA-256
confirmado por canal oficial. Alternativamente, avaliar exceção restrita de
inspeção para esse destino conforme a política da instituição.

Não instalar como raiz o certificado de site capturado, não confiar em CA baixada
de origem não autenticada e não desativar a validação TLS. Nenhum certificado ou
configuração Fortinet foi alterado nesta investigação.

Após a correção, testar HTTPS sem exceções de certificado, confirmar 401 sem
credencial e 200 com credencial válida; então testar uma pergunta sintética.
