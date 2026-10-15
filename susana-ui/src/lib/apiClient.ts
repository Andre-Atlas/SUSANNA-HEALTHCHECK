import { buildApiUrl } from '@/lib/api';
import { clearToken, getToken } from '@/lib/auth';

export const AUTH_EXPIRED_EVENT = 'susana:auth-expired';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/** Converte o `detail` do FastAPI (texto ou lista de erros de validação) em mensagem legível. */
function detailToMessage(detail: unknown, status: number): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string };
    return (first.msg || 'Dados inválidos.').replace(/^Value error, /, '');
  }
  if (status === 429) return 'Muitas tentativas. Aguarde alguns minutos.';
  if (status >= 500) return 'O serviço está indisponível no momento. Tente novamente.';
  return 'Não foi possível concluir a operação.';
}

/** Cabeçalhos com o token de sessão, quando houver. */
export function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getToken();
  return token ? { ...extra, Authorization: `Bearer ${token}` } : extra;
}

export async function apiFetch<T>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  const { json, headers, ...rest } = init;
  const res = await fetch(buildApiUrl(path), {
    ...rest,
    headers: authHeaders({
      ...(json !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...((headers as Record<string, string>) || {}),
    }),
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  const text = await res.text();
  const data = text ? (() => { try { return JSON.parse(text); } catch { return text; } })() : null;
  if (!res.ok) {
    if (res.status === 401 && getToken()) {
      clearToken();
      window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
    }
    throw new ApiError(res.status, detailToMessage(data?.detail, res.status));
  }
  return data as T;
}
