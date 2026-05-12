/** How choropleth values are derived from ACS estimates. */
export type CensusValueMode = 'raw' | 'yoy' | 'vs_natl'

export type NationalRefEntry = { us?: number | null; pop_weighted_states?: number | null }

export function nationalBaseline(
  nationalRef: Record<string, Record<string, NationalRefEntry>> | undefined,
  vintage: string,
  slug: string,
): number | null {
  const b = nationalRef?.[vintage]?.[slug]
  if (!b) return null
  const w = b.pop_weighted_states
  const u = b.us
  if (typeof w === 'number' && Number.isFinite(w) && w !== 0) return w
  if (typeof u === 'number' && Number.isFinite(u) && u !== 0) return u
  return null
}

export function trendCell(series: unknown, vy: string): number | null {
  if (!series || typeof series !== 'object' || Array.isArray(series)) return null
  const v = (series as Record<string, unknown>)[vy]
  return typeof v === 'number' && Number.isFinite(v) ? v : null
}

export function displayValueForMode(
  mode: CensusValueMode,
  raw: number | null,
  prevRaw: number | null,
  baseline: number | null,
): number | null {
  if (raw == null || !Number.isFinite(raw)) return null
  if (mode === 'raw') return raw
  if (mode === 'vs_natl') {
    if (baseline == null || baseline === 0) return null
    return ((raw / baseline) - 1) * 100
  }
  if (mode === 'yoy') {
    if (prevRaw == null || !Number.isFinite(prevRaw) || prevRaw === 0) return null
    return ((raw - prevRaw) / prevRaw) * 100
  }
  return raw
}

export function prevVintageInList(vintages: string[], current: string): string | null {
  const i = vintages.indexOf(current)
  return i > 0 ? vintages[i - 1]! : null
}
