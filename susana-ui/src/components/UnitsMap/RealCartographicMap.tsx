'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import type { HealthUnitItem } from './HealthUnitsInteractiveMap';

export type MapTileLayerType = 'osm' | 'satellite';

interface RealCartographicMapProps {
  units: HealthUnitItem[];
  selectedUnit: HealthUnitItem | null;
  onSelectUnit: (unit: HealthUnitItem | null) => void;
  selectedRA?: string;
  activeLayer?: MapTileLayerType;
  onChangeLayer?: (layer: MapTileLayerType) => void;
  userCoords?: { lat: number; lng: number } | null;
}

// Configurações de Camadas Cartográficas Oficiais
const TILE_LAYERS: Record<
  MapTileLayerType,
  {
    name: string;
    icon: string;
    url: string;
    options: {
      attribution: string;
      maxZoom: number;
      subdomains?: string[];
    };
  }
> = {
  osm: {
    name: 'Mapa Urbano',
    icon: '🗺️',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    options: {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
      subdomains: ['a', 'b', 'c'],
    },
  },
  satellite: {
    name: 'Satélite Aéreo',
    icon: '🛰️',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    options: {
      attribution: 'Tiles &copy; Esri &mdash; Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and GIS User Community',
      maxZoom: 18,
    },
  },
};

// Cores semânticas oficiais do SUS Digital
const PIN_COLORS: Record<string, { bg: string; border: string; label: string }> = {
  ubs: { bg: '#2563eb', border: '#1d4ed8', label: 'UBS' },
  upa: { bg: '#ea580c', border: '#c2410c', label: 'UPA 24h' },
  hospital: { bg: '#dc2626', border: '#b91c1c', label: 'Hospital' },
  regional: { bg: '#9333ea', border: '#7e22ce', label: 'Regional' },
  policlinica: { bg: '#0d9488', border: '#0f766e', label: 'Policlínica' },
  caps: { bg: '#059669', border: '#047857', label: 'CAPS' },
  farmacia: { bg: '#7c3aed', border: '#6d28d9', label: 'Farmácia' },
  laboratorio: { bg: '#0891b2', border: '#0e7490', label: 'Laboratório' },
};

const DEFAULT_PIN_COLOR = { bg: '#2563eb', border: '#1d4ed8', label: 'Saúde' };

// Centro Geográfico do Distrito Federal (Marco Zero / Praça dos Três Poderes - Brasília)
const DF_DEFAULT_CENTER: [number, number] = [-15.7942, -47.8822];
const DF_DEFAULT_ZOOM = 11;

// Limites Geográficos Rígidos do Distrito Federal (Bounding Box)
const DF_BOUNDS: [[number, number], [number, number]] = [
  [-16.15, -48.45], // Sudoeste do DF
  [-15.40, -47.15], // Nordeste do DF
];

