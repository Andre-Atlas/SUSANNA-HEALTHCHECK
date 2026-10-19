# Proposal: Landing page com mascote 3D e vídeo showcase

## Por Que (Why)
A landing atual (`#L` em `susana-ui/src/app/page.tsx`) mostra a SUSANNA como imagem estática e não apresenta o vídeo showcase do projeto. O guia de identidade visual prevê movimento sutil e vidro sobre azul; a página só cumpre isso em parte.

## O Que (What)
1. **Mascote 3D animado no hero** (`components/Mascot3D`): modelo procedural em Three.js, construído em código a partir da imagem `suzanna-poses.jpg`, carregado sob demanda.
2. **Estilo da página** alinhado ao guia: palco de vidro, selo "Exemplo" nos cartões ilustrativos, cabeçalho de seção, indicadores, foco visível, `prefers-reduced-motion`.
3. **Seção de vídeo** "Veja a SUSANNA em ação" (`components/Landing/VideoShowcase`): vídeo recodificado (1080p e 720p) com pôster e capítulos clicáveis.
4. **Teste de fumaça** (`npm run smoke`) com Playwright.

Fora de escopo: `site/`, plataforma `#A`, backend, `showcase-video/`, remoção do código morto `components/Landing/LandingPage.tsx`.

## Impacto / Riscos
- **Semelhança com o Zé Gotinha:** o guia (p. 4) pede confirmar originalidade e direito de uso antes de divulgar. O modelo 3D herda esse ponto; não é resolvido aqui.
- **Fidelidade:** é uma aproximação estilizada por código, não idêntica ao render fotorrealista.
- **Peso:** Three.js fica num chunk carregado sob demanda (~170 KB gzip); o JS inicial cresce cerca de 2,6 KB gzip. O vídeo adiciona ~7,3 MB ao repositório.
- **WebGL ausente ou movimento reduzido:** a imagem oficial é exibida no lugar do 3D.
