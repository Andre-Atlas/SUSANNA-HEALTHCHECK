'use client';

import React, { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, Check, IdCard, User } from 'lucide-react';
import { Checkbox, Field, PasswordField } from '@/components/Auth/fields';
import {
  ConditionsChecklist,
  draftToPatch,
  LocationCard,
  ProfileBasicsFields,
  type ProfileDraft,
} from '@/components/Auth/profileFields';
import { useAuth } from '@/context/AuthProvider';
import { isValidCpf, maskCpf, onlyDigits, passwordIssues, passwordStrength } from '@/lib/ptBR';

const STEPS = ['Acesso', 'Perfil', 'Saúde e localização'];
const STRENGTH_COLORS = ['#dbeafe', '#f87171', '#f59e0b', '#60a5fa', '#16a34a'];

interface RegisterWizardProps {
  onFinish: () => void;
  onSwitchToLogin: () => void;
}

export function RegisterWizard({ onFinish, onSwitchToLogin }: RegisterWizardProps) {
  const { register, update, citizen } = useAuth();
  const reduce = useReducedMotion();
  const [step, setStep] = useState(0);
  const [dir, setDir] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Passo 1
  const [nome, setNome] = useState('');
  const [cpf, setCpf] = useState('');
  const [senha, setSenha] = useState('');
  const [confirma, setConfirma] = useState('');
  const [lembrar, setLembrar] = useState(true);
  const [consent, setConsent] = useState(false);
  const [touched, setTouched] = useState(false);

  // Passos 2 e 3
  const [draft, setDraft] = useState<ProfileDraft>({ data_nascimento: '', sexo_biologico: '', ra_residencia: '', telefone: '', condicoes: [] });
  const patchDraft = (d: Partial<ProfileDraft>) => setDraft((prev) => ({ ...prev, ...d }));

  const go = (next: number) => {
    setDir(next > step ? 1 : -1);
    setError(null);
    setStep(next);
  };

  const errors = {
    nome: touched && nome.trim().split(/\s+/).length < 2 ? 'Informe nome e sobrenome.' : null,
    cpf: touched && !isValidCpf(cpf) ? 'CPF inválido. Confira os números.' : null,
    senha: touched ? passwordIssues(senha) : null,
    confirma: touched && confirma !== senha ? 'As senhas não conferem.' : null,
  };
  const strength = passwordStrength(senha);

  const submitAccess = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    const invalid = nome.trim().split(/\s+/).length < 2 || !isValidCpf(cpf) || passwordIssues(senha) || confirma !== senha;
    if (invalid) return;
    if (!consent) {
      setError('Para criar a conta, confirme que leu como seus dados são usados.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await register({ nome_completo: nome.trim(), cpf: onlyDigits(cpf), senha, lembrar });
      go(1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível criar a conta.');
    } finally {
      setBusy(false);
    }
  };

  const saveProfile = async (next: number) => {
    setBusy(true);
    setError(null);
    try {
      await update(draftToPatch(draft));
      go(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível salvar.');
    } finally {
      setBusy(false);
    }
  };

  const variants = {
    enter: (d: number) => ({ opacity: 0, x: reduce ? 0 : 24 * d }),
    center: { opacity: 1, x: 0 },
    exit: (d: number) => ({ opacity: 0, x: reduce ? 0 : -24 * d }),
  };

  return (
    <div>
      {step < 3 && (
        <div className="sx-steps" aria-label={`Passo ${step + 1} de 3: ${STEPS[step]}`}>
          <div className="bar">
            <i style={{ width: `${((step + 1) / 3) * 100}%` }} />
          </div>
          <small>
            {step + 1}/3 · {STEPS[step]}
          </small>
        </div>
      )}

      <AnimatePresence mode="wait" custom={dir} initial={false}>
        <motion.div
          key={step}
          custom={dir}
          variants={variants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ duration: 0.2, ease: [0.2, 0.8, 0.2, 1] }}
        >
          {step === 0 && (
            <form className="sx-form" onSubmit={submitAccess} noValidate>
              <Field
                label="Nome completo"
                icon={<User size={18} aria-hidden />}
                autoComplete="name"
                placeholder="Como está no seu documento"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                error={errors.nome}
                autoFocus
              />
              <Field
                label="CPF"
                icon={<IdCard size={18} aria-hidden />}
                inputMode="numeric"
                autoComplete="username"
                placeholder="000.000.000-00"
                value={cpf}
                onChange={(e) => setCpf(maskCpf(e.target.value))}
                error={errors.cpf}
                hint="Será usado para entrar. Exibimos sempre mascarado."
              />
              <div className="sx-row">
                <div>
                  <PasswordField
                    label="Senha"
                    autoComplete="new-password"
                    placeholder="8+ letras e números"
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    error={errors.senha}
                  />
                  {senha && (
                    <div className="sx-strength" aria-hidden>
                      {[1, 2, 3, 4].map((i) => (
                        <i key={i} style={{ background: i <= strength ? STRENGTH_COLORS[strength] : undefined }} />
                      ))}
                    </div>
                  )}
                </div>
                <PasswordField
                  label="Confirmar senha"
                  autoComplete="new-password"
                  placeholder="Repita a senha"
                  value={confirma}
                  onChange={(e) => setConfirma(e.target.value)}
                  error={errors.confirma}
                />
              </div>
              <Checkbox label="Lembrar de mim neste aparelho" checked={lembrar} onChange={(e) => setLembrar(e.target.checked)} />
              <Checkbox
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                label={
                  <span className="sx-legal">
                    Entendo que meus dados (LGPD) servem só para personalizar orientações e lembretes, podem ser editados ou
                    excluídos a qualquer momento e nunca são enviados ao modelo de IA com CPF ou telefone.
                  </span>
                }
              />
              {error && (
                <div className="sx-alert" role="alert">
                  {error}
                </div>
              )}
              <button className="sx-btn block" type="submit" disabled={busy}>
                {busy ? 'Criando conta…' : 'Criar conta'}
                <span className="arrow">
                  <ArrowRight size={16} aria-hidden />
                </span>
              </button>
              <div className="sx-line" style={{ justifyContent: 'center' }}>
                <span className="sx-legal">Já tem conta?</span>
                <button type="button" className="sx-link" onClick={onSwitchToLogin}>
                  Entrar
                </button>
              </div>
            </form>
          )}

          {step === 1 && (
            <div className="sx-form">
              <p className="sx-lead" style={{ margin: 0 }}>
                Conta criada{citizen ? `, ${citizen.primeiro_nome}` : ''}! Estes dados são opcionais e deixam as respostas mais
                certeiras.
              </p>
              <ProfileBasicsFields draft={draft} onChange={patchDraft} />
              {error && (
                <div className="sx-alert" role="alert">
                  {error}
                </div>
              )}
              <div className="sx-actions">
                <button type="button" className="sx-link" onClick={() => go(2)}>
                  Pular
                </button>
                <button type="button" className="sx-btn" disabled={busy} onClick={() => saveProfile(2)}>
                  {busy ? 'Salvando…' : 'Continuar'}
                  <span className="arrow">
                    <ArrowRight size={16} aria-hidden />
                  </span>
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="sx-form">
              <ConditionsChecklist draft={draft} onChange={patchDraft} />
              <LocationCard />
              {error && (
                <div className="sx-alert" role="alert">
                  {error}
                </div>
              )}
              <div className="sx-actions">
                <button type="button" className="sx-link" onClick={() => go(1)}>
                  Voltar
                </button>
                <button type="button" className="sx-btn" disabled={busy} onClick={() => saveProfile(3)}>
                  {busy ? 'Salvando…' : 'Concluir'}
                  <span className="arrow">
                    <Check size={16} aria-hidden />
                  </span>
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="sx-done" role="status">
              <motion.div
                className="tick"
                initial={reduce ? false : { scale: 0.4, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: 'spring', stiffness: 320, damping: 18 }}
              >
                <Check size={34} aria-hidden />
              </motion.div>
              <h3 className="sx-title" style={{ fontSize: 24 }}>
                Tudo <b>pronto</b>
              </h3>
              <p className="sx-lead" style={{ margin: 0, maxWidth: 320 }}>
                Sua agenda já mostra as vacinas indicadas para o seu perfil. Peça lembretes de consultas e exames direto no chat.
              </p>
              <button type="button" className="sx-btn" onClick={onFinish}>
                Ver minha agenda
                <span className="arrow">
                  <ArrowRight size={16} aria-hidden />
                </span>
              </button>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