// Helper para gerar o L.divIcon com SVG de alta fidelidade
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function createPinIcon(L: any, tipo: string, isSelected: boolean) {
  const pinStyle = PIN_COLORS[tipo] || DEFAULT_PIN_COLOR;
  const color = isSelected ? '#ef4444' : pinStyle.bg;
  const strokeColor = isSelected ? '#f59e0b' : '#ffffff';
  const strokeWidth = isSelected ? '2.6' : '1.8';

  // Glifo interno diferenciado por categoria (WCAG 1.4.1 - não depender exclusivamente de cor)
  let glyphHtml = `
    <!-- Cruz médica branca (UBS, UPA, Hospital, Policlínica, CAPS) -->
    <rect x="12.4" y="7.5" width="3.2" height="11" rx="1" fill="#ffffff"/>
    <rect x="8.5" y="11.4" width="11" height="3.2" rx="1" fill="#ffffff"/>
  `;
  if (tipo === 'laboratorio') {
    // Frasco / tubo laboratorial para Laboratórios
    glyphHtml = `
      <path d="M12 7.5H16M13 7.5V10.5L9.5 16.5C8.8 17.6 9.6 19 10.9 19H17.1C18.4 19 19.2 17.6 18.5 16.5L15 10.5V7.5" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="rgba(255,255,255,0.2)"/>
      <circle cx="14" cy="16" r="1" fill="#ffffff"/>
    `;
  } else if (tipo === 'farmacia') {
    // Cápsula farmacêutica para Farmácia
    glyphHtml = `
      <rect x="10" y="9" width="8" height="10" rx="4" stroke="#ffffff" stroke-width="1.8" fill="none"/>
      <line x1="10" y1="14" x2="18" y2="14" stroke="#ffffff" stroke-width="1.6"/>
    `;
  }

  const iconHtml = `
    <div class="sus-unit-pin-marker ${isSelected ? 'sus-unit-pin-selected' : ''}" style="width: 28px; height: 34px; transform-origin: 14px 32px; ${isSelected ? 'transform: scale(1.25); filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.8));' : ''}">
      <svg width="28" height="34" viewBox="0 0 28 34" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 3px 5px rgba(0,0,0,0.25));">
        <!-- Sombra de solo -->
        <ellipse cx="14" cy="32" rx="7" ry="2" fill="rgba(15, 23, 42, 0.35)" />
        <!-- Gota de mapa invertida -->
        <path d="M14 0C6.26801 0 0 6.26801 0 14C0 24.5 14 32 14 32C14 32 28 24.5 28 14C28 6.26801 21.732 0 14 0Z" fill="${color}" stroke="${strokeColor}" stroke-width="${strokeWidth}"/>
        ${glyphHtml}
      </svg>
    </div>
  `;

  return L.divIcon({
    html: iconHtml,
    className: '',
    iconSize: [28, 34],
    iconAnchor: [14, 32],
    popupAnchor: [0, -32],
  });
}

