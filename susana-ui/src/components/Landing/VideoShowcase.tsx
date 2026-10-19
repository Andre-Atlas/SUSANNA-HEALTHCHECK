'use client';

import { useRef, useState } from 'react';

const CHAPTERS = [
  { t: 2.94, label: 'Contexto', text: 'A informação de saúde do DF está espalhada em vários sites.' },
  { t: 7.94, label: 'Produto', text: 'Uma assistente que responde com fontes oficiais.' },
  { t: 21.94, label: 'IA aplicada', text: 'RAG local, aterrado em dados públicos do SUS.' },
  { t: 33.94, label: 'Desafios', text: 'O que tornou o projeto difícil.' },
  { t: 42.7, label: 'Resultados', text: 'Pronta para o cidadão, com 27 testes automatizados.' },
];

export function VideoShowcase() {
  const ref = useRef<HTMLVideoElement>(null);
  const [active, setActive] = useState(-1);

  const jump = (i: number) => {
    const v = ref.current;
    if (!v) return;
    v.currentTime = CHAPTERS[i].t;
    void v.play().catch(() => {});
    setActive(i);
  };

  const onTime = () => {
    const v = ref.current;
    if (!v) return;
    let idx = -1;
    CHAPTERS.forEach((c, i) => {
      if (v.currentTime >= c.t - 0.05) idx = i;
    });
    setActive(idx);
  };

  return (
    <section id="video" className="showcase" aria-labelledby="video-title">
      <div className="showcase-head rv">
        <div className="eyebrow">Showcase</div>
        <h2 id="video-title">
          Veja a <em>SUSANNA</em> em ação
        </h2>
        <p>Um minuto para entender o problema, a solução e os resultados do projeto.</p>
      </div>

      <div className="showcase-frame glass rv">
        <video
          ref={ref}
          controls
          playsInline
          preload="metadata"
          poster="/video/susana-showcase-poster.webp"
          onTimeUpdate={onTime}
          aria-label="Vídeo de apresentação da SUSANNA"
          aria-describedby="video-desc"
        >
          <source src="/video/susana-showcase-1080.mp4" type="video/mp4" media="(min-width: 900px)" />
          <source src="/video/susana-showcase-720.mp4" type="video/mp4" />
          Seu navegador não reproduz vídeo. O resumo do conteúdo está logo abaixo.
        </video>
      </div>

      <ul className="chapters rv" aria-label="Capítulos do vídeo">
        {CHAPTERS.map((c, i) => (
          <li key={c.label}>
            <button type="button" className={active === i ? 'on' : ''} onClick={() => jump(i)} aria-current={active === i ? 'step' : undefined}>
              <i>{String(i + 1).padStart(2, '0')}</i>
              <b>{c.label}</b>
            </button>
          </li>
        ))}
      </ul>

      <p id="video-desc" className="showcase-desc rv">
        {CHAPTERS.map((c) => `${c.label}: ${c.text}`).join(' ')}
      </p>
    </section>
  );
}
