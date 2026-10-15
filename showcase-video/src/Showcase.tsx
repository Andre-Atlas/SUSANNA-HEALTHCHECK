import React from 'react';
import { AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { Backdrop } from './components/Backdrop';
import { ProgressNav } from './components/ProgressNav';
import { SceneShell } from './components/SceneShell';
import { AIPipeline } from './scenes/AIPipeline';
import { Challenges } from './scenes/Challenges';
import { Intro } from './scenes/Intro';
import { Problem } from './scenes/Problem';
import { Product } from './scenes/Product';
import { Outro, Results } from './scenes/Results';
import { fontFamily } from './theme';
import { FPS, T } from './timing';

export const Showcase: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  // Fade final da imagem para o fundo
  const fadeOut = interpolate(frame, [durationInFrames - 24, durationInFrames - 2], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ fontFamily }}>
      <Backdrop />
      <AbsoluteFill style={{ opacity: fadeOut }}>
        <SceneShell from={T.intro} to={T.problem}>
          <Intro />
        </SceneShell>
        <SceneShell from={T.problem} to={T.product}>
          <Problem />
        </SceneShell>
        <SceneShell from={T.product} to={T.ai}>
          <Product />
        </SceneShell>
        <SceneShell from={T.ai} to={T.challenges}>
          <AIPipeline />
        </SceneShell>
        <SceneShell from={T.challenges} to={T.results}>
          <Challenges />
        </SceneShell>
        <SceneShell from={T.results} to={T.outro}>
          <Results />
        </SceneShell>
        <SceneShell from={T.outro} to={T.end} holdOut>
          <Outro />
        </SceneShell>
        <ProgressNav />
      </AbsoluteFill>
      <Audio
        src={staticFile('trilha.mp3')}
        volume={(f) =>
          interpolate(f, [0, 0.5 * FPS], [0, 1], { extrapolateRight: 'clamp' }) *
          interpolate(f, [durationInFrames - 1.5 * FPS, durationInFrames], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
        }
      />
    </AbsoluteFill>
  );
};
