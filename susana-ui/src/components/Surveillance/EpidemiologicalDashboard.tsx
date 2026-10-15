'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  ChevronRight,
  Info,
  MapPin,
  MessageSquare,
  Minus,
  RefreshCw,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { buildApiUrl } from '@/lib/api';

// =========================================================================
// Tipos Estruturados de Vigilância Epidemiológica (SUS-DF)
// =========================================================================
export interface SurveillanceCategory {
  id: string;
  nome: string;
  slug: string;
  icone: string;
  descricao: string;
  cor_badge: string;
  total_agravos: number;
}

export interface SurveillanceCondition {
  id: string;
  category_id: string;
  nome: string;
  codigo_cid10: string;
  tipo_agravo: string;
  descricao: string;
  nivel_alerta: 'baixo' | 'atencao' | 'alerta' | 'critico';
  sazonalidade: string;
  vetor_ou_transmissao: string;
  taxa_incidencia_100k: number;
  total_casos_ano: number;
  variacao_semanal_pct: number;
  faixa_etaria_predominante: string;
}

export interface TimeSeriesPoint {
  semana_epidemio: string;
  numero_semana: number;
  rotulo: string;
  casos: number;
  taxa_movel: number;
  status: string;
}

export interface RegionCaseDistribution {
  ra_id: string;
  ra_nome: string;
  casos: number;
  taxa_incidencia_100k: number;
  percentual_distrital: number;
  nivel_risco: string;
}

export interface GuidelineItem {
  tipo: 'sinal_alarme' | 'prevencao' | 'conduta';
  titulo: string;
  descricao: string;
  severidade?: string;
}

export interface UnidadeReferenciaItem {
  tipo_servico: string;
  nome_exemplo: string;
  papel_clinico: string;
  endereco_resumo: string;
}

export interface DashboardKPIs {
  total_casos_ano: number;
  casos_ultima_semana: number;
  variacao_semanal_pct: number;
  tendencia: 'alta' | 'queda' | 'estavel';
  taxa_incidencia_distrital_100k: number;
  obitos_confirmados: number;
  ra_hotspot_id: string;
  ra_hotspot_nome: string;
  ra_hotspot_casos: number;
  nivel_alerta_geral: string;
}

export interface ConditionDashboardResponse {
  condition: SurveillanceCondition;
  kpis: DashboardKPIs;
  time_series: TimeSeriesPoint[];
  regions: RegionCaseDistribution[];
  guidelines: GuidelineItem[];
  unidades_referencia: UnidadeReferenciaItem[];
  fonte_oficial: string;
  ano_vigente: number;
  data_atualizacao: string;
}

interface EpidemiologicalDashboardProps {
  onAskSuzanna?: (prompt: string) => void;
}

