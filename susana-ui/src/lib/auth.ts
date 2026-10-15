// Armazenamento do token de sessão.
// "Lembrar de mim" → localStorage (sobrevive ao fechar o navegador);
// caso contrário → sessionStorage (encerra ao fechar a aba).

const TOKEN_KEY = 'susana_auth';
const LEGACY_CITIZEN_KEY = 'susana_citizen';

export interface StoredToken {
  token: string;
  expires_at: string;
  remember: boolean;
}

function safeStorage(kind: 'local' | 'session'): Storage | null {
  try {
    return kind === 'local' ? window.localStorage : window.sessionStorage;
  } catch {
    return null;
  }
}

export function saveToken(t: StoredToken): void {
  const target = safeStorage(t.remember ? 'local' : 'session');
  const other = safeStorage(t.remember ? 'session' : 'local');
  other?.removeItem(TOKEN_KEY);
  target?.setItem(TOKEN_KEY, JSON.stringify(t));
}

export function loadToken(): StoredToken | null {
  for (const kind of ['local', 'session'] as const) {
    const store = safeStorage(kind);
    const raw = store?.getItem(TOKEN_KEY);
    if (!raw) continue;
    try {
      const parsed = JSON.parse(raw) as StoredToken;
      if (new Date(parsed.expires_at).getTime() > Date.now()) return parsed;
    } catch {
      /* token corrompido: descarta */
    }
    store?.removeItem(TOKEN_KEY);
  }
  return null;
}

export function getToken(): string | null {
  return loadToken()?.token ?? null;
}

export function clearToken(): void {
  safeStorage('local')?.removeItem(TOKEN_KEY);
  safeStorage('session')?.removeItem(TOKEN_KEY);
}

/** Remove o perfil antigo guardado em texto puro pelo cadastro anterior. */
export function clearLegacyCitizen(): void {
  safeStorage('local')?.removeItem(LEGACY_CITIZEN_KEY);
}
