# Specs: Landing page

- **MUST** exibir o mascote em 3D no hero quando houver WebGL e o usuário não pedir movimento reduzido.
- **MUST** exibir a imagem oficial (`/images/suzanna-hero.webp`) enquanto o 3D carrega, sem WebGL e com `prefers-reduced-motion: reduce`.
- **MUST NOT** carregar Three.js no bundle inicial.
- **MUST** pausar a renderização quando o mascote sai da tela ou a aba fica oculta.
- **MUST** marcar como "Exemplo" os cartões com dados ilustrativos.
- **MUST** oferecer o vídeo com controles nativos, pôster, capítulos acionáveis por teclado e resumo em texto.

## Cenários

**Cenário:** WebGL disponível.
- **WHEN** o visitante abre a landing.
- **THEN** a imagem oficial aparece primeiro.
- **AND** o canvas 3D assume (`data-mascot="ready"`) e o mascote acena.

**Cenário:** Movimento reduzido ou sem WebGL.
- **WHEN** o navegador pede `prefers-reduced-motion: reduce` ou não cria contexto WebGL.
- **THEN** não existe `<canvas>` no palco e a imagem oficial permanece visível.

**Cenário:** Capítulo do vídeo.
- **WHEN** o visitante aciona o capítulo "IA aplicada".
- **THEN** o vídeo vai para 21,94 s e toca.
