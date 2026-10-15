// Cálculos geográficos locais: as coordenadas do usuário nunca saem do navegador.

export interface Coords {
  lat: number;
  lng: number;
}

export function haversineKm(a: Coords, b: Coords): number {
  const R = 6371;
  const toRad = (x: number) => (x * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

export function formatKm(km: number): string {
  return km < 1 ? `${Math.round(km * 1000)} m` : `${km.toFixed(1).replace('.', ',')} km`;
}

interface Located {
  lat?: number;
  lng?: number;
}

export function sortByDistance<T extends Located>(items: T[], origin: Coords | null): T[] {
  if (!origin) return items;
  const dist = (u: T) => (u.lat != null && u.lng != null ? haversineKm(origin, { lat: u.lat, lng: u.lng }) : Infinity);
  return [...items].sort((a, b) => dist(a) - dist(b));
}

/** RA da unidade mais próxima — usada só como sugestão que o usuário confirma. */
export function suggestRA<T extends Located & { ra: string }>(items: T[], origin: Coords | null): string | null {
  const nearest = sortByDistance(items, origin)[0];
  if (!nearest || nearest.lat == null || nearest.lng == null || !origin) return null;
  return haversineKm(origin, { lat: nearest.lat, lng: nearest.lng }) < 15 ? nearest.ra : null;
}