export function EpidemiologicalDashboard({ onAskSuzanna }: EpidemiologicalDashboardProps) {
  // Estados principais
  const [categories, setCategories] = useState<SurveillanceCategory[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('cat_arboviroses');
  const [conditions, setConditions] = useState<SurveillanceCondition[]>([]);
  const [selectedConditionId, setSelectedConditionId] = useState<string>('dengue');
  const [dashboardData, setDashboardData] = useState<ConditionDashboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Interatividade do gráfico SVG (Hover / Tooltip)
  const [hoveredPointIndex, setHoveredPointIndex] = useState<number | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  // 1. Carrega categorias na montagem
  useEffect(() => {
    async function loadCategories() {
      try {
        const res = await fetch(buildApiUrl('/api/surveillance/categories'));
        if (!res.ok) throw new Error('Falha ao obter categorias epidemiológicas.');
        const data: SurveillanceCategory[] = await res.json();
        setCategories(data);
        if (data.length > 0 && !data.some((c) => c.id === activeCategory)) {
          setActiveCategory(data[0].id);
        }
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar vigilância epidemiológica.');
      }
    }
    loadCategories();
  }, []);

  // 2. Carrega condições da categoria ativa
  useEffect(() => {
    async function loadConditions() {
      if (!activeCategory) return;
      try {
        const res = await fetch(buildApiUrl(`/api/surveillance/conditions?category_id=${activeCategory}`));
        if (!res.ok) throw new Error('Falha ao listar agravos da categoria.');
        const data: SurveillanceCondition[] = await res.json();
        setConditions(data);
        if (data.length > 0) {
          // Se o agravo atualmente selecionado não pertence a esta categoria, seleciona o primeiro
          if (!data.some((c) => c.id === selectedConditionId)) {
            setSelectedConditionId(data[0].id);
          }
        }
      } catch (err: any) {
        setError(err.message || 'Erro ao buscar condições epidemiológicas.');
      }
    }
    loadConditions();
  }, [activeCategory]);

  // 3. Carrega dados consolidados do agravo selecionado
  useEffect(() => {
    async function loadDashboard() {
      if (!selectedConditionId) return;
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(buildApiUrl(`/api/surveillance/dashboard/${selectedConditionId}`));
        if (!res.ok) throw new Error('Falha ao obter dados detalhados do agravo.');
        const data: ConditionDashboardResponse = await res.json();
        setDashboardData(data);
      } catch (err: any) {
        setError(err.message || 'Erro ao carregar dados do dashboard.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [selectedConditionId]);

  // Manipulador de hover no SVG
  const handleSvgMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!svgRef.current || !dashboardData?.time_series?.length) return;
    const rect = svgRef.current.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const width = rect.width;
    const totalPoints = dashboardData.time_series.length;

    // Converte posição X relativa em índice de ponto
    const step = width / (totalPoints - 1);
    const index = Math.round(clientX / step);
    const clamped = Math.max(0, Math.min(totalPoints - 1, index));
    setHoveredPointIndex(clamped);
  };

  const handleSvgMouseLeave = () => {
    setHoveredPointIndex(null);
  };

  // Manipulador de toque em dispositivos móveis
  const handleTouch = (clientX: number) => {
    if (!svgRef.current || !dashboardData?.time_series?.length) return;
    const rect = svgRef.current.getBoundingClientRect();
    const relativeX = clientX - rect.left;
    const width = rect.width;
    const totalPoints = dashboardData.time_series.length;
    const divisor = totalPoints > 1 ? totalPoints - 1 : 1;
    const step = width / divisor;
    const index = Math.round(relativeX / step);
    const clamped = Math.max(0, Math.min(totalPoints - 1, index));
    setHoveredPointIndex(clamped);
  };

  // Cores semafóricas para nível de alerta (Conforme WCAG 2.1 AA)
  const getAlertBadge = (nivel: string) => {
    switch (nivel) {
      case 'critico':
        return { bg: 'rgba(239, 68, 68, 0.15)', text: '#dc2626', border: 'rgba(239, 68, 68, 0.3)', label: 'Crítico / Epidêmico' };
      case 'alerta':
        return { bg: 'rgba(249, 115, 22, 0.15)', text: '#ea580c', border: 'rgba(249, 115, 22, 0.3)', label: 'Alerta SES-DF' };
      case 'atencao':
        return { bg: 'rgba(234, 179, 8, 0.15)', text: '#a16207', border: 'rgba(234, 179, 8, 0.3)', label: 'Atenção Epidemiológica' };
      default:
        return { bg: 'rgba(34, 197, 94, 0.15)', text: '#16a34a', border: 'rgba(34, 197, 94, 0.3)', label: 'Transmissão Controlada' };
    }
  };

  // Memoização da geometria da curva SVG para máxima fluidez a 60-120 FPS
  const chartGeometry = useMemo(() => {
    if (!dashboardData?.time_series?.length) return null;
    const series = dashboardData.time_series;
    const width = 640;
    const height = 180;
    const paddingBottom = 30;
    const chartHeight = height - paddingBottom;
    const maxVal = Math.max(...series.map((s) => s.casos), 10);
    const ceiling = Math.ceil(maxVal * 1.15);

    const divisor = series.length > 1 ? series.length - 1 : 1;
    const points: [number, number][] = series.map((pt, i) => {
      const x = series.length === 1 ? width / 2 : (i / divisor) * width;
      const y = chartHeight - (pt.casos / ceiling) * (chartHeight - 20) - 10;
      return [x, y];
    });

    let pathD = `M ${points[0][0]},${points[0][1]}`;
    if (points.length > 1) {
      for (let i = 1; i < points.length; i++) {
        const prev = points[i - 1];
        const curr = points[i];
        const midX = (prev[0] + curr[0]) / 2;
        pathD += ` C ${midX},${prev[1]} ${midX},${curr[1]} ${curr[0]},${curr[1]}`;
      }
    } else {
      pathD += ` L ${points[0][0] + 1},${points[0][1]}`;
    }

    const areaD = `${pathD} L ${width},${chartHeight} L 0,${chartHeight} Z`;

    return {
      series,
      width,
      height,
      chartHeight,
      points,
      pathD,
      areaD,
      divisor,
    };
  }, [dashboardData?.time_series]);

  // Renderização da curva Bézier suave com gradiente
  const renderInteractiveChart = () => {
    if (!dashboardData || !chartGeometry) {
      return (
        <div style={{ padding: '40px', textAlign: 'center', color: 'var(--mut)' }}>
          Nenhum dado temporal disponível para este agravo.
        </div>
      );
    }

    const { series, width, height, chartHeight, points, pathD, areaD, divisor } = chartGeometry;
    const activePoint = hoveredPointIndex !== null ? points[hoveredPointIndex] : null;
    const activeData = hoveredPointIndex !== null ? series[hoveredPointIndex] : null;

    return (
      <div style={{ position: 'relative', width: '100%', userSelect: 'none' }}>
        <svg
          ref={svgRef}
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={`Gráfico de evolução temporal de casos de ${dashboardData.condition.nome} no DF`}
          style={{ width: '100%', height: 'auto', overflow: 'visible', cursor: 'crosshair', touchAction: 'none' }}
          onMouseMove={handleSvgMouseMove}
          onMouseLeave={handleSvgMouseLeave}
          onTouchStart={(e) => {
            if (e.touches.length > 0) handleTouch(e.touches[0].clientX);
          }}
          onTouchMove={(e) => {
            if (e.touches.length > 0) handleTouch(e.touches[0].clientX);
          }}
          onTouchEnd={handleSvgMouseLeave}
        >
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.45" />
              <stop offset="70%" stopColor="#60a5fa" stopOpacity="0.12" />
              <stop offset="100%" stopColor="#93c5fd" stopOpacity="0.0" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Linhas de grade sutis */}
          <line x1="0" y1={chartHeight / 2} x2={width} y2={chartHeight / 2} stroke="rgba(203, 213, 225, 0.4)" strokeDasharray="3 3" />
          <line x1="0" y1={chartHeight} x2={width} y2={chartHeight} stroke="rgba(203, 213, 225, 0.7)" />

          {/* Área sombreada em gradiente líquido */}
          <path d={areaD} fill="url(#chartGradient)" />

          {/* Linha principal Bézier */}
          <path d={pathD} fill="none" stroke="#2563eb" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />

          {/* Pontos nas semanas */}
          {points.map(([px, py], idx) => {
            const isHovered = hoveredPointIndex === idx;
            return (
              <circle
                key={idx}
                cx={px}
                cy={py}
                r={isHovered ? 6 : 3.5}
                fill={isHovered ? '#2563eb' : '#ffffff'}
                stroke="#2563eb"
                strokeWidth={isHovered ? 3 : 2}
                style={{ transition: 'all 0.15s ease' }}
              />
            );
          })}

          {/* Linha guia vertical (crosshair) e destaque quando em hover */}
          {activePoint && (
            <>
              <line
                x1={activePoint[0]}
                y1={0}
                x2={activePoint[0]}
                y2={chartHeight}
                stroke="#60a5fa"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
              <circle
                cx={activePoint[0]}
                cy={activePoint[1]}
                r="7"
                fill="#2563eb"
                stroke="#ffffff"
                strokeWidth="2.5"
                filter="url(#glow)"
              />
            </>
          )}

          {/* Rótulos das Semanas Epidemiológicas no rodapé */}
          {series.map((pt, idx) => {
            const x = series.length === 1 ? width / 2 : (idx / divisor) * width;
            const isHovered = hoveredPointIndex === idx;
            return (
              <text
                key={idx}
                x={x}
                y={height - 8}
                textAnchor="middle"
                fontSize="11"
                fontWeight={isHovered ? 700 : 400}
                fill={isHovered ? '#1e40af' : '#64748b'}
              >
                {pt.semana_epidemio}
              </text>
            );
          })}
        </svg>

        {/* Tooltip de Vidro Flutuante (Liquid Glass) */}
        {activePoint && activeData && (
          <div
            style={{
              position: 'absolute',
              left: `${Math.min(Math.max((activePoint[0] / width) * 100, 18), 82)}%`,
              top: `${Math.max((activePoint[1] / height) * 100 - 32, 5)}%`,
              transform: 'translate(-50%, -100%)',
              background: 'rgba(255, 255, 255, 0.92)',
              backdropFilter: 'blur(20px) saturate(180%)',
              border: '1px solid rgba(255, 255, 255, 0.9)',
              borderRadius: '12px',
              padding: '8px 12px',
              boxShadow: '0 10px 25px rgba(30, 64, 175, 0.15)',
              pointerEvents: 'none',
              zIndex: 30,
              minWidth: '140px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 500 }}>
              {activeData.semana_epidemio} ({activeData.rotulo})
            </div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#1e3a8a', margin: '2px 0' }}>
              {activeData.casos.toLocaleString('pt-BR')} <span style={{ fontSize: '11px', fontWeight: 500 }}>casos</span>
            </div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#2563eb', fontWeight: 600 }}>
              <span>Média móvel: {activeData.taxa_movel}</span>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* -------------------------------------------------------------------
          CABECALHO DA ABA & SELETOR DE MACROCATEGORIAS (CHIPS)
      ------------------------------------------------------------------- */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div>
          <h1 style={{ fontSize: '32px', margin: 0, fontWeight: 300, color: 'var(--ink)' }}>
            Monitoramento <b>epidemiológico</b>
          </h1>
          <p className="sub" style={{ margin: '4px 0 0', color: 'var(--mut)', fontSize: '14px' }}>
            Painel oficial da Subsecretaria de Vigilância à Saúde (SVS/SES-DF) integrado aos dados do SINAN.
          </p>
        </div>

        {/* Chips de Categorias */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {categories.map((cat) => {
            const isActive = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                aria-pressed={isActive}
                style={{
                  padding: '9px 16px',
                  borderRadius: '99px',
                  border: isActive ? '1.5px solid var(--b2)' : '1px solid rgba(255, 255, 255, 0.8)',
                  background: isActive ? 'linear-gradient(135deg, #2563eb, #1e40af)' : 'rgba(255, 255, 255, 0.65)',
                  backdropFilter: 'blur(16px)',
                  color: isActive ? '#ffffff' : 'var(--ink)',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  boxShadow: isActive ? '0 4px 14px rgba(37, 99, 235, 0.25)' : '0 2px 6px rgba(0, 0, 0, 0.03)',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <span>{cat.nome}</span>
                <span
                  style={{
                    background: isActive ? 'rgba(255, 255, 255, 0.25)' : 'rgba(37, 99, 235, 0.1)',
                    color: isActive ? '#ffffff' : '#2563eb',
                    fontSize: '11px',
                    padding: '2px 7px',
                    borderRadius: '99px',
                    fontWeight: 700,
                  }}
                >
                  {cat.total_agravos}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* -------------------------------------------------------------------
          SELETOR SECUNDÁRIO: PILLS DOS AGRAVOS ESPECÍFICOS
      ------------------------------------------------------------------- */}
      <div
        className="glass"
        style={{
          padding: '12px 18px',
          borderRadius: '20px',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          gap: '10px',
          background: 'rgba(255, 255, 255, 0.75)',
        }}
      >
        <span style={{ fontSize: '12px', fontWeight: 600, color: '#1e3a8a', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Agravos monitorados:
        </span>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {conditions.map((cond) => {
            const isSelected = selectedConditionId === cond.id;
            const badge = getAlertBadge(cond.nivel_alerta);
            return (
              <button
                key={cond.id}
                onClick={() => setSelectedConditionId(cond.id)}
                aria-pressed={isSelected}
                style={{
                  padding: '7px 14px',
                  borderRadius: '12px',
                  border: isSelected ? '1.5px solid var(--b2)' : '1px solid rgba(203, 213, 225, 0.6)',
                  background: isSelected ? 'rgba(37, 99, 235, 0.1)' : 'rgba(255, 255, 255, 0.85)',
                  color: isSelected ? '#1e40af' : '#334155',
                  fontSize: '13px',
                  fontWeight: isSelected ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <span>{cond.nome}</span>
                <span style={{ fontSize: '10px', color: '#64748b', fontWeight: 400 }}>({cond.codigo_cid10})</span>
                <span
                  style={{
                    width: '7px',
                    height: '7px',
                    borderRadius: '50%',
                    background: badge.text,
                    display: 'inline-block',
                  }}
                  title={badge.label}
                />
              </button>
            );
          })}
        </div>
      </div>

      {/* Estado de Erro ou Loading */}
      {loading && !dashboardData && (
        <div className="glass" style={{ padding: '60px', textAlign: 'center', borderRadius: '24px' }}>
          <RefreshCw className="animate-spin" style={{ margin: '0 auto 12px', color: '#2563eb' }} size={28} />
          <p style={{ color: 'var(--mut)', margin: 0, fontSize: '14px' }}>
            Carregando dados oficiais da vigilância epidemiológica do DF…
          </p>
        </div>
      )}

      {error && (
        <div
          style={{
            padding: '16px 20px',
            borderRadius: '16px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#b91c1c',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* -------------------------------------------------------------------
          PAINEL PRINCIPAL: DADOS DO AGRAVO ATIVO
      ------------------------------------------------------------------- */}
      {dashboardData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* Header do Agravo Ativo com Badge de Alerta e Descrição */}
          <div
            className="glass"
            style={{
              padding: '20px 24px',
              borderRadius: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <h2 style={{ fontSize: '24px', fontWeight: 600, color: 'var(--ink)', margin: 0 }}>
                    {dashboardData.condition.nome}
                  </h2>
                  <span
                    style={{
                      background: 'rgba(37, 99, 235, 0.1)',
                      color: '#1d4ed8',
                      fontSize: '12px',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '8px',
                    }}
                  >
                    CID-10 {dashboardData.condition.codigo_cid10}
                  </span>
                  <span
                    style={{
                      background: getAlertBadge(dashboardData.condition.nivel_alerta).bg,
                      color: getAlertBadge(dashboardData.condition.nivel_alerta).text,
                      border: `1px solid ${getAlertBadge(dashboardData.condition.nivel_alerta).border}`,
                      fontSize: '11px',
                      fontWeight: 700,
                      padding: '3px 10px',
                      borderRadius: '99px',
                    }}
                  >
                    {getAlertBadge(dashboardData.condition.nivel_alerta).label}
                  </span>
                </div>
                <p style={{ margin: '6px 0 0', fontSize: '13px', color: '#475569', maxWidth: '750px', lineHeight: 1.5 }}>
                  {dashboardData.condition.descricao}
                </p>
              </div>

              {/* Botão de Atalho para Tirar Dúvidas com a SUSANNA */}
              {onAskSuzanna && (
                <button
                  onClick={() =>
                    onAskSuzanna(
                      `Olá SUSANNA, gostaria de saber quais são os principais sintomas e cuidados em relação a ${dashboardData.condition.nome} no Distrito Federal.`
                    )
                  }
                  style={{
                    padding: '10px 18px',
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, #2563eb, #1e40af)',
                    color: '#ffffff',
                    border: 'none',
                    fontWeight: 600,
                    fontSize: '13px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    boxShadow: '0 4px 16px rgba(37, 99, 235, 0.28)',
                    transition: 'transform 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
                  onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
                >
                  <MessageSquare size={16} />
                  <span>Perguntar à SUSANNA</span>
                </button>
              )}
            </div>

            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '18px',
                paddingTop: '10px',
                borderTop: '1px dashed rgba(203, 213, 225, 0.7)',
                fontSize: '12px',
                color: '#64748b',
              }}
            >
              <div>
                <strong style={{ color: '#1e3a8a' }}>Transmissão/Vetor:</strong> {dashboardData.condition.vetor_ou_transmissao}
              </div>
              <div>
                <strong style={{ color: '#1e3a8a' }}>Sazonalidade:</strong> {dashboardData.condition.sazonalidade}
              </div>
              <div>
                <strong style={{ color: '#1e3a8a' }}>Faixa mais atingida:</strong> {dashboardData.condition.faixa_etaria_predominante}
              </div>
            </div>
          </div>

          {/* -----------------------------------------------------------------
              GRID DE KPIS (4 CARTÕES MODERNOS EM LIQUID GLASS)
          ----------------------------------------------------------------- */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '14px',
            }}
          >
            {/* KPI 1: Casos Notificados */}
            <div className="glass" style={{ padding: '18px 20px', borderRadius: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#64748b' }}>Notificações no DF (Ano)</span>
                <Activity size={18} style={{ color: '#2563eb' }} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: '#0f172a', margin: '8px 0 4px' }}>
                {dashboardData.kpis.total_casos_ano.toLocaleString('pt-BR')}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>
                Última semana: <strong style={{ color: '#1e3a8a' }}>{dashboardData.kpis.casos_ultima_semana}</strong> casos
              </div>
            </div>

            {/* KPI 2: Tendência Semanal */}
            <div className="glass" style={{ padding: '18px 20px', borderRadius: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#64748b' }}>Tendência Semanal</span>
                {dashboardData.kpis.tendencia === 'alta' ? (
                  <ArrowUpRight size={18} style={{ color: '#dc2626' }} />
                ) : dashboardData.kpis.tendencia === 'queda' ? (
                  <ArrowDownRight size={18} style={{ color: '#16a34a' }} />
                ) : (
                  <Minus size={18} style={{ color: '#2563eb' }} />
                )}
              </div>
              <div
                style={{
                  fontSize: '28px',
                  fontWeight: 700,
                  color:
                    dashboardData.kpis.tendencia === 'alta'
                      ? '#dc2626'
                      : dashboardData.kpis.tendencia === 'queda'
                      ? '#16a34a'
                      : '#2563eb',
                  margin: '8px 0 4px',
                }}
              >
                {dashboardData.kpis.variacao_semanal_pct > 0 ? `+${dashboardData.kpis.variacao_semanal_pct}%` : `${dashboardData.kpis.variacao_semanal_pct}%`}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>
                {dashboardData.kpis.tendencia === 'alta'
                  ? 'Transmissão em aceleração'
                  : dashboardData.kpis.tendencia === 'queda'
                  ? 'Curva em desaceleração'
                  : 'Comportamento estável'}
              </div>
            </div>

            {/* KPI 3: Incidência Distrital */}
            <div className="glass" style={{ padding: '18px 20px', borderRadius: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#64748b' }}>Taxa de Incidência</span>
                <Info size={18} style={{ color: '#60a5fa' }} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: '#0f172a', margin: '8px 0 4px' }}>
                {dashboardData.kpis.taxa_incidencia_distrital_100k.toLocaleString('pt-BR', { minimumFractionDigits: 1 })}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>Por 100 mil habitantes no DF</div>
            </div>

            {/* KPI 4: Região Mais Afetada (Hotspot) */}
            <div className="glass" style={{ padding: '18px 20px', borderRadius: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#64748b' }}>Região Mais Afetada</span>
                <MapPin size={18} style={{ color: '#ea580c' }} />
              </div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', margin: '8px 0 4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {dashboardData.kpis.ra_hotspot_nome}
              </div>
              <div style={{ fontSize: '11px', color: '#64748b' }}>
                <strong style={{ color: '#1e3a8a' }}>{dashboardData.kpis.ra_hotspot_casos}</strong> casos acumulados
              </div>
            </div>
          </div>

          {/* -----------------------------------------------------------------
              GRÁFICO INTERATIVO DE EVOLUÇÃO TEMPORAL (SPLINE AREA)
          ----------------------------------------------------------------- */}
          <div className="glass" style={{ padding: '22px 24px', borderRadius: '24px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', gap: '8px' }}>
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ink)', margin: 0 }}>
                  Evolução temporal por Semana Epidemiológica (SE 36 a 45)
                </h3>
                <span style={{ fontSize: '12px', color: 'var(--mut)' }}>
                  Passe o cursor sobre os pontos da curva para inspecionar os casos e a média móvel.
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '12px', height: '3px', background: '#2563eb', borderRadius: '2px' }} />
                  <span style={{ color: '#475569' }}>Casos semanais</span>
                </div>
              </div>
            </div>

            {renderInteractiveChart()}
          </div>

          {/* -----------------------------------------------------------------
              GRID COM 2 COLUNAS: RANKING DE RAs & DIRETRIZES CLÍNICAS / PREVENÇÃO
          ----------------------------------------------------------------- */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '18px' }}>
            {/* Coluna 1: Distribuição por Região Administrativa */}
            <div className="glass" style={{ padding: '22px 24px', borderRadius: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ink)', margin: 0 }}>
                  Casos por Região Administrativa
                </h3>
                <span style={{ fontSize: '11px', color: '#64748b' }}>Top Regiões</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {dashboardData.regions.map((reg) => {
                  const maxCases = dashboardData.regions[0]?.casos || 1;
                  const barWidthPercent = Math.max(8, (reg.casos / maxCases) * 100);
                  return (
                    <div key={reg.ra_id} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                        <span style={{ fontWeight: 500, color: '#1e293b' }}>{reg.ra_nome}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '12px', color: '#64748b' }}>{reg.percentual_distrital}%</span>
                          <strong style={{ color: '#1e3a8a', minWidth: '40px', textAlign: 'right' }}>
                            {reg.casos.toLocaleString('pt-BR')}
                          </strong>
                        </div>
                      </div>
                      <div
                        style={{
                          height: '9px',
                          borderRadius: '99px',
                          background: 'rgba(226, 232, 240, 0.7)',
                          overflow: 'hidden',
                          width: '100%',
                        }}
                      >
                        <div
                          style={{
                            height: '100%',
                            width: `${barWidthPercent}%`,
                            borderRadius: '99px',
                            background: 'linear-gradient(90deg, #60a5fa, #2563eb)',
                            transition: 'width 0.8s ease',
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Coluna 2: Sinais de Alarme & Onde Buscar Socorro */}
            <div className="glass" style={{ padding: '22px 24px', borderRadius: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--ink)', margin: 0 }}>
                  Sinais de Alarme & Conduta SES-DF
                </h3>
                <span style={{ fontSize: '12px', color: 'var(--mut)' }}>
                  Protocolos clínicos oficiais e recomendações preventivas.
                </span>
              </div>

              {/* Lista de Sinais de Alarme & Prevenção */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {dashboardData.guidelines.map((g, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '10px 14px',
                      borderRadius: '14px',
                      background:
                        g.tipo === 'sinal_alarme'
                          ? 'rgba(239, 68, 68, 0.08)'
                          : g.tipo === 'prevencao'
                          ? 'rgba(37, 99, 235, 0.08)'
                          : 'rgba(241, 245, 249, 0.85)',
                      border:
                        g.tipo === 'sinal_alarme'
                          ? '1px solid rgba(239, 68, 68, 0.25)'
                          : g.tipo === 'prevencao'
                          ? '1px solid rgba(37, 99, 235, 0.2)'
                          : '1px solid rgba(203, 213, 225, 0.6)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {g.tipo === 'sinal_alarme' ? (
                        <ShieldAlert size={16} style={{ color: '#dc2626' }} />
                      ) : (
                        <CheckCircle2 size={16} style={{ color: '#2563eb' }} />
                      )}
                      <strong style={{ fontSize: '13px', color: g.tipo === 'sinal_alarme' ? '#991b1b' : '#1e3a8a' }}>
                        {g.titulo}
                      </strong>
                    </div>
                    <p style={{ margin: 0, fontSize: '12px', color: '#475569', lineHeight: 1.45 }}>
                      {g.descricao}
                    </p>
                  </div>
                ))}
              </div>

              {/* Unidades de Referência no DF */}
              <div style={{ marginTop: 'auto', paddingTop: '10px', borderTop: '1px dashed #cbd5e1' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#1e3a8a', textTransform: 'uppercase' }}>
                  Unidades de Referência para Atendimento:
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                  {dashboardData.unidades_referencia.map((u, ui) => (
                    <div key={ui} style={{ fontSize: '12px', color: '#334155' }}>
                      <strong style={{ color: '#2563eb' }}>{u.tipo_servico}:</strong> {u.nome_exemplo} —{' '}
                      <span style={{ color: '#64748b' }}>{u.papel_clinico}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Rodapé de Fonte Oficial */}
          <div
            style={{
              padding: '12px 18px',
              borderRadius: '16px',
              background: 'rgba(255, 255, 255, 0.55)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '12px',
              color: '#64748b',
            }}
          >
            <span>
              Fonte dos dados: <strong>{dashboardData.fonte_oficial}</strong>
            </span>
            <span>Atualizado: {dashboardData.data_atualizacao}</span>
          </div>
        </div>
      )}
    </div>
  );
}
