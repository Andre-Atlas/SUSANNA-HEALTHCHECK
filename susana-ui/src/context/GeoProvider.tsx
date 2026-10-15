'use client';

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { Coords } from '@/lib/geo';

// Localização atual: fica só neste aparelho (memória + sessionStorage) e nunca é enviada à API.
type GeoStatus = 'idle' | 'prompt' | 'granted' | 'denied' | 'unavailable';

interface GeoContextValue {
  status: GeoStatus;
  coords: Coords | null;
  request: () => Promise<Coords | null>;
  forget: () => void;
}

const CONSENT_KEY = 'susana_geo_ok';
const COORDS_KEY = 'susana_geo_coords';
const GeoContext = createContext<GeoContextValue | null>(null);

function read(store: 'local' | 'session', key: string): string | null {
  try {
    return (store === 'local' ? localStorage : sessionStorage).getItem(key);
  } catch {
    return null;
  }
}

function write(store: 'local' | 'session', key: string, value: string | null) {
  try {
    const s = store === 'local' ? localStorage : sessionStorage;
    if (value === null) s.removeItem(key);
    else s.setItem(key, value);
  } catch {
    /* armazenamento indisponível */
  }
}

export function GeoProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<GeoStatus>('idle');
  const [coords, setCoords] = useState<Coords | null>(null);

  const locate = useCallback(
    () =>
      new Promise<Coords | null>((resolve) => {
        if (typeof navigator === 'undefined' || !navigator.geolocation) {
          setStatus('unavailable');
          resolve(null);
          return;
        }
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const c = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            setCoords(c);
            setStatus('granted');
            write('local', CONSENT_KEY, '1');
            write('session', COORDS_KEY, JSON.stringify(c));
            resolve(c);
          },
          (err) => {
            setStatus(err.code === err.PERMISSION_DENIED ? 'denied' : 'unavailable');
            if (err.code === err.PERMISSION_DENIED) write('local', CONSENT_KEY, null);
            resolve(null);
          },
          { enableHighAccuracy: false, maximumAge: 10 * 60 * 1000, timeout: 10000 },
        );
      }),
    [],
  );

  // Retoma a localização apenas se o usuário já consentiu antes neste aparelho
  useEffect(() => {
    const cached = read('session', COORDS_KEY);
    if (cached) {
      try {
        // Leitura do sessionStorage só é possível no cliente
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setCoords(JSON.parse(cached));
        setStatus('granted');
        return;
      } catch {
        /* ignora */
      }
    }
    if (read('local', CONSENT_KEY) === '1') locate();
    else if (typeof navigator !== 'undefined' && !navigator.geolocation) setStatus('unavailable');
    else setStatus('prompt');
  }, [locate]);

  const forget = useCallback(() => {
    write('local', CONSENT_KEY, null);
    write('session', COORDS_KEY, null);
    setCoords(null);
    setStatus('prompt');
  }, []);

  const value = useMemo(() => ({ status, coords, request: locate, forget }), [status, coords, locate, forget]);
  return <GeoContext.Provider value={value}>{children}</GeoContext.Provider>;
}

export function useGeo(): GeoContextValue {
  const ctx = useContext(GeoContext);
  if (!ctx) throw new Error('useGeo deve ser usado dentro de <GeoProvider>');
  return ctx;
}
