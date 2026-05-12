/**
 * Scale transforms for choropleth and bubble maps (inspired by d3-in-angular COVID demo).
 * Maps a raw metric value to a display position t ∈ [0, 1] for color and bubble sizing.
 */

export type CensusScaleId = 'linear' | 'sqrt' | 'log' | 'exp'

/**
 * Choropleth fill easing close to D3’s ``easeCubicInOut`` (see d3-in-angular county demos).
 * Use on SVG ``style`` (not the ``fill`` attribute) so the browser can interpolate colors.
 */
export const CENSUS_CHORO_FILL_TRANSITION =
  'fill 1.2s cubic-bezier(0.65, 0, 0.35, 1), stroke 0.45s cubic-bezier(0.65, 0, 0.35, 1)'

/** Robust choropleth range (reduces “flat” maps when a few outliers dominate min/max). */
export function quantileExtent(
  values: (number | null | undefined)[],
  qLow = 0.04,
  qHigh = 0.96,
): { min: number; max: number } {
  const nums = values
    .filter((x): x is number => typeof x === 'number' && Number.isFinite(x))
    .sort((a, b) => a - b)
  const n = nums.length
  if (n < 2) return { min: 0, max: 1 }
  const lo = nums[Math.max(0, Math.min(n - 1, Math.floor(qLow * (n - 1))))]!
  const hi = nums[Math.max(0, Math.min(n - 1, Math.ceil(qHigh * (n - 1))))]!
  if (!(lo < hi)) {
    const mid = nums[Math.floor(n / 2)]!
    return { min: mid * 0.9, max: mid * 1.1 }
  }
  return { min: lo, max: hi }
}

/** Min/max of observed values (same as ``quantileExtent(..., 0, 1)``). Used for bubble radii so sizes span the full metric range. */
export function minMaxExtent(values: (number | null | undefined)[]): { min: number; max: number } {
  return quantileExtent(values, 0, 1)
}

export const CENSUS_SCALES: { id: CensusScaleId; label: string }[] = [
  { id: 'linear', label: 'Linear' },
  { id: 'sqrt', label: 'Square root' },
  { id: 'log', label: 'Logarithmic' },
  { id: 'exp', label: 'Exponential (t²)' },
]

export function metricToDisplayT(
  v: number | null | undefined,
  min: number,
  max: number,
  scale: CensusScaleId,
): number | null {
  if (v == null || !Number.isFinite(v) || max <= min) return null
  const clamped = Math.max(min, Math.min(max, v))
  const u = (clamped - min) / (max - min)
  switch (scale) {
    case 'linear':
      return u
    case 'sqrt':
      return Math.sqrt(Math.max(0, u))
    case 'log': {
      const lo = Math.log10(Math.max(min, 1))
      const hi = Math.log10(Math.max(max, 1))
      const span = hi - lo || 1e-9
      return (Math.log10(Math.max(clamped, 1)) - lo) / span
    }
    case 'exp':
      return u * u
    default:
      return u
  }
}

/** Multi-stop ramp (light slate → sky → blue → navy) for clearer choropleth steps. */
const CHORO_RGB_STOPS: { t: number; rgb: [number, number, number] }[] = [
  { t: 0, rgb: [241, 245, 249] },
  { t: 0.12, rgb: [224, 231, 255] },
  { t: 0.28, rgb: [191, 219, 254] },
  { t: 0.44, rgb: [125, 211, 252] },
  { t: 0.58, rgb: [56, 189, 248] },
  { t: 0.72, rgb: [59, 130, 246] },
  { t: 0.86, rgb: [29, 78, 216] },
  { t: 1, rgb: [23, 37, 84] },
]

function lerpChannel(a: number, b: number, u: number): number {
  return Math.round(a + (b - a) * u)
}

export function colorFromT(t: number | null): string {
  if (t == null || !Number.isFinite(t)) return '#e2e8f0'
  const x = Math.min(1, Math.max(0, t))
  let i = 0
  while (i < CHORO_RGB_STOPS.length - 2 && x > CHORO_RGB_STOPS[i + 1]!.t) i += 1
  const lo = CHORO_RGB_STOPS[i]!
  const hi = CHORO_RGB_STOPS[i + 1]!
  const span = hi.t - lo.t || 1e-9
  const u = (x - lo.t) / span
  const r = lerpChannel(lo.rgb[0], hi.rgb[0], u)
  const g = lerpChannel(lo.rgb[1], hi.rgb[1], u)
  const b = lerpChannel(lo.rgb[2], hi.rgb[2], u)
  return `rgb(${r},${g},${b})`
}

export function bubbleRadiusPx(
  v: number | null | undefined,
  min: number,
  max: number,
  scale: CensusScaleId,
  rMin = 3,
  rMax = 18,
): number {
  const t = metricToDisplayT(v, min, max, scale)
  if (t == null) return rMin
  return rMin + t * (rMax - rMin)
}
