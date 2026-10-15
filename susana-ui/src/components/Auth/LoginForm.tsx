'use client';

import React, { useState } from 'react';
import { ArrowRight, IdCard } from 'lucide-react';
import { Checkbox, Field, PasswordField } from '@/components/Auth/fields';
import { useAuth } from '@/context/AuthProvider';
import { isValidCpf, maskCpf, onlyDigits } from '@/lib/ptBR';

interface LoginFormProps {
  onDone: (firstName: string) => void;
  onSwitchToRegister: () => void;
  onSkip: () => void;
}

export function LoginForm({ onDone, onSwitchToRegister, onSkip }: LoginFormProps) {
  const { login } = useAuth();
  const [cpf, setCpf] = useState('');
  const [senha, setSenha] = useState('');
  const [lembrar, setLembrar] = useState(true);
  const [touched, setTouched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [forgot, setForgot] = useState(false);

  const cpfError = touched && cpf && !isValidCpf(cpf) ? 'CPF inválido. Confira os números.' : null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!isValidCpf(cpf) || !senha) return;
    setBusy(true);
    setError(null);
    try {
      const me = await login(onlyDigits(cpf), senha, lembrar);
      onDone(me.primeiro_nome);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível entrar.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="sx-form" onSubmit={submit} noValidate>
      <Field
        label="CPF"
        icon={<IdCard size={18} aria-hidden />}
        inputMode="numeric"
        autoComplete="username"
        placeholder="000.000.000-00"
        value={cpf}
        onChange={(e) => setCpf(maskCpf(e.target.value))}
        onBlur={() => setTouched(true)}
        error={cpfError}
        autoFocus
      />
      <PasswordField
        label="Senha"
        autoComplete="current-password"
        placeholder="Sua senha"
        value={senha}
        onChange={(e) => setSenha(e.target.value)}
      />
      <div className="sx-line">
        <Checkbox label="Lembrar de mim" checked={lembrar} onChange={(e) => setLembrar(e.target.checked)} />
        <button type="button" className="sx-link" onClick={() => setForgot((f) => !f)} aria-expanded={forgot}>
          Esqueci minha senha
        </button>
      </div>
      {forgot && (
        <p className="sx-legal" role="note">
          A recuperação automática ainda não está disponível. Você pode criar uma nova conta ou continuar usando a
          SUSANNA sem cadastro — todas as informações públicas seguem acessíveis.
        </p>
      )}
      {lembrar && <p className="sx-legal">Você continuará conectado neste aparelho por 30 dias.</p>}
      {error && (
        <div className="sx-alert" role="alert">
          {error}
        </div>
      )}
      <button className="sx-btn block" type="submit" disabled={busy}>
        {busy ? 'Entrando…' : 'Entrar'}
        <span className="arrow">
          <ArrowRight size={16} aria-hidden />
        </span>
      </button>
      <div className="sx-divider">ou</div>
      <div className="sx-line" style={{ justifyContent: 'center' }}>
        <span className="sx-legal">Ainda não tem conta?</span>
        <button type="button" className="sx-link" onClick={onSwitchToRegister}>
          Criar conta
        </button>
        <span className="sx-legal">·</span>
        <button type="button" className="sx-link" onClick={onSkip}>
          Continuar sem conta
        </button>
      </div>
    </form>
  );
}
