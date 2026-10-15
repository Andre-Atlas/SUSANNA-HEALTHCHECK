// Fronteiras das cenas alinhadas à trilha "The Open Door" (análise de energia/onsets):
// introdução calma até 7,94 s (entrada da batida, grade de 0,5 s), respiros em ~22–24 s
// e ~38–40 s, novo ataque em 42,70 s; a música se encerra por volta de 56,5 s.
export const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);

export const T = {
  intro: s(0),
  problem: s(2.94),
  product: s(7.94),
  productMap: s(12.44),
  productAgenda: s(16.94),
  ai: s(21.94),
  challenges: s(33.94),
  results: s(42.7),
  outro: s(53.94),
  end: s(57.0),
};

export const TOTAL_FRAMES = T.end;
// Sobreposição entre cenas (transição suave centrada no corte)
export const XF = 24;
// Cada lado da troca dura HALF quadros: a cena sai antes do corte e a próxima entra depois dele
export const HALF = 12;

export const SECTIONS = [
  { label: 'Contexto', from: T.problem },
  { label: 'Produto', from: T.product },
  { label: 'IA aplicada', from: T.ai },
  { label: 'Desafios', from: T.challenges },
  { label: 'Resultados', from: T.results },
];
