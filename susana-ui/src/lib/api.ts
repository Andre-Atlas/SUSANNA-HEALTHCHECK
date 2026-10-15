/**
 * Configuração centralizada da URL da API do SUS Digital (FastAPI Backend)
 * =========================================================================
 * Regra de resolução automática:
 * 1. Se NEXT_PUBLIC_API_URL estiver definida (ex: no Vercel ou .env), usa ela.
 * 2. Se estiver rodando no navegador sob proxy reverso (ex: Caddy em produção unificando as portas),
 *    usa caminho relativo '' para que o navegador envie direto para a mesma origem (/api/...).
 * 3. Em desenvolvimento local isolado (porta 3000), aponta para 'http://localhost:8000'.
 */

export const getApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL !== undefined && process.env.NEXT_PUBLIC_API_URL !== '') {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, '');
  }
  // No navegador, usa caminho relativo '' pois o Next.js (em dev) e Caddy (em prod)
  // fazem o proxy reverso transparente para o FastAPI na rota /api/*
  if (typeof window !== 'undefined') {
    return '';
  }
  return 'http://127.0.0.1:8000';
};

export const API_BASE_URL = getApiBaseUrl();

export const buildApiUrl = (endpoint: string): string => {
  const base = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${base}${cleanEndpoint}`;
};

export const createApiUrl = (endpoint: string): URL => {
  const base = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  if (base.startsWith('http://') || base.startsWith('https://')) {
    return new URL(`${base}${cleanEndpoint}`);
  }
  const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';
  return new URL(`${origin}${cleanEndpoint}`);
};
