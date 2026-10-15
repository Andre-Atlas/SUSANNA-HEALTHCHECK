'use client';

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { apiFetch, AUTH_EXPIRED_EVENT } from '@/lib/apiClient';
import { clearLegacyCitizen, clearToken, loadToken, saveToken } from '@/lib/auth';
import type { AuthResponse, CitizenProfile, ProfilePatch, RegisterPayload } from '@/lib/types';

type AuthStatus = 'loading' | 'anon' | 'authed';
export type AuthMode = 'login' | 'register';

interface AuthContextValue {
  status: AuthStatus;
  citizen: CitizenProfile | null;
  login: (cpf: string, senha: string, lembrar: boolean) => Promise<CitizenProfile>;
  register: (data: RegisterPayload) => Promise<CitizenProfile>;
  update: (patch: ProfilePatch) => Promise<CitizenProfile>;
  logout: (everywhere?: boolean) => Promise<void>;
  changePassword: (atual: string, nova: string) => Promise<void>;
  deleteAccount: (senha: string) => Promise<void>;
  // Diálogo de entrada/cadastro e painel de perfil, abertos de qualquer tela
  authDialog: AuthMode | null;
  openAuth: (mode?: AuthMode) => void;
  closeAuth: () => void;
  profileOpen: boolean;
  setProfileOpen: (open: boolean) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [citizen, setCitizen] = useState<CitizenProfile | null>(null);
  const [authDialog, setAuthDialog] = useState<AuthMode | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);

  const signOutLocally = useCallback(() => {
    clearToken();
    setCitizen(null);
    setStatus('anon');
  }, []);

  useEffect(() => {
    clearLegacyCitizen();
    if (!loadToken()) {
      // O token vive no armazenamento do navegador, indisponível durante o SSR
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStatus('anon');
      return;
    }
    apiFetch<CitizenProfile>('/api/citizen/me')
      .then((me) => {
        setCitizen(me);
        setStatus('authed');
      })
      .catch(signOutLocally);
  }, [signOutLocally]);

  useEffect(() => {
    window.addEventListener(AUTH_EXPIRED_EVENT, signOutLocally);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, signOutLocally);
  }, [signOutLocally]);

  const accept = useCallback((res: AuthResponse) => {
    saveToken({ token: res.token, expires_at: res.expires_at, remember: res.remember });
    setCitizen(res.citizen);
    setStatus('authed');
    return res.citizen;
  }, []);

  const login = useCallback(
    async (cpf: string, senha: string, lembrar: boolean) =>
      accept(await apiFetch<AuthResponse>('/api/citizen/login', { method: 'POST', json: { cpf, senha, lembrar } })),
    [accept],
  );

  const register = useCallback(
    async (data: RegisterPayload) =>
      accept(await apiFetch<AuthResponse>('/api/citizen/register', { method: 'POST', json: data })),
    [accept],
  );

  const update = useCallback(async (patch: ProfilePatch) => {
    const me = await apiFetch<CitizenProfile>('/api/citizen/me', { method: 'PATCH', json: patch });
    setCitizen(me);
    return me;
  }, []);

  const logout = useCallback(
    async (everywhere = false) => {
      try {
        await apiFetch(everywhere ? '/api/citizen/logout-all' : '/api/citizen/logout', { method: 'POST' });
      } catch {
        /* encerra localmente mesmo sem rede */
      }
      signOutLocally();
    },
    [signOutLocally],
  );

  const changePassword = useCallback(async (senha_atual: string, nova_senha: string) => {
    await apiFetch('/api/citizen/me/password', { method: 'POST', json: { senha_atual, nova_senha } });
  }, []);

  const deleteAccount = useCallback(
    async (senha: string) => {
      await apiFetch('/api/citizen/me', { method: 'DELETE', json: { senha } });
      signOutLocally();
    },
    [signOutLocally],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      citizen,
      login,
      register,
      update,
      logout,
      changePassword,
      deleteAccount,
      authDialog,
      openAuth: (mode = 'login') => setAuthDialog(mode),
      closeAuth: () => setAuthDialog(null),
      profileOpen,
      setProfileOpen,
    }),
    [status, citizen, login, register, update, logout, changePassword, deleteAccount, authDialog, profileOpen],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de <AuthProvider>');
  return ctx;
}
