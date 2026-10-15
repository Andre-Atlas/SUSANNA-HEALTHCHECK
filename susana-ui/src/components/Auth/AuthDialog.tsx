'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { BellRing, ShieldCheck, Sparkles, Syringe, X } from 'lucide-react';
import { LoginForm } from '@/components/Auth/LoginForm';
import { RegisterWizard } from '@/components/Auth/RegisterWizard';
import { useAuth, type AuthMode } from '@/context/AuthProvider';

interface AuthDialogProps {
  /** Chamado ao concluir o cadastro (ex.: abrir a aba Agenda). */
  onOpenAgenda: () => void;
  onWelcome?: (firstName: string) => void;
}

const FOCUSABLE = 'button:not([disabled]), input:not([disabled]), select:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])';

export function AuthDialog(props: AuthDialogProps) {
  const { authDialog } = useAuth();
  return <AnimatePresence>{authDialog && <AuthPanel key="auth" initialMode={authDialog} {...props} />}</AnimatePresence>;
}

/** Conteúdo do diálogo: montado a cada abertura, já no modo pedido. */
function AuthPanel({ initialMode, onOpenAgenda, onWelcome }: AuthDialogProps & { initialMode: AuthMode }) {
  const { closeAuth, status } = useAuth();
  const reduce = useReducedMotion();
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const panelRef = useRef<HTMLDivElement>(null);
  // Depois do passo 1 a conta já existe: some a alternância Entrar/Criar conta
  const wizardStarted = mode === 'register' && status === 'authed';

  // Trava a rolagem da página e devolve o foco ao fechar
  useEffect(() => {
    const lastFocus = document.activeElement as HTMLElement | null;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prevOverflow;
      lastFocus?.focus?.();
    };
  }, []);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.stopPropagation();
      closeAuth();
      return;
    }
    if (e.key !== 'Tab' || !panelRef.current) return;
    const nodes = Array.from(panelRef.current.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((n) => n.offsetParent !== null);
    if (!nodes.length) return;
    const first = nodes[0];
    const last = nodes[nodes.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  };

  const switchTo = (m: AuthMode) => setMode(m);

  return (
    <motion.div
      className="sx sx-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      onMouseDown={(e) => e.target === e.currentTarget && closeAuth()}
      onKeyDown={onKeyDown}
    >
      <motion.div
        ref={panelRef}
        className="sx-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
        initial={reduce ? { opacity: 0 } : { opacity: 0, y: 18, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={reduce ? { opacity: 0 } : { opacity: 0, y: 12, scale: 0.98 }}
        transition={{ duration: 0.28, ease: [0.2, 0.8, 0.2, 1] }}
      >
        <div className="sx-hero" aria-hidden>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <img className="mascot" src="/images/suzanna-avatar.webp" alt="" />
            <h2>
              Sua saúde, <b>do seu jeito</b>.
            </h2>
            <p>A conta é opcional. Sem ela, você continua usando a SUSANNA normalmente.</p>
          </div>
          <ul>
            <li>
              <span>
                <Syringe size={16} />
              </span>
              Vacinas pendentes calculadas para você
            </li>
            <li>
              <span>
                <BellRing size={16} />
              </span>
              Lembretes de consultas e exames pelo chat
            </li>
            <li>
              <span>
                <Sparkles size={16} />
              </span>
              Respostas que consideram seu perfil
            </li>
            <li>
              <span>
                <ShieldCheck size={16} />
              </span>
              Dados protegidos e sob seu controle
            </li>
          </ul>
        </div>

        <div className="sx-body">
          <button type="button" className="sx-close" onClick={closeAuth} aria-label="Fechar">
            <X size={18} aria-hidden />
          </button>
          <h2 id="auth-title" className="sx-title">
            {mode === 'login' ? (
              <>
                Bem-vindo <b>de volta</b>
              </>
            ) : (
              <>
                Criar <b>conta</b>
              </>
            )}
          </h2>
          <p className="sx-lead">
            {mode === 'login'
              ? 'Entre com seu CPF e senha.'
              : wizardStarted
                ? 'Complete se quiser — cada passo pode ser pulado.'
                : 'Leva menos de um minuto. Só o primeiro passo é obrigatório.'}
          </p>

          {!wizardStarted && (
            <div className="sx-seg" role="tablist" aria-label="Entrar ou criar conta">
              {(
                [
                  ['login', 'Entrar'],
                  ['register', 'Criar conta'],
                ] as const
              ).map(([m, label]) => (
                <button key={m} type="button" role="tab" aria-selected={mode === m} onClick={() => switchTo(m)}>
                  {mode === m && (
                    <motion.span
                      layoutId="auth-seg"
                      className="ind"
                      transition={reduce ? { duration: 0 } : { type: 'spring', stiffness: 420, damping: 34 }}
                    />
                  )}
                  {label}
                </button>
              ))}
            </div>
          )}

          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: reduce ? 0 : 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: reduce ? 0 : -6 }}
              transition={{ duration: 0.16 }}
            >
              {mode === 'login' ? (
                <LoginForm
                  onDone={(name) => {
                    onWelcome?.(name);
                    closeAuth();
                  }}
                  onSwitchToRegister={() => switchTo('register')}
                  onSkip={closeAuth}
                />
              ) : (
                <RegisterWizard
                  onSwitchToLogin={() => switchTo('login')}
                  onFinish={() => {
                    closeAuth();
                    onOpenAgenda();
                  }}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}
