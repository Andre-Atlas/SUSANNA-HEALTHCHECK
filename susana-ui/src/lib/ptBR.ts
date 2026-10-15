// Máscaras, validações e rótulos em português usados no cadastro e na agenda

export const onlyDigits = (v: string) => v.replace(/\D/g, '');

export function maskCpf(v: string): string {
  const d = onlyDigits(v).slice(0, 11);
  return d
    .replace(/^(\d{3})(\d)/, '$1.$2')
    .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d{1,2})$/, '.$1-$2');
}

/** Mesmo algoritmo (módulo 11) do backend, para avisar o erro na hora. */
export function isValidCpf(v: string): boolean {
  const d = onlyDigits(v);
  if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false;
  const digit = (len: number) => {
    let sum = 0;
    for (let i = 0; i < len; i++) sum += Number(d[i]) * (len + 1 - i);
    const r = 11 - (sum % 11);
    return r >= 10 ? 0 : r;
  };
  return digit(9) === Number(d[9]) && digit(10) === Number(d[10]);
}

export function maskPhone(v: string): string {
  const d = onlyDigits(v).slice(0, 11);
  if (d.length <= 2) return d.length ? `(${d}` : '';
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

export function passwordIssues(p: string): string | null {
  if (p.length < 8) return 'Use pelo menos 8 caracteres.';
  if (!/[A-Za-zÀ-ÿ]/.test(p) || !/\d/.test(p)) return 'Combine letras e números.';
  return null;
}

/** 0 a 4 — usado no medidor de força da senha. */
export function passwordStrength(p: string): number {
  let s = 0;
  if (p.length >= 8) s++;
  if (p.length >= 12) s++;
  if (/[A-Za-zÀ-ÿ]/.test(p) && /\d/.test(p)) s++;
  if (/[^A-Za-z0-9]/.test(p) || (/[a-z]/.test(p) && /[A-Z]/.test(p))) s++;
  return s;
}

export function ageFromBirth(iso?: string | null): number | null {
  if (!iso) return null;
  const b = new Date(iso + 'T00:00:00');
  if (Number.isNaN(b.getTime())) return null;
  const now = new Date();
  let age = now.getFullYear() - b.getFullYear();
  if (now.getMonth() < b.getMonth() || (now.getMonth() === b.getMonth() && now.getDate() < b.getDate())) age--;
  return age >= 0 && age <= 120 ? age : null;
}

export const CONDITIONS: { id: string; label: string; onlyF?: boolean }[] = [
  { id: 'gestante', label: 'Gestante', onlyF: true },
  { id: 'diabetes', label: 'Diabetes' },
  { id: 'hipertensao', label: 'Hipertensão' },
  { id: 'asma', label: 'Asma' },
  { id: 'dpoc', label: 'DPOC / pulmão' },
  { id: 'cardiopatia', label: 'Doença cardíaca' },
  { id: 'doenca_renal_cronica', label: 'Doença renal' },
  { id: 'imunossupressao', label: 'Imunossupressão' },
  { id: 'hiv', label: 'HIV' },
  { id: 'cancer', label: 'Câncer' },
  { id: 'obesidade', label: 'Obesidade' },
  { id: 'deficiencia', label: 'Deficiência' },
  { id: 'tabagismo', label: 'Tabagismo' },
];

export const EVENT_TYPE_LABEL: Record<string, string> = {
  consulta: 'Consulta',
  exame: 'Exame',
  vacina: 'Vacina',
  medicamento: 'Medicamento',
  outro: 'Lembrete',
};

const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
const WEEKDAYS = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'];

export const monthName = (m: number) => MONTHS[m];

export function toISODate(d: Date): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

export function parseISODate(iso: string): Date {
  return new Date(iso.slice(0, 10) + 'T00:00:00');
}

/** "ter, 20 out" */
export function shortDate(iso: string): string {
  const d = parseISODate(iso);
  return `${WEEKDAYS[d.getDay()].slice(0, 3)}, ${d.getDate()} ${MONTHS[d.getMonth()].slice(0, 3)}`;
}

/** "terça, 20 de outubro" */
export function longDate(iso: string): string {
  const d = parseISODate(iso);
  return `${WEEKDAYS[d.getDay()]}, ${d.getDate()} de ${MONTHS[d.getMonth()]}`;
}
