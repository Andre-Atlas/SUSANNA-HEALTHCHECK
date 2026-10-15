'use client';

import React, { useEffect, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { KeyRound, LogOut, Trash, User, X } from 'lucide-react';
import { Field, PasswordField } from '@/components/Auth/fields';
import { ConditionsChecklist, draftToPatch, LocationCard, ProfileBasicsFields, type ProfileDraft } from '@/components/Auth/profileFields';
import { useAuth } from '@/context/AuthProvider';
import { maskPhone, passwordIssues } from '@/lib/ptBR';
import type { CitizenProfile } from '@/lib/types';

function toDraft(c: CitizenProfile): ProfileDraft {
  return {
    data_nascimento: c.data_nascimento || '',
    sexo_biologico: c.sexo_biologico || '',
    ra_residencia: c.ra_residencia && c.ra_residencia !== 'geral_df' ? c.ra_residencia : '',
    telefone: c.telefone ? maskPhone(c.telefone) : '',
    condicoes: c.condicoes || [],
  };
}

export function ProfileSheet() {
  const { citizen, profileOpen } = useAuth();
  return <AnimatePresence>{profileOpen && citizen && <ProfilePanel key="profile" citizen={citizen} />}</AnimatePresence>;
}

/** Montado a cada abertura com os dados atuais do perfil. */
function ProfilePanel({ citizen }: { citizen: CitizenProfile }) {
  const { setProfileOpen, update, logout, changePassword, deleteAccount } = useAuth();
  const reduce = useReducedMotion();
  const [nome, setNome] = useState(citizen.nome_completo);
  const [draft, setDraft] = useState<ProfileDraft>(() => toDraft(citizen));
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [pwOpen, setPwOpen] = useState(false);
  const [pwAtual, setPwAtual] = useState('');
  const [pwNova, setPwNova] = useState('');
  const [delOpen, setDelOpen] = useState(false);
  const [delSenha, setDelSenha] = useState('');

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setProfileOpen(false);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [setProfileOpen]);

  const run = async (fn: () => Promise<unknown>, okText: string) => {
    setBusy(true);
    setMsg(null);
    try {
      await fn();
      setMsg({ ok: true, text: okText });
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : 'Não foi possível concluir.' });
    } finally {
      setBusy(false);
    }
  };

  const close = () => setProfileOpen(false);

  return (
    <motion.div
      className="sx sx-sheet-wrap"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onMouseDown={(e) => e.target === e.currentTarget && close()}
    >
      <motion.aside
        className="sx-sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-title"
        initial={reduce ? { opacity: 0 } : { x: 40, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={reduce ? { opacity: 0 } : { x: 40, opacity: 0 }}
        transition={{ duration: 0.26, ease: [0.2, 0.8, 0.2, 1] }}
      >
        <button type="button" className="sx-close" onClick={close} aria-label="Fechar">
          <X size={18} aria-hidden />
        </button>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <div className="sx-avatar" aria-hidden>
            {citizen.primeiro_nome.charAt(0)}
          </div>
          <div style={{ minWidth: 0 }}>
            <h2 id="profile-title" className="sx-title" style={{ fontSize: 22 }}>
              Meu <b>perfil</b>
            </h2>
            <p className="sx-legal" style={{ margin: 0 }}>
              CPF {citizen.cpf_mascarado} · {citizen.ra_display}
            </p>
          </div>
        </div>

        <h4>Dados pessoais</h4>
        <div className="sx-form">
          <Field label="Nome completo" icon={<User size={18} aria-hidden />} value={nome} onChange={(e) => setNome(e.target.value)} />
          <ProfileBasicsFields draft={draft} onChange={(d) => setDraft((p) => ({ ...p, ...d }))} />
        </div>

        <h4>Saúde e localização</h4>
        <div className="sx-form">
          <ConditionsChecklist draft={draft} onChange={(d) => setDraft((p) => ({ ...p, ...d }))} />
          <LocationCard />
        </div>

        {msg && (
          <div className={`sx-alert${msg.ok ? ' ok' : ''}`} role="status" style={{ marginTop: 14 }}>
            {msg.text}
          </div>
        )}
        <button
          type="button"
          className="sx-btn block"
          style={{ marginTop: 14 }}
          disabled={busy}
          onClick={() => run(() => update({ ...draftToPatch(draft), nome_completo: nome.trim() }), 'Perfil atualizado.')}
        >
          {busy ? 'Salvando…' : 'Salvar alterações'}
        </button>

        <h4>Segurança</h4>
        <div className="sx-form">
          <button type="button" className="sx-btn ghost block" onClick={() => setPwOpen((o) => !o)} aria-expanded={pwOpen}>
            <KeyRound size={16} aria-hidden /> Alterar senha
          </button>
          {pwOpen && (
            <>
              <PasswordField
                label="Senha atual"
                autoComplete="current-password"
                value={pwAtual}
                onChange={(e) => setPwAtual(e.target.value)}
              />
              <PasswordField
                label="Nova senha"
                autoComplete="new-password"
                value={pwNova}
                onChange={(e) => setPwNova(e.target.value)}
                error={pwNova ? passwordIssues(pwNova) : null}
              />
              <button
                type="button"
                className="sx-btn sm"
                disabled={busy || !pwAtual || !!passwordIssues(pwNova)}
                onClick={() =>
                  run(async () => {
                    await changePassword(pwAtual, pwNova);
                    setPwAtual('');
                    setPwNova('');
                    setPwOpen(false);
                  }, 'Senha alterada. Outros aparelhos foram desconectados.')
                }
              >
                Salvar nova senha
              </button>
            </>
          )}
          <div className="sx-segbtns">
            <button type="button" className="sx-btn ghost sm" onClick={() => logout().then(close)}>
              <LogOut size={15} aria-hidden /> Sair
            </button>
            <button type="button" className="sx-btn ghost sm" onClick={() => logout(true).then(close)}>
              Sair de todos
            </button>
          </div>
        </div>

        <h4>Privacidade</h4>
        <p className="sx-legal">
          Seus dados ficam guardados apenas para personalizar orientações. A localização nunca sai deste aparelho, e o modelo de IA não
          recebe CPF, telefone nem nome completo.
        </p>
        {!delOpen ? (
          <button type="button" className="sx-link" style={{ color: '#dc2626' }} onClick={() => setDelOpen(true)}>
            Excluir minha conta
          </button>
        ) : (
          <div className="sx-card sx-form">
            <p className="sx-legal" style={{ margin: 0 }}>
              Isso apaga perfil, agenda, registros de vacina e conversas salvas. Não pode ser desfeito.
            </p>
            <PasswordField
              label="Confirme sua senha"
              autoComplete="current-password"
              value={delSenha}
              onChange={(e) => setDelSenha(e.target.value)}
            />
            <div className="sx-segbtns">
              <button type="button" className="sx-btn ghost sm" onClick={() => setDelOpen(false)}>
                Cancelar
              </button>
              <button
                type="button"
                className="sx-btn danger sm"
                disabled={busy || !delSenha}
                onClick={() =>
                  run(async () => {
                    await deleteAccount(delSenha);
                    close();
                  }, 'Conta excluída.')
                }
              >
                <Trash size={15} aria-hidden /> Excluir
              </button>
            </div>
          </div>
        )}
      </motion.aside>
    </motion.div>
  );
}
