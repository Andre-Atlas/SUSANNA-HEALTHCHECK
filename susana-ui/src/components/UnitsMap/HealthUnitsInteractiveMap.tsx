'use client';

import React, { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import type { MapTileLayerType } from './RealCartographicMap';
import { formatKm, haversineKm, sortByDistance, type Coords } from '@/lib/geo';

export interface HealthUnitItem {
  id: string;
  nome: string;
  ra: string;
  ra_display: string;
  tipo: string;
  tipo_display: string;
  cluster: string;
  endereco: string;
  horario: string;
  servicos: string[];
  referencia_emergencia?: string;
  url?: string;
  telefone?: string;
  atendimento_24h?: boolean;
  bairro?: string;
  lat?: number;
  lng?: number;
  svg_x: number;
  svg_y: number;
}

export interface RADistribution {
  ra: string;
  ra_display: string;
  unit_count: number;
}

interface HealthUnitsInteractiveMapProps {
  units: HealthUnitItem[];
  raList: RADistribution[];
  selectedRA: string;
  onSelectRA: (ra: string) => void;
  activeType: string;
  onSelectType: (tipo: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedUnit: HealthUnitItem | null;
  onSelectUnit: (unit: HealthUnitItem | null) => void;
  onAskSuzanna: (unit: HealthUnitItem) => void;
  isLoading?: boolean;
  /** Localização atual (só no aparelho): ordena por distância e mostra "você" no mapa. */
  userCoords?: Coords | null;
}

// Cores semânticas oficiais do SUS Digital
const PIN_COLORS: Record<string, { bg: string; border: string; glow: string; label: string }> = {
  ubs: { bg: '#2563eb', border: '#1d4ed8', glow: 'rgba(37,99,235,0.3)', label: 'UBS' },
  upa: { bg: '#ea580c', border: '#c2410c', glow: 'rgba(234,88,12,0.3)', label: 'UPA 24h' },
  hospital: { bg: '#dc2626', border: '#b91c1c', glow: 'rgba(220,38,38,0.3)', label: 'Hospital' },
  regional: { bg: '#9333ea', border: '#7e22ce', glow: 'rgba(147,51,234,0.3)', label: 'Regional' },
  policlinica: { bg: '#0d9488', border: '#0f766e', glow: 'rgba(13,148,136,0.3)', label: 'Policlínica' },
  caps: { bg: '#059669', border: '#047857', glow: 'rgba(5,150,105,0.3)', label: 'CAPS' },
  farmacia: { bg: '#7c3aed', border: '#6d28d9', glow: 'rgba(124,58,237,0.3)', label: 'Farmácia' },
  laboratorio: { bg: '#0891b2', border: '#0e7490', glow: 'rgba(8,145,178,0.3)', label: 'Laboratório' },
};

const DEFAULT_PIN_COLOR = { bg: '#2563eb', border: '#1d4ed8', glow: 'rgba(37,99,235,0.3)', label: 'Saúde' };

// Carregamento dinâmico sem SSR do Motor Cartográfico Real de Brasília/DF (Leaflet)
const RealCartographicMap = dynamic(() => import('./RealCartographicMap'), {
  ssr: false,
  loading: () => (
    <div
      style={{
        width: '100%',
        height: '560px',
        borderRadius: '20px',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        color: '#475569',
        fontSize: '14px',
        fontWeight: 600,
      }}
    >
      <div style={{ fontSize: '36px', animation: 'pulse 1.5s infinite' }}>🗺️</div>
      <div style={{ color: '#1e40af' }}>Carregando Cartografia Real de Brasília e do DF...</div>
      <div style={{ fontSize: '12px', color: '#64748b', fontWeight: 400 }}>
        Mapeando ruas, quadras, Lago Paranoá, vegetação e unidades de saúde
      </div>
    </div>
  ),
});

export const HealthUnitsInteractiveMap: React.FC<HealthUnitsInteractiveMapProps> = ({
  units,
  raList,
  selectedRA,
  onSelectRA,
  activeType,
  onSelectType,
  searchQuery,
  onSearchChange,
  selectedUnit,
  onSelectUnit,
  onAskSuzanna,
  userCoords = null,
}) => {
  const [viewMode, setViewMode] = useState<'mapa' | 'lista'>('mapa');
  const [mapLayer, setMapLayer] = useState<MapTileLayerType>('osm');

  // Filtragem e busca em memória instantânea para sincronia visual
  const matchedUnits = useMemo(() => {
    return units.filter((u) => {
      // Filtro de RA
      if (selectedRA && selectedRA !== 'todas' && selectedRA !== '') {
        const raNorm = selectedRA.toLowerCase().replace(' ', '_');
        if (u.ra !== raNorm && !u.ra.includes(raNorm)) return false;
      }

      // Filtro de Tipo
      if (activeType && activeType !== 'todas') {
        const typeNorm = activeType.toLowerCase();
        if (typeNorm === 'hospitais' || typeNorm === 'hospital') {
          if (u.tipo !== 'hospital' && u.tipo !== 'regional' && !u.nome.toLowerCase().includes('hospital')) {
            return false;
          }
        } else if (typeNorm === 'policlinica' || typeNorm === 'policlinicas') {
          if (u.tipo !== 'policlinica' && !u.nome.toLowerCase().includes('policl')) {
            return false;
          }
        } else if (typeNorm === 'caps') {
          if (u.tipo !== 'caps' && !u.nome.toLowerCase().includes('caps')) {
            return false;
          }
        } else if (typeNorm === 'farmacia' || typeNorm === 'farmacias') {
          if (u.tipo !== 'farmacia' && !u.nome.toLowerCase().includes('farm')) {
            return false;
          }
        } else if (typeNorm === 'laboratorio' || typeNorm === 'laboratorios') {
          if (u.tipo !== 'laboratorio' && !u.nome.toLowerCase().includes('laborat') && !u.nome.toLowerCase().includes('lacen')) {
            return false;
          }
        } else if (u.tipo !== typeNorm) {
          return false;
        }
      }

      // Filtro de busca textual
      if (searchQuery.trim()) {
        const stripAccents = (str: string) => str ? str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase() : '';
        const q = stripAccents(searchQuery.trim());
        const matchesName = stripAccents(u.nome).includes(q);
        const matchesEnd = stripAccents(u.endereco).includes(q);
        const matchesRA = stripAccents(u.ra_display).includes(q);
        const matchesBairro = u.bairro ? stripAccents(u.bairro).includes(q) : false;
        const matchesTipo = stripAccents(u.tipo_display).includes(q);
        const matchesServ = u.servicos.some((s) => stripAccents(s).includes(q));
        if (!matchesName && !matchesEnd && !matchesRA && !matchesBairro && !matchesTipo && !matchesServ) {
          return false;
        }
      }

      return true;
    });
  }, [units, selectedRA, activeType, searchQuery]);

  const filteredUnits = useMemo(
    () => (userCoords ? sortByDistance(matchedUnits, userCoords) : matchedUnits),
    [matchedUnits, userCoords]
  );
  const distanceTo = (u: HealthUnitItem) =>
    userCoords && u.lat != null && u.lng != null ? formatKm(haversineKm(userCoords, { lat: u.lat, lng: u.lng })) : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
      {/* ------------------------------------------------------------- */}
      {/* 1. BARRA SUPERIOR DE BUSCA E FILTROS EM TEMPO REAL            */}
      {/* ------------------------------------------------------------- */}
      <div
        style={{
          background: 'rgba(255, 255, 255, 0.88)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid var(--b2)',
          borderRadius: '16px',
          padding: '14px 18px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 4px 20px rgba(15, 23, 42, 0.04)',
        }}
      >
        {/* Campo de Busca em Tempo Real */}
        <div style={{ flex: '1 1 280px', position: 'relative', minWidth: '240px' }}>
          <span
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#475569',
              fontSize: '15px',
              pointerEvents: 'none',
            }}
            aria-hidden="true"
          >
            🔍
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Buscar por UBS, UPA, especialidade ou bairro..."
            aria-label="Buscar unidades de saúde por nome, endereço ou serviço"
            style={{
              width: '100%',
              padding: '9px 36px 9px 36px',
              borderRadius: '12px',
              border: '1px solid var(--b2)',
              background: '#ffffff',
              fontSize: '13px',
              color: '#0f172a',
              outline: 'none',
              boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.03)',
              transition: 'border-color 0.15s ease',
            }}
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => onSearchChange('')}
              aria-label="Limpar campo de pesquisa"
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: '#e2e8f0',
                border: 'none',
                borderRadius: '50%',
                width: '20px',
                height: '20px',
                fontSize: '11px',
                color: '#334155',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              title="Limpar busca"
            >
              ✕
            </button>
          )}
        </div>

        {/* Dropdown de Região Administrativa */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: '0 1 auto' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#1e3a8a' }}>Região:</span>
          <select
            value={selectedRA}
            onChange={(e) => {
              onSelectRA(e.target.value);
              onSelectUnit(null);
            }}
            aria-label="Filtrar por Região Administrativa"
            style={{
              padding: '9px 14px',
              borderRadius: '12px',
              border: '1px solid var(--b2)',
              background: '#ffffff',
              fontSize: '13px',
              color: '#0f172a',
              fontWeight: 500,
              cursor: 'pointer',
              outline: 'none',
              maxWidth: '220px',
            }}
          >
            <option value="todas">Todas as 33 RAs do DF</option>
            {raList.map((r) => (
              <option key={r.ra} value={r.ra}>
                {r.ra_display} ({r.unit_count})
              </option>
            ))}
          </select>
        </div>

        {/* Alternador Visualizador: Mapa vs Lista */}
        <div
          style={{
            display: 'inline-flex',
            borderRadius: '10px',
            background: 'rgba(241, 245, 249, 0.9)',
            padding: '3px',
            border: '1px solid var(--b2)',
          }}
        >
          <button
            type="button"
            onClick={() => setViewMode('mapa')}
            aria-label="Visualizar em modo mapa interativo"
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: 'none',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              background: viewMode === 'mapa' ? '#ffffff' : 'transparent',
              color: viewMode === 'mapa' ? '#1e40af' : '#64748b',
              boxShadow: viewMode === 'mapa' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              transition: 'all 0.15s ease',
            }}
          >
            🗺️ Mapa Interativo
          </button>
          <button
            type="button"
            onClick={() => setViewMode('lista')}
            aria-label="Visualizar em modo lista de postos de saúde"
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              border: 'none',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              background: viewMode === 'lista' ? '#ffffff' : 'transparent',
              color: viewMode === 'lista' ? '#1e40af' : '#64748b',
              boxShadow: viewMode === 'lista' ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
              transition: 'all 0.15s ease',
            }}
          >
            📋 Lista ({filteredUnits.length})
          </button>
        </div>
      </div>

      {/* Filtros em Pílulas Rápidas por Categoria */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
        {[
          { key: 'todas', label: 'Todas as Unidades', icon: '📍' },
          { key: 'ubs', label: 'UBS (Atenção Primária)', icon: '🏥' },
          { key: 'upa', label: 'UPA 24h', icon: '🚨' },
          { key: 'hospitais', label: 'Hospitais', icon: '🏨' },
          { key: 'policlinica', label: 'Policlínicas', icon: '🩺' },
          { key: 'caps', label: 'CAPS', icon: '🧠' },
          { key: 'farmacia', label: 'Farmácia', icon: '💊' },
          { key: 'laboratorio', label: 'Laboratórios', icon: '🧪' },
        ].map((tab) => {
          const isSelected = activeType.toLowerCase() === tab.key;
          return (
            <button
              key={tab.key}
              type="button"
              onClick={() => {
                onSelectType(tab.key);
                onSelectUnit(null);
              }}
              aria-pressed={isSelected}
              style={{
                padding: '6px 12px',
                borderRadius: '20px',
                border: isSelected ? '1px solid #2563eb' : '1px solid var(--b2)',
                background: isSelected ? 'linear-gradient(135deg, #2563eb, #1d4ed8)' : 'rgba(255, 255, 255, 0.8)',
                color: isSelected ? '#ffffff' : '#334155',
                fontSize: '12px',
                fontWeight: isSelected ? 600 : 500,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: isSelected ? '0 2px 8px rgba(37, 99, 235, 0.25)' : 'none',
                transition: 'all 0.15s ease',
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          );
        })}

        <div style={{ marginLeft: 'auto', fontSize: '12px', color: '#475569', fontWeight: 500 }}>
          Mostrando <b>{filteredUnits.length}</b> de {units.length} estabelecimentos
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 2. ÁREA PRINCIPAL DO MAPA OU LISTA                             */}
      {/* ------------------------------------------------------------- */}
      {viewMode === 'mapa' ? (
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '560px',
            borderRadius: '20px',
            overflow: 'hidden',
            border: '1px solid var(--b2)',
            background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
            boxShadow: '0 10px 30px rgba(15, 23, 42, 0.06)',
          }}
        >
          {/* Motor Cartográfico Real de Brasília/DF (OpenStreetMap / Esri Satélite) */}
          <RealCartographicMap
            units={filteredUnits}
            selectedUnit={selectedUnit}
            onSelectUnit={onSelectUnit}
            selectedRA={selectedRA}
            activeLayer={mapLayer}
            onChangeLayer={setMapLayer}
            userCoords={userCoords}
          />

          {/* Banner informativo quando nenhuma unidade for encontrada no Modo Mapa */}
          {filteredUnits.length === 0 && (
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 420,
                background: 'rgba(255, 255, 255, 0.94)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                padding: '20px 28px',
                borderRadius: '16px',
                border: '1px solid var(--b2)',
                boxShadow: '0 8px 32px rgba(15, 23, 42, 0.12)',
                textAlign: 'center',
                maxWidth: '380px',
              }}
            >
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🔍</div>
              <div style={{ fontWeight: 600, color: '#0f172a', fontSize: '14px', marginBottom: '4px' }}>
                Nenhum estabelecimento encontrado
              </div>
              <div style={{ fontSize: '12px', color: '#64748b', lineHeight: 1.5 }}>
                Nenhuma unidade de saúde corresponde aos filtros ativos. Tente buscar por outro termo ou selecione &ldquo;Todas as Unidades&rdquo;.
              </div>
            </div>
          )}

          {/* ------------------------------------------------------------- */}
          {/* CARD FLUTUANTE DE ESTABELECIMENTO (POPUP EM LIQUID GLASS)      */}
          {/* ------------------------------------------------------------- */}
          {selectedUnit && (
            <div
              style={{
                position: 'absolute',
                top: '64px',
                right: '16px',
                zIndex: 450,
                width: '340px',
                maxWidth: 'calc(100% - 32px)',
                maxHeight: 'calc(100% - 80px)',
                overflowY: 'auto',
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(24px)',
                WebkitBackdropFilter: 'blur(24px)',
                border: '1px solid rgba(226, 232, 240, 0.95)',
                borderRadius: '16px',
                boxShadow: '0 16px 40px rgba(15, 23, 42, 0.16)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
              }}
            >
              {/* Cabeçalho do Card */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', fontWeight: 600 }}>
                    Unidades de Saúde no DF
                  </div>
                  <h4 style={{ margin: '3px 0 0', fontSize: '15px', fontWeight: 700, color: '#0a1b3d', lineHeight: 1.25 }}>
                    {selectedUnit.nome}
                  </h4>
                </div>
                <button
                  type="button"
                  onClick={() => onSelectUnit(null)}
                  aria-label="Fechar detalhes da unidade"
                  style={{
                    background: '#f1f5f9',
                    border: 'none',
                    borderRadius: '50%',
                    minWidth: '40px',
                    minHeight: '40px',
                    fontSize: '13px',
                    color: '#334155',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'background 0.15s ease',
                  }}
                  title="Fechar detalhes"
                >
                  ✕
                </button>
              </div>

              {/* Informações Estruturadas (Padrão da Imagem de Referência) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', color: '#334155' }}>
                <div>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>Estabelecimento: </span>
                  <span>{selectedUnit.tipo_display}</span>
                </div>

                <div>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>Endereço: </span>
                  <span>{selectedUnit.endereco}</span>
                </div>

                <div>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>Bairro / RA: </span>
                  <span>{selectedUnit.bairro || selectedUnit.ra_display}</span>
                </div>

                <div>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>Telefone: </span>
                  <span style={{ color: '#2563eb', fontWeight: 500 }}>{selectedUnit.telefone || '136 (Disque Saúde)'}</span>
                </div>

                {/* Badge de Atendimento 24h */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>24h: </span>
                  {selectedUnit.atendimento_24h ? (
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '99px',
                        background: '#dcfce7',
                        color: '#166534',
                        fontWeight: 600,
                        fontSize: '11px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      🟢 Sim (Ininterrupto 24 horas)
                    </span>
                  ) : (
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '99px',
                        background: '#f1f5f9',
                        color: '#475569',
                        fontWeight: 500,
                        fontSize: '11px',
                      }}
                    >
                      Não ({selectedUnit.horario})
                    </span>
                  )}
                </div>

                {/* Serviços Oferecidos */}
                {selectedUnit.servicos && selectedUnit.servicos.length > 0 && (
                  <div style={{ marginTop: '4px' }}>
                    <span style={{ fontWeight: 600, color: '#0f172a', display: 'block', marginBottom: '4px' }}>
                      Serviços Disponíveis:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {selectedUnit.servicos.slice(0, 4).map((srv, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: '2px 7px',
                            borderRadius: '6px',
                            background: '#eff6ff',
                            color: '#1d4ed8',
                            fontSize: '10px',
                            fontWeight: 500,
                          }}
                        >
                          {srv}
                        </span>
                      ))}
                      {selectedUnit.servicos.length > 4 && (
                        <span style={{ fontSize: '10px', color: '#64748b', alignSelf: 'center' }}>
                          +{selectedUnit.servicos.length - 4} mais
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Referência de Emergência (Se houver) */}
                {selectedUnit.referencia_emergencia && (
                  <div
                    style={{
                      marginTop: '4px',
                      padding: '6px 8px',
                      borderRadius: '8px',
                      background: '#fef2f2',
                      border: '1px solid #fee2e2',
                      color: '#991b1b',
                      fontSize: '11px',
                    }}
                  >
                    🚨 <b>Emergência:</b> {selectedUnit.referencia_emergencia}
                  </div>
                )}
              </div>

              {/* Ação Direta Integrada com a SUSANNA */}
              <button
                type="button"
                onClick={() => onAskSuzanna(selectedUnit)}
                aria-label={`Tirar dúvidas com a SUSANNA sobre ${selectedUnit.nome}`}
                style={{
                  marginTop: '6px',
                  padding: '10px 12px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                  color: '#ffffff',
                  border: 'none',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  boxShadow: '0 2px 8px rgba(37, 99, 235, 0.3)',
                  transition: 'opacity 0.15s ease',
                }}
              >
                <span>💬 Tirar dúvidas com a SUSANNA sobre esta unidade</span>
              </button>
            </div>
          )}
        </div>
      ) : (
        /* ------------------------------------------------------------- */
        /* MODO LISTA DE UNIDADES ENCONTRADAS                            */
        /* ------------------------------------------------------------- */
        <div
          style={{
            maxHeight: '560px',
            overflowY: 'auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '12px',
            padding: '4px',
          }}
        >
          {filteredUnits.length === 0 ? (
            <div
              style={{
                gridColumn: '1 / -1',
                textAlign: 'center',
                padding: '40px 20px',
                color: '#64748b',
                background: 'rgba(255,255,255,0.7)',
                borderRadius: '16px',
                border: '1px solid var(--b2)',
              }}
            >
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🔍</div>
              <h4 style={{ margin: 0, color: '#1e293b' }}>Nenhuma unidade encontrada</h4>
              <p style={{ margin: '4px 0 0', fontSize: '13px' }}>
                Tente ajustar os termos de pesquisa ou selecionar outra Região Administrativa.
              </p>
            </div>
          ) : (
            filteredUnits.map((u) => {
              const isSelected = selectedUnit?.id === u.id;
              const pinStyle = PIN_COLORS[u.tipo] || DEFAULT_PIN_COLOR;

              return (
                <div
                  key={u.id}
                  onClick={() => {
                    onSelectUnit(u);
                    setViewMode('mapa');
                  }}
                  style={{
                    background: isSelected ? '#eff6ff' : 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(16px)',
                    border: isSelected ? '1.5px solid #2563eb' : '1px solid var(--b2)',
                    borderRadius: '14px',
                    padding: '14px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                    boxShadow: isSelected ? '0 4px 14px rgba(37,99,235,0.15)' : '0 2px 6px rgba(0,0,0,0.03)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <b style={{ fontSize: '13px', color: '#0f172a' }}>{u.nome}</b>
                    <span
                      style={{
                        fontSize: '10px',
                        padding: '2px 6px',
                        borderRadius: '6px',
                        background: pinStyle.bg,
                        color: '#fff',
                        fontWeight: 600,
                      }}
                    >
                      {pinStyle.label}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#2563eb', fontWeight: 500 }}>
                    📍 {u.bairro || u.ra_display}
                    {distanceTo(u) && <span style={{ color: '#64748b', fontWeight: 400 }}> · {distanceTo(u)}</span>}
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b' }}>
                    🏢 {u.endereco}
                  </div>
                  <div style={{ fontSize: '11px', color: u.atendimento_24h ? '#166534' : '#475569', fontWeight: u.atendimento_24h ? 600 : 400 }}>
                    ⏰ {u.atendimento_24h ? '🟢 24 horas ininterruptas' : u.horario}
                  </div>

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAskSuzanna(u);
                    }}
                    style={{
                      marginTop: '4px',
                      padding: '6px 10px',
                      borderRadius: '8px',
                      background: 'rgba(37, 99, 235, 0.1)',
                      color: '#1d4ed8',
                      border: '1px solid rgba(37, 99, 235, 0.2)',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '4px',
                    }}
                  >
                    💬 Perguntar à SUSANNA
                  </button>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
