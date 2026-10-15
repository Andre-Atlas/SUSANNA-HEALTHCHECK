// Tipos compartilhados entre cadastro, agenda e chat

export interface CitizenProfile {
  id: string;
  nome_completo: string;
  primeiro_nome: string;
  cpf_mascarado: string;
  cns_mascarado?: string | null;
  data_nascimento?: string | null;
  idade_anos?: number | null;
  faixa_etaria?: string | null;
  sexo_biologico?: 'M' | 'F' | null;
  gestante: boolean;
  condicoes: string[];
  ra_residencia: string;
  ra_display: string;
  bairro_ou_setor?: string | null;
  telefone?: string | null;
  perfil_completo: boolean;
  created_at: string;
}

export interface AuthResponse {
  token: string;
  expires_at: string;
  remember: boolean;
  citizen: CitizenProfile;
}

export interface RegisterPayload {
  nome_completo: string;
  cpf: string;
  senha: string;
  lembrar: boolean;
}

export type ProfilePatch = Partial<{
  nome_completo: string;
  data_nascimento: string | null;
  sexo_biologico: 'M' | 'F' | null;
  ra_residencia: string | null;
  telefone: string | null;
  condicoes: string[];
}>;

export type AgendaEventType = 'consulta' | 'exame' | 'vacina' | 'medicamento' | 'outro';

export interface AgendaEvent {
  id: string;
  tipo: AgendaEventType;
  titulo: string;
  data_evento: string;
  horario?: string | null;
  unidade_saude?: string | null;
  notas?: string | null;
  lembrete_min_antes: number;
  recorrencia?: 'diaria' | 'semanal' | null;
  status: 'agendado' | 'concluido' | 'cancelado';
  origem: 'manual' | 'chat';
  created_at: string;
  updated_at: string;
}

export interface PendingVaccine {
  vaccine_id: string;
  dose_num: number;
  nome: string;
  dose_label: string;
  status: 'atrasada' | 'agora' | 'proxima';
  data_sugerida: string;
  motivo: string;
}

export interface AgendaOverview {
  eventos: AgendaEvent[];
  vacinas_pendentes: PendingVaccine[];
  perfil_incompleto: boolean;
  pendencias: number;
}

export interface AgendaProposal {
  proposal_id: string;
  tipo: AgendaEventType;
  titulo: string;
  data_evento?: string | null;
  horario?: string | null;
  unidade_saude?: string | null;
  recorrencia?: 'diaria' | 'semanal' | null;
  faltando: string[];
  texto_confirmacao: string;
}

export interface RADistribution {
  ra: string;
  ra_display: string;
  unit_count: number;
}
