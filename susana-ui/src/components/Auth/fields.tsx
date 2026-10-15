'use client';

import React, { useId, useState } from 'react';
import { Eye, EyeOff, Lock } from 'lucide-react';

interface FieldProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label: string;
  icon?: React.ReactNode;
  hint?: string | null;
  error?: string | null;
  trailing?: React.ReactNode;
}

/** Campo em pílula com ícone, rótulo acessível e mensagem de ajuda/erro. */
export function Field({ label, icon, hint, error, trailing, id, ...input }: FieldProps) {
  const autoId = useId();
  const fieldId = id || autoId;
  const msgId = `${fieldId}-msg`;
  return (
    <div>
      <label className="sx-label" htmlFor={fieldId}>
        {label}
      </label>
      <div className="sx-field" data-invalid={error ? 'true' : undefined}>
        {icon}
        <input id={fieldId} aria-invalid={!!error} aria-describedby={error || hint ? msgId : undefined} {...input} />
        {trailing}
      </div>
      {(error || hint) && (
        <p id={msgId} className={`sx-hint${error ? ' bad' : ''}`} role={error ? 'alert' : undefined}>
          {error || hint}
        </p>
      )}
    </div>
  );
}

export function PasswordField(props: Omit<FieldProps, 'type' | 'trailing' | 'icon'>) {
  const [show, setShow] = useState(false);
  return (
    <Field
      {...props}
      type={show ? 'text' : 'password'}
      icon={<Lock size={18} aria-hidden />}
      trailing={
        <button
          type="button"
          className="sx-eye"
          onClick={() => setShow((s) => !s)}
          aria-label={show ? 'Ocultar senha' : 'Mostrar senha'}
          aria-pressed={show}
        >
          {show ? <EyeOff size={18} aria-hidden /> : <Eye size={18} aria-hidden />}
        </button>
      }
    />
  );
}

export function SelectField({
  label,
  icon,
  hint,
  children,
  ...select
}: React.SelectHTMLAttributes<HTMLSelectElement> & { label: string; icon?: React.ReactNode; hint?: string }) {
  const id = useId();
  return (
    <div>
      <label className="sx-label" htmlFor={id}>
        {label}
      </label>
      <div className="sx-field">
        {icon}
        <select id={id} {...select}>
          {children}
        </select>
      </div>
      {hint && <p className="sx-hint">{hint}</p>}
    </div>
  );
}

export function Checkbox({ label, ...input }: React.InputHTMLAttributes<HTMLInputElement> & { label: React.ReactNode }) {
  return (
    <label className="sx-check">
      <input type="checkbox" {...input} />
      <span>{label}</span>
    </label>
  );
}