export default function RealCartographicMap({
  units,
  selectedUnit,
  onSelectUnit,
  selectedRA = 'todas',
  activeLayer: externalActiveLayer,
  onChangeLayer: externalOnChangeLayer,
  userCoords = null,
}: RealCartographicMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapInstanceRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tileLayerRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markersLayerRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markersMapRef = useRef<Map<string, { marker: any; unit: HealthUnitItem }>>(new Map());
  const previousSelectedIdRef = useRef<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const leafletRef = useRef<any>(null);

  const [internalLayer, setInternalLayer] = useState<MapTileLayerType>('osm');
  const activeLayer = externalActiveLayer || internalLayer;

  const [currentZoom, setCurrentZoom] = useState<number>(DF_DEFAULT_ZOOM);
  const [isMapReady, setIsMapReady] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const userMarkerRef = useRef<any>(null);

  // Marcador "você está aqui" (coordenadas ficam só no navegador)
  useEffect(() => {
    const L = leafletRef.current;
    const map = mapInstanceRef.current;
    if (!isMapReady || !L || !map) return;
    if (userMarkerRef.current) {
      userMarkerRef.current.remove();
      userMarkerRef.current = null;
    }
    if (!userCoords) return;
    const insideDF = L.latLngBounds(DF_BOUNDS).contains([userCoords.lat, userCoords.lng]);
    if (!insideDF) return;
    userMarkerRef.current = L.circleMarker([userCoords.lat, userCoords.lng], {
      radius: 9,
      color: '#ffffff',
      weight: 3,
      fillColor: '#2563eb',
      fillOpacity: 1,
    })
      .bindTooltip('Você está aqui', { direction: 'top', offset: [0, -8] })
      .addTo(map);
    map.flyTo([userCoords.lat, userCoords.lng], Math.max(map.getZoom(), 13), { duration: 0.8 });
  }, [isMapReady, userCoords]);

  // 1. Inicialização do Mapa Leaflet
  useEffect(() => {
    let isMounted = true;

    async function initLeaflet() {
      if (!mapContainerRef.current || mapInstanceRef.current) return;

      const L = await import('leaflet');

      if (!isMounted || !mapContainerRef.current) return;
      leafletRef.current = L;

      // Criar instância do mapa
      const map = L.map(mapContainerRef.current, {
        center: DF_DEFAULT_CENTER,
        zoom: DF_DEFAULT_ZOOM,
        minZoom: 10,
        maxZoom: 18,
        maxBounds: DF_BOUNDS,
        maxBoundsViscosity: 1.0,
        zoomControl: false, // Usaremos controles customizados em Liquid Glass
        attributionControl: true,
      });

      // Adicionar camada de tiles inicial
      const initialLayerConfig = TILE_LAYERS[activeLayer];
      const tileLayer = L.tileLayer(initialLayerConfig.url, initialLayerConfig.options).addTo(map);

      // Adicionar grupo de camadas para os marcadores
      const markersLayer = L.layerGroup().addTo(map);

      mapInstanceRef.current = map;
      tileLayerRef.current = tileLayer;
      markersLayerRef.current = markersLayer;

      map.on('zoomend', () => {
        setCurrentZoom(map.getZoom());
      });

      setIsMapReady(true);
    }

    initLeaflet();

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        tileLayerRef.current = null;
        markersLayerRef.current = null;
        markersMapRef.current.clear();
      }
    };
  }, []);

  // 2. Troca de Camadas Cartográficas (OSM / Satélite Esri)
  useEffect(() => {
    let isActive = true;
    if (!mapInstanceRef.current || !isMapReady) return;

    import('leaflet').then((L) => {
      if (!isActive || !mapInstanceRef.current) return;
      const map = mapInstanceRef.current;
      if (!map) return;

      if (tileLayerRef.current) {
        map.removeLayer(tileLayerRef.current);
      }

      const layerConfig = TILE_LAYERS[activeLayer];
      const newTileLayer = L.tileLayer(layerConfig.url, layerConfig.options).addTo(map);
      tileLayerRef.current = newTileLayer;
    });

    return () => {
      isActive = false;
    };
  }, [activeLayer, isMapReady]);

  // 3. Atualização dos Marcadores Médicos no Mapa (Desacoplado de selectedUnit para alta performance)
  useEffect(() => {
    let isActive = true;
    if (!mapInstanceRef.current || !markersLayerRef.current || !isMapReady) return;

    import('leaflet').then((L) => {
      if (!isActive || !mapInstanceRef.current || !markersLayerRef.current) return;
      leafletRef.current = L;
      const markersLayer = markersLayerRef.current;
      const markersMap = markersMapRef.current;

      markersLayer.clearLayers();
      markersMap.clear();

      units.forEach((u) => {
        const isSelected = selectedUnit?.id === u.id;
        const customIcon = createPinIcon(L, u.tipo, isSelected);

        const lat: number = typeof u.lat === 'number' && Number.isFinite(u.lat) ? u.lat : DF_DEFAULT_CENTER[0];
        const lng: number = typeof u.lng === 'number' && Number.isFinite(u.lng) ? u.lng : DF_DEFAULT_CENTER[1];

        const marker = L.marker([lat, lng], {
          icon: customIcon,
          title: u.nome,
          riseOnHover: true,
        });

        // Tooltip suave com Glassmorphism
        marker.bindTooltip(
          `
            <div style="font-weight: 600; font-size: 12px; color: #0f172a;">${u.nome}</div>
            <div style="font-size: 11px; color: #2563eb; margin-top: 2px;">📍 ${u.ra_display} &bull; ${u.tipo_display}</div>
          `,
          {
            direction: 'top',
            offset: [0, -30],
            opacity: 0.96,
            className: 'susana-tooltip-glass',
          }
        );

        marker.on('click', () => {
          onSelectUnit(u);
          if (mapInstanceRef.current) {
            mapInstanceRef.current.flyTo([lat, lng], Math.max(mapInstanceRef.current.getZoom(), 15), {
              duration: 0.8,
            });
          }
        });

        marker.addTo(markersLayer);
        markersMap.set(u.id, { marker, unit: u });
      });

      previousSelectedIdRef.current = selectedUnit?.id || null;
    });

    return () => {
      isActive = false;
    };
  }, [units, isMapReady, onSelectUnit]);

  // 4. Seleção Otimizada em O(1) do Marcador Ativo (Sem reconstrução massiva de DOM)
  useEffect(() => {
    if (!mapInstanceRef.current || !isMapReady) return;
    const L = leafletRef.current;
    if (!L) return;

    const prevId = previousSelectedIdRef.current;
    const currId = selectedUnit?.id || null;

    if (prevId === currId) return;

    // Resetar o marcador anteriormente selecionado
    if (prevId) {
      const prevEntry = markersMapRef.current.get(prevId);
      if (prevEntry) {
        prevEntry.marker.setIcon(createPinIcon(L, prevEntry.unit.tipo, false));
      }
    }

    // Destacar o novo marcador selecionado
    if (currId && selectedUnit) {
      const currEntry = markersMapRef.current.get(currId);
      if (currEntry) {
        currEntry.marker.setIcon(createPinIcon(L, selectedUnit.tipo, true));
        currEntry.marker.openTooltip();
      }

      const lat = typeof selectedUnit.lat === 'number' && Number.isFinite(selectedUnit.lat) ? selectedUnit.lat : null;
      const lng = typeof selectedUnit.lng === 'number' && Number.isFinite(selectedUnit.lng) ? selectedUnit.lng : null;

      if (lat !== null && lng !== null) {
        mapInstanceRef.current.flyTo([lat, lng], Math.max(mapInstanceRef.current.getZoom(), 15), {
          duration: 0.8,
        });
      }
    }

    previousSelectedIdRef.current = currId;
  }, [selectedUnit, isMapReady]);

  // 5. Ajustar Visualização quando RA For Selecionada (Blindado contra unmount race condition)
  useEffect(() => {
    let isActive = true;
    if (!mapInstanceRef.current || !isMapReady || selectedRA === 'todas') return;

    if (units.length > 0) {
      import('leaflet').then((L) => {
        if (!isActive || !mapInstanceRef.current) return;
        const coordinateTuples: [number, number][] = units.map((u) => [
          typeof u.lat === 'number' && Number.isFinite(u.lat) ? u.lat : DF_DEFAULT_CENTER[0],
          typeof u.lng === 'number' && Number.isFinite(u.lng) ? u.lng : DF_DEFAULT_CENTER[1],
        ]);
        const bounds = L.latLngBounds(coordinateTuples);

        if (bounds.isValid() && mapInstanceRef.current) {
          mapInstanceRef.current.fitBounds(bounds, {
            padding: [40, 40],
            maxZoom: 14,
            animate: true,
            duration: 0.8,
          });
        }
      });
    }

    return () => {
      isActive = false;
    };
  }, [selectedRA, units, isMapReady]);

  // Controles de Navegação Customizados
  const handleZoomIn = useCallback(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.zoomIn();
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.zoomOut();
    }
  }, []);

  const handleResetDF = useCallback(() => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo(DF_DEFAULT_CENTER, DF_DEFAULT_ZOOM, {
        duration: 0.9,
      });
      onSelectUnit(null);
    }
  }, [onSelectUnit]);

  const handleSelectLayer = (layer: MapTileLayerType) => {
    if (externalOnChangeLayer) {
      externalOnChangeLayer(layer);
    } else {
      setInternalLayer(layer);
    }
  };

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '560px',
        borderRadius: '20px',
        overflow: 'hidden',
        border: '1px solid var(--b2)',
        background: '#f1f5f9',
        boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)',
      }}
    >
      {/* Contêiner Real do Mapa Leaflet */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }} />

      {/* ------------------------------------------------------------- */}
      {/* CONTROLES FLUTUANTES (LIQUID GLASS)                           */}
      {/* ------------------------------------------------------------- */}

      {/* Controles de Zoom (+ / - / Reset) - Canto Superior Esquerdo */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          zIndex: 400,
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          background: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          padding: '6px',
          borderRadius: '12px',
          border: '1px solid var(--b2)',
          boxShadow: '0 4px 14px rgba(15, 23, 42, 0.1)',
        }}
      >
        <button
          type="button"
          onClick={handleZoomIn}
          disabled={currentZoom >= 18}
          aria-label="Aproximar mapa (+)"
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            background: '#ffffff',
            color: '#0f172a',
            fontSize: '18px',
            fontWeight: 700,
            cursor: currentZoom >= 18 ? 'not-allowed' : 'pointer',
            opacity: currentZoom >= 18 ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.15s ease',
          }}
          title="Aproximar mapa (+)"
        >
          +
        </button>
        <button
          type="button"
          onClick={handleZoomOut}
          disabled={currentZoom <= 10}
          aria-label="Afastar mapa (-)"
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            background: '#ffffff',
            color: '#0f172a',
            fontSize: '18px',
            fontWeight: 700,
            cursor: currentZoom <= 10 ? 'not-allowed' : 'pointer',
            opacity: currentZoom <= 10 ? 0.5 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.15s ease',
          }}
          title="Afastar mapa (-)"
        >
          −
        </button>
        <button
          type="button"
          onClick={handleResetDF}
          aria-label="Redefinir visualização geral do Distrito Federal"
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            background: '#f8fafc',
            color: '#334155',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.15s ease',
          }}
          title="Visão geral do Distrito Federal"
        >
          ↺
        </button>
      </div>

      {/* Alternador de Camadas Cartográficas (Liquid Glass) - Canto Superior Direito */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          zIndex: 400,
          display: 'flex',
          gap: '4px',
          background: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          padding: '4px',
          borderRadius: '12px',
          border: '1px solid var(--b2)',
          boxShadow: '0 4px 14px rgba(15, 23, 42, 0.1)',
        }}
      >
        {(Object.keys(TILE_LAYERS) as MapTileLayerType[]).map((layerKey) => {
          const layerConfig = TILE_LAYERS[layerKey];
          const isSelected = activeLayer === layerKey;
          return (
            <button
              key={layerKey}
              type="button"
              onClick={() => handleSelectLayer(layerKey)}
              aria-pressed={isSelected}
              aria-label={`Visualizar mapa no modo ${layerConfig.name}`}
              style={{
                padding: '6px 10px',
                borderRadius: '8px',
                border: 'none',
                background: isSelected ? 'linear-gradient(135deg, #2563eb, #1d4ed8)' : 'transparent',
                color: isSelected ? '#ffffff' : '#334155',
                fontSize: '11px',
                fontWeight: isSelected ? 600 : 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s ease',
                boxShadow: isSelected ? '0 2px 6px rgba(37,99,235,0.3)' : 'none',
              }}
            >
              <span>{layerConfig.icon}</span>
              <span>{layerConfig.name}</span>
            </button>
          );
        })}
      </div>

      {/* Legenda Cartográfica Semântica - Canto Inferior Esquerdo */}
      <div
        style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          zIndex: 400,
          background: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          padding: '8px 12px',
          borderRadius: '10px',
          border: '1px solid var(--b2)',
          fontSize: '11px',
          color: '#334155',
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '10px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.ubs.bg }} />
          <span>UBS</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.upa.bg }} />
          <span>UPA 24h</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.hospital.bg }} />
          <span>Hospital</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.policlinica.bg }} />
          <span>Policlínica</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.caps.bg }} />
          <span>CAPS</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.farmacia.bg }} />
          <span>Farmácia</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: PIN_COLORS.laboratorio.bg }} />
          <span>Laboratório</span>
        </div>
      </div>
    </div>
  );
}
