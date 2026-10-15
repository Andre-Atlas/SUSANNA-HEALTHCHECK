import { Easing } from 'remotion';
import { loadFont } from '@remotion/google-fonts/Inter';

// Tokens canônicos do Design System "Liquid Blue & Glassmorphism" (susana-ui/docs)
export const C = {
  bg: '#f5f9ff',
  ink: '#0a1b3d',
  mut: '#5b6b8c',
  b1: '#1e40af',
  b2: '#2563eb',
  b3: '#60a5fa',
  b4: '#dbeafe',
  ok: '#16a34a',
  warn: '#d97706',
  bad: '#dc2626',
  violet: '#7c3aed',
};

export const { fontFamily } = loadFont('normal', {
  weights: ['300', '400', '500', '600', '700'],
  subsets: ['latin', 'latin-ext'],
});

export const glass: React.CSSProperties = {
  background: 'rgba(255,255,255,0.58)',
  backdropFilter: 'blur(22px) saturate(170%)',
  WebkitBackdropFilter: 'blur(22px) saturate(170%)',
  border: '1px solid rgba(255,255,255,0.75)',
  boxShadow: '0 8px 30px rgba(30,64,175,0.10), inset 0 1px 0 #fff',
};

export const EASE = Easing.bezier(0.2, 0.8, 0.2, 1);
