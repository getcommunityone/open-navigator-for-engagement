// @ts-nocheck — react-simple-maps ships without TypeScript types (same as USMap.tsx)
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, Navigate, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ComposableMap, Geographies, Geography } from 'react-simple-maps'
import { geoCentroid } from 'd3-geo'
import { feature } from 'topojson-client'
import { MapContainer, GeoJSON, useMap, CircleMarker, Tooltip as LeafletTooltip } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  ArrowLeftIcon,
  TableCellsIcon,
  ChartBarSquareIcon,
  SwatchIcon,
  PlayIcon,
  PauseIcon,
} from '@heroicons/react/24/outline'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
  Line,
  LineChart,
} from 'recharts'
import { STATE_CODE_TO_NAME } from '../utils/stateMapping'
import {
  CENSUS_CHORO_FILL_TRANSITION,
  CENSUS_SCALES,
  bubbleRadiusPx,
  colorFromT,
  metricToDisplayT,
  minMaxExtent,
  quantileExtent,
  type CensusScaleId,
} from '../utils/censusMapTransforms'
import {
  type CensusValueMode,
  displayValueForMode,
  nationalBaseline,
  prevVintageInList,
  trendCell,
} from '../utils/censusMapValueMode'

const STATES_TOPO = 'https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json'
const COUNTY_TOPO = 'https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json'

/** Lon/lat pair for geography centroids. */
function toLonLatPair(c: unknown): [number, number] | null {
  if (!Array.isArray(c) || c.length < 2) return null
  const lon = Number(c[0])
  const lat = Number(c[1])
  if (!Number.isFinite(lon) || !Number.isFinite(lat)) return null
  return [lon, lat]
}

/** Project [lon,lat] to SVG; geoAlbersUsa may return null / non-array — never feed that to r-s-m Marker. */
function safeProjectScreen(
  projection: ((c: [number, number]) => unknown) | null | undefined,
  lonLat: [number, number],
): [number, number] | null {
  if (projection == null || typeof projection !== 'function') return null
  try {
    const p = projection(lonLat)
    if (!Array.isArray(p) || p.length < 2) return null
    const x = Number(p[0])
    const y = Number(p[1])
    if (!Number.isFinite(x) || !Number.isFinite(y)) return null
    return [x, y]
  } catch {
    return null
  }
}

const FIPS2_TO_USPS: Record<string, string> = {
  '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE',
  '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA',
  '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN',
  '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM',
  '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
  '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA',
  '54': 'WV', '55': 'WI', '56': 'WY', '72': 'PR',
}

/** Topo / Census ids may be 1 or "01"; normalize to 2-digit state FIPS for routes and JSON keys. */
function normalizeStateFips(raw: unknown): string | null {
  const s = String(raw ?? '').trim()
  if (!s) return null
  const n = Number.parseInt(s, 10)
  if (!Number.isFinite(n) || n < 1 || n > 99) return null
  return String(n).padStart(2, '0')
}

interface CensusMetric {
  slug: string
  label: string
  format: string
}

interface CensusManifest {
  vintage: string
  vintages?: string[]
  county_topo_cdn: string
  state_topo_cdn?: string
  metrics: CensusMetric[]
  place_states: string[]
  national_ref?: Record<string, Record<string, { us?: number | null; pop_weighted_states?: number | null }>>
  paths: {
    county_metrics: string
    place_geojson: string
    state_metrics?: string
    state_trends?: string
    county_trends?: string
    place_trends?: string
  }
}

interface StateMetricsPayload {
  geography: string
  vintage: string
  values: Record<string, Record<string, number | null | undefined>>
}

interface CountyMetricsPayload {
  geography: string
  vintage: string
  values: Record<string, Record<string, number | null | undefined>>
}

/** Multi-year state series from ``state_trends.json`` */
interface StateTrendsPayload {
  geography: string
  vintages: string[]
  by_state: Record<string, Record<string, unknown>>
}

interface CountyPlaceTrendsPayload {
  geography: string
  state: string
  vintages: string[]
  byGeoid: Record<string, Record<string, unknown>>
}

type GeoJSONFeatureCollection = GeoJSON.FeatureCollection

function stateMetricsFromTrends(
  trends: StateTrendsPayload,
  vintage: string,
  metricSlugs: string[],
): StateMetricsPayload {
  const values: Record<string, Record<string, number | null | undefined>> = {}
  for (const [st, row] of Object.entries(trends.by_state)) {
    const cell: Record<string, number | null | undefined> = {}
    const nm = row.NAME
    if (typeof nm === 'string' && nm.trim()) cell.NAME = nm.trim()
    for (const slug of metricSlugs) {
      const series = row[slug]
      if (series && typeof series === 'object' && !Array.isArray(series)) {
        const v = (series as Record<string, unknown>)[vintage]
        cell[slug] = typeof v === 'number' && Number.isFinite(v) ? v : null
      } else {
        cell[slug] = null
      }
    }
    values[st] = cell
  }
  return { geography: 'state', vintage, values }
}

function countyMetricsFromTrends(
  trends: CountyPlaceTrendsPayload,
  vintage: string,
  metricSlugs: string[],
  stateFips: string,
): CountyMetricsPayload {
  const values: Record<string, Record<string, number | null | undefined>> = {}
  const stp = stateFips.padStart(2, '0')
  for (const [gid, row] of Object.entries(trends.byGeoid)) {
    if (!gid.startsWith(stp)) continue
    const cell: Record<string, number | null | undefined> = {}
    const nm = row.NAME
    if (typeof nm === 'string' && nm.trim()) cell.NAME = nm.trim()
    cell.GEOID = gid
    for (const slug of metricSlugs) {
      const series = row[slug]
      if (series && typeof series === 'object' && !Array.isArray(series)) {
        const v = (series as Record<string, unknown>)[vintage]
        cell[slug] = typeof v === 'number' && Number.isFinite(v) ? v : null
      } else {
        cell[slug] = null
      }
    }
    const g5 = gid.replace(/\D/g, '').slice(-5).padStart(5, '0')
    values[g5] = cell
  }
  return { geography: 'county', vintage, values }
}

function mergePlaceGeoWithTrends(
  base: GeoJSONFeatureCollection | undefined,
  trends: CountyPlaceTrendsPayload | undefined,
  vintage: string,
  metricSlugs: string[],
): GeoJSONFeatureCollection | undefined {
  if (!base) return undefined
  if (!trends?.byGeoid) return base
  return {
    ...base,
    features: base.features.map((f) => {
      const p = (f.properties ?? {}) as Record<string, unknown>
      const gid = String(p.GEOID ?? '')
      const row = trends.byGeoid[gid]
      if (!row) return f
      const np: Record<string, unknown> = { ...p }
      for (const slug of metricSlugs) {
        const series = row[slug]
        if (series && typeof series === 'object' && !Array.isArray(series)) {
          const v = (series as Record<string, unknown>)[vintage]
          if (typeof v === 'number' && Number.isFinite(v)) np[slug] = v
        }
      }
      return { ...f, properties: np }
    }),
  }
}

function trendPointsFromSeries(
  vintages: string[],
  series: Record<string, unknown> | undefined,
): { year: string; value: number | null }[] {
  if (!series || typeof series !== 'object' || Array.isArray(series)) return []
  return vintages.map((y) => {
    const v = (series as Record<string, unknown>)[y]
    return { year: y, value: typeof v === 'number' && Number.isFinite(v) ? v : null }
  })
}

function VintageAndPlayControls({
  vintages,
  displayVintage,
  singleVintage,
  showPlay,
  playing,
  setPlaying,
  onVintageChange,
}: {
  vintages: string[]
  displayVintage: string
  singleVintage: boolean
  showPlay: boolean
  playing: boolean
  setPlaying: (v: boolean) => void
  onVintageChange: (v: string) => void
}) {
  const vintageIndex = Math.max(0, vintages.indexOf(displayVintage))
  return (
    <>
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold uppercase text-slate-500">Vintage</span>
        <input
          type="range"
          min={0}
          max={Math.max(0, vintages.length - 1)}
          step={1}
          value={vintageIndex}
          disabled={singleVintage}
          onChange={(e) => {
            setPlaying(false)
            onVintageChange(vintages[Number(e.target.value)]!)
          }}
          className="w-36 accent-[#354F52] disabled:opacity-40"
        />
        <span className="text-sm font-mono text-slate-800 tabular-nums min-w-[44px]">{displayVintage}</span>
      </div>
      {showPlay ? (
        <button
          type="button"
          onClick={() => setPlaying(!playing)}
          className="inline-flex items-center gap-1 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
          title={playing ? 'Pause animation' : 'Play through ACS vintages'}
        >
          {playing ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
          {playing ? 'Pause' : 'Play'}
        </button>
      ) : null}
    </>
  )
}

function AcTrendChart({
  title,
  points,
  format,
}: {
  title: string
  points: { year: string; value: number | null }[]
  format: (v: number) => string
}) {
  const nonNull = points.filter((p) => p.value != null)
  if (nonNull.length < 2) {
    return (
      <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50/80 p-3 text-xs text-slate-500">
        {title} — need at least two vintages with data for a trend line.
      </div>
    )
  }
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-600 mb-2">{title}</div>
      <div className="h-[160px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200" />
            <XAxis dataKey="year" tick={{ fontSize: 9 }} interval="preserveStartEnd" />
            <YAxis
              width={44}
              tick={{ fontSize: 9 }}
              tickFormatter={(x) => {
                const n = Number(x)
                if (!Number.isFinite(n)) return ''
                if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
                if (Math.abs(n) >= 1000) return `${Math.round(n / 1000)}k`
                return String(Math.round(n))
              }}
            />
            <RechartsTooltip
              formatter={(value: number) => [format(value), '']}
              labelFormatter={(y) => `ACS ${y}`}
            />
            <Line type="monotone" dataKey="value" stroke="#52796F" strokeWidth={2} dot={{ r: 3 }} connectNulls />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function countyGeoidFromFeature(f: GeoJSON.Feature): string {
  const id = f.id
  if (typeof id === 'number' && Number.isFinite(id)) return String(Math.trunc(id)).padStart(5, '0')
  if (typeof id === 'string' && /^\d+$/.test(id)) return id.padStart(5, '0')
  const p = f.properties as Record<string, unknown> | null
  const raw = p?.GEOID ?? p?.GEO_ID ?? p?.geoid
  if (raw == null) return ''
  const digits = String(raw).replace(/\D/g, '')
  if (!digits) return ''
  return digits.length <= 5 ? digits.padStart(5, '0') : digits.slice(-5).padStart(5, '0')
}

function buildStateCountyGeoJson(
  topology: { objects: { counties: unknown } },
  values: Record<string, Record<string, unknown>>,
  stateFips: string,
  metricSlug: string,
): GeoJSONFeatureCollection | null {
  try {
    const fc = feature(topology as never, topology.objects.counties as never) as GeoJSON.FeatureCollection
    const features: GeoJSON.Feature[] = []
    for (const f of fc.features) {
      const gid = countyGeoidFromFeature(f)
      if (gid.length !== 5 || !gid.startsWith(stateFips)) continue
      const row = values[gid] ?? {}
      const base = (f.properties as Record<string, unknown> | undefined) ?? {}
      const name = typeof row.NAME === 'string' ? row.NAME : typeof base.name === 'string' ? base.name : gid
      const props: Record<string, unknown> = {
        ...base,
        GEOID: gid,
        NAME: name,
        ...row,
        [metricSlug]: row[metricSlug],
      }
      features.push({ ...f, properties: props, id: gid })
    }
    if (!features.length) return null
    return { type: 'FeatureCollection', features }
  } catch {
    return null
  }
}

function censusNull(v: unknown): v is number {
  return typeof v === 'number' && Number.isFinite(v)
}

function formatMetricValue(
  slug: string,
  v: number | null | undefined,
  metrics: CensusMetric[],
  valueMode: CensusValueMode = 'raw',
): string {
  if (v == null || !Number.isFinite(v)) return '—'
  if (valueMode === 'yoy' || valueMode === 'vs_natl') return `${v.toFixed(1)}%`
  const m = metrics.find((x) => x.slug === slug)
  if (m?.format === 'currency') return `$${Math.round(v).toLocaleString()}`
  if (m?.format === 'count') return `${Math.round(v).toLocaleString()}`
  if (m?.format === 'percent') return `${v.toFixed(1)}%`
  if (m?.format === 'ratio') return v.toFixed(3)
  if (m?.format === 'years') return `${v.toFixed(1)} yrs`
  return String(v)
}

/** Animated camera when drilling into county / place GeoJSON (Leaflet ``flyToBounds``). */
function FlyToDataBounds({ data }: { data: GeoJSONFeatureCollection }) {
  const map = useMap()
  useEffect(() => {
    if (!data?.features?.length) return
    const layer = L.geoJSON(data as never)
    const b = layer.getBounds()
    if (!b.isValid()) return
    map.flyToBounds(b, {
      padding: [28, 28],
      maxZoom: 11,
      duration: 1.35,
      easeLinearity: 0.28,
    })
  }, [map, data])
  return null
}

function featureLatLng(feature: GeoJSON.Feature): { lat: number; lng: number } | null {
  try {
    const layer = L.geoJSON(feature as never)
    const c = layer.getBounds().getCenter()
    if (c && Number.isFinite(c.lat) && Number.isFinite(c.lng)) return { lat: c.lat, lng: c.lng }
  } catch {
    /* ignore */
  }
  return null
}

const CHORO_LEGEND_GRADIENT_STOPS = 17

function ChoroplethLegend({
  min,
  max,
  scale,
  format,
  valueMode = 'raw',
}: {
  min: number
  max: number
  scale: CensusScaleId
  format: (v: number) => string
  valueMode?: CensusValueMode
}) {
  const n = CHORO_LEGEND_GRADIENT_STOPS
  const stops = Array.from({ length: n }, (_, i) => {
    const u = n <= 1 ? 0 : i / (n - 1)
    const v = min + u * (max - min)
    const t = metricToDisplayT(v, min, max, scale) ?? 0
    return { offset: `${u * 100}%`, color: colorFromT(t), value: v }
  })
  const tickUs = [0, 0.25, 0.5, 0.75, 1] as const
  const gradId = `census-ramp-${scale}-${Math.round(min)}-${Math.round(max)}`
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600 mb-2">
        <SwatchIcon className="h-4 w-4" />
        Color scale (filled map)
      </div>
      <svg width="100%" height="52" viewBox="0 0 260 52" preserveAspectRatio="xMidYMid meet" className="max-w-full">
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
            {stops.map((s, i) => (
              <stop key={i} offset={s.offset} stopColor={s.color} />
            ))}
          </linearGradient>
        </defs>
        <rect x="8" y="8" width="244" height="14" rx="3" fill={`url(#${gradId})`} stroke="#94a3b8" strokeWidth="0.5" />
        {tickUs.map((frac) => (
          <text key={frac} x={8 + frac * 244} y="44" fontSize="9" fill="#475569" textAnchor="middle">
            {format(min + frac * (max - min))}
          </text>
        ))}
      </svg>
      <p className="text-[10px] text-slate-500 mt-1 leading-snug">
        Stops are evenly spaced in <strong>mapped</strong> value range; shading follows the selected transform (
        {CENSUS_SCALES.find((x) => x.id === scale)?.label ?? scale}).{' '}
        {valueMode === 'raw'
          ? 'Extremes use percentile clipping so outliers do not wash out the map.'
          : valueMode === 'yoy'
            ? 'Legend shows percent change vs the prior vintage in the manifest list.'
            : 'Legend shows percent difference from the national benchmark (population-weighted state composite when available).'}
      </p>
    </div>
  )
}

function BubbleLegend({
  min,
  max,
  scale,
  format,
}: {
  min: number
  max: number
  scale: CensusScaleId
  format: (v: number) => string
}) {
  const refs = [0.15, 0.5, 0.88].map((u) => min + u * (max - min))
  const items = refs.map((v) => ({
    v,
    r: bubbleRadiusPx(v, min, max, scale, 4, 22),
    label: format(v),
  }))
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-600 mb-3">Bubble size scale</div>
      <div className="flex items-end justify-around gap-2 px-2" style={{ height: 56 }}>
        {items.map((it, i) => (
          <div key={i} className="flex flex-col items-center gap-1">
            <div
              className="rounded-full bg-rose-500/85 border border-white shadow"
              style={{ width: it.r * 2, height: it.r * 2 }}
            />
            <span className="text-[10px] text-slate-600 text-center max-w-[72px] leading-tight">{it.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

/** When manifest lists 2+ vintages, advance years even if ``*_trends_*.json`` is missing (per-vintage metrics still load). */
const PLAY_INTERVAL_MS = 1950

function CensusMapPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams, setSearchParams] = useSearchParams()
  const { vintage, metric, stateFips: stateFipsRaw } = useParams<{
    vintage?: string
    metric?: string
    stateFips?: string
  }>()
  const stateFips = stateFipsRaw
    ? normalizeStateFips(stateFipsRaw) ?? (stateFipsRaw.length <= 2 ? stateFipsRaw.padStart(2, '0') : stateFipsRaw)
    : undefined

  const mode = useMemo(() => {
    if (location.pathname.includes('/census-map/place/')) return 'place'
    if (location.pathname.includes('/census-map/state/')) return 'stateCounty'
    return 'us'
  }, [location.pathname])

  const viz: 'filled' | 'bubble' = searchParams.get('viz') === 'bubble' ? 'bubble' : 'filled'
  const scaleRaw = searchParams.get('scale') || 'linear'
  const scale: CensusScaleId = (['linear', 'sqrt', 'log', 'exp'].includes(scaleRaw) ? scaleRaw : 'linear') as CensusScaleId

  const setViz = (v: 'filled' | 'bubble') => {
    const next = new URLSearchParams(searchParams)
    if (v === 'filled') next.delete('viz')
    else next.set('viz', 'bubble')
    setSearchParams(next, { replace: true })
  }

  const setScale = (s: CensusScaleId) => {
    const next = new URLSearchParams(searchParams)
    if (s === 'linear') next.delete('scale')
    else next.set('scale', s)
    setSearchParams(next, { replace: true })
  }

  const valueModeRaw = searchParams.get('valueMode') || 'raw'
  const valueMode: CensusValueMode = (
    ['raw', 'yoy', 'vs_natl'].includes(valueModeRaw) ? valueModeRaw : 'raw'
  ) as CensusValueMode

  const setValueMode = (m: CensusValueMode) => {
    const next = new URLSearchParams(searchParams)
    if (m === 'raw') next.delete('valueMode')
    else next.set('valueMode', m)
    setSearchParams(next, { replace: true })
  }

  const { data: manifest, isError: manifestError } = useQuery({
    queryKey: ['census-map-manifest'],
    queryFn: async (): Promise<CensusManifest> => {
      const r = await fetch('/data/census-map/manifest.json')
      if (!r.ok) throw new Error('manifest')
      return r.json()
    },
  })

  const effectiveVintage = vintage ?? manifest?.vintage ?? '2022'
  const metricSlug = metric ?? 'median_household_income'
  const vintages = useMemo(
    () => manifest?.vintages ?? (manifest?.vintage ? [manifest.vintage] : ['2022']),
    [manifest?.vintage, manifest?.vintages?.join(',')],
  )
  const multiYear = (manifest?.vintages?.length ?? 0) > 1
  const metricSlugsList = useMemo(() => (manifest?.metrics ?? []).map((m) => m.slug), [manifest?.metrics])

  const { data: stateTrends } = useQuery({
    queryKey: ['census-state-trends'],
    queryFn: async (): Promise<StateTrendsPayload | null> => {
      const r = await fetch('/data/census-map/state_trends.json')
      if (r.status === 404) return null
      if (!r.ok) throw new Error('state trends')
      return r.json() as StateTrendsPayload
    },
    enabled: !!manifest && multiYear,
    retry: false,
  })

  const { data: countyTrends } = useQuery({
    queryKey: ['census-county-trends', stateFips],
    queryFn: async (): Promise<CountyPlaceTrendsPayload | null> => {
      const r = await fetch(`/data/census-map/county_trends_${stateFips}.json`)
      if (r.status === 404) return null
      if (!r.ok) throw new Error('county trends')
      return r.json() as CountyPlaceTrendsPayload
    },
    enabled: !!manifest && multiYear && mode === 'stateCounty' && !!stateFips,
    retry: false,
  })

  const { data: placeTrends } = useQuery({
    queryKey: ['census-place-trends', stateFips],
    queryFn: async (): Promise<CountyPlaceTrendsPayload | null> => {
      const r = await fetch(`/data/census-map/place_trends_${stateFips}.json`)
      if (r.status === 404) return null
      if (!r.ok) throw new Error('place trends')
      return r.json() as CountyPlaceTrendsPayload
    },
    enabled: !!manifest && multiYear && mode === 'place' && !!stateFips,
    retry: false,
  })

  const [playing, setPlaying] = useState(false)
  const [animIndex, setAnimIndex] = useState(0)
  const vintagesRef = useRef(vintages)
  vintagesRef.current = vintages

  useEffect(() => {
    const ix = vintages.indexOf(effectiveVintage)
    setAnimIndex(ix >= 0 ? ix : 0)
  }, [effectiveVintage, vintages.join(',')])

  const canPlayMultiVintage =
    multiYear &&
    vintages.length > 1 &&
    (mode === 'us' || (mode === 'stateCounty' && !!stateFips) || (mode === 'place' && !!stateFips))

  const canTrendAnimate = canPlayMultiVintage

  const displayVintage =
    playing && canTrendAnimate ? vintages[animIndex % vintages.length]! : effectiveVintage

  useEffect(() => {
    if (!playing || !canTrendAnimate) return
    const t = window.setInterval(() => {
      setAnimIndex((i) => {
        const list = vintagesRef.current
        if (!list.length) return 0
        return (i + 1) % list.length
      })
    }, PLAY_INTERVAL_MS)
    return () => window.clearInterval(t)
  }, [playing, canTrendAnimate])

  useEffect(() => {
    setPlaying(false)
  }, [effectiveVintage, mode, metricSlug, valueMode])

  useEffect(() => {
    if (valueMode !== 'raw' && viz === 'bubble') {
      const next = new URLSearchParams(searchParams)
      next.delete('viz')
      setSearchParams(next, { replace: true })
    }
  }, [valueMode, viz, searchParams, setSearchParams])

  const showPlay = canTrendAnimate

  const { data: statePayloadRaw } = useQuery({
    queryKey: ['census-state-metrics', displayVintage],
    queryFn: async (): Promise<StateMetricsPayload> => {
      const r = await fetch(`/data/census-map/${displayVintage}/state_metrics.json`)
      if (!r.ok) throw new Error('state metrics')
      return r.json()
    },
    enabled: mode === 'us' && !!displayVintage && !stateTrends,
    retry: false,
  })

  const statePayload = useMemo(() => {
    if (mode === 'us' && stateTrends && displayVintage) {
      return stateMetricsFromTrends(stateTrends, displayVintage, metricSlugsList)
    }
    return statePayloadRaw
  }, [mode, stateTrends, statePayloadRaw, displayVintage, metricSlugsList])

  const { data: countyPayloadRaw, isError: countyPayloadError, isPending: countyPayloadLoading } = useQuery({
    queryKey: ['census-county-metrics', displayVintage],
    queryFn: async (): Promise<CountyMetricsPayload> => {
      const r = await fetch(`/data/census-map/${displayVintage}/county_metrics.json`)
      if (!r.ok) throw new Error('county metrics')
      return r.json()
    },
    enabled: mode === 'stateCounty' && !!displayVintage && !countyTrends,
    retry: false,
  })

  const countyPayload = useMemo(() => {
    if (mode === 'stateCounty' && countyTrends && stateFips && displayVintage) {
      return countyMetricsFromTrends(countyTrends, displayVintage, metricSlugsList, stateFips)
    }
    return countyPayloadRaw
  }, [mode, countyTrends, countyPayloadRaw, displayVintage, metricSlugsList, stateFips])

  const { data: countyTopo, isPending: countyTopoLoading } = useQuery({
    queryKey: ['census-county-topo', manifest?.county_topo_cdn],
    queryFn: async () => {
      const u = manifest!.county_topo_cdn || COUNTY_TOPO
      const r = await fetch(u)
      if (!r.ok) throw new Error('county topo')
      return r.json()
    },
    enabled: mode === 'stateCounty' && !!manifest,
    staleTime: Infinity,
  })

  const placeUrl =
    mode === 'place' && stateFips
      ? `/data/census-map/${displayVintage}/place_${stateFips}.geojson`
      : null

  const { data: placeGeo, isError: placeGeoError } = useQuery({
    queryKey: ['census-place-geo', placeUrl],
    queryFn: async (): Promise<GeoJSONFeatureCollection> => {
      const r = await fetch(placeUrl!)
      if (!r.ok) throw new Error('place geojson')
      return r.json()
    },
    enabled: mode === 'place' && !!placeUrl,
  })

  const placeGeoMerged = useMemo(
    () => mergePlaceGeoWithTrends(placeGeo, placeTrends ?? undefined, displayVintage, metricSlugsList),
    [placeGeo, placeTrends, displayVintage, metricSlugsList],
  )

  const metrics = manifest?.metrics ?? []
  const placeStates = manifest?.place_states ?? []

  const [hoverRegion, setHoverRegion] = useState<{
    id: string
    name: string
    value: number | null
  } | null>(null)

  const [countyHover, setCountyHover] = useState<{ id: string; name: string; value: number | null } | null>(null)

  const [placeHover, setPlaceHover] = useState<{ id: string; name: string; value: number | null } | null>(null)

  const [tableSort, setTableSort] = useState<{ key: 'name' | 'value' | 'geoid'; dir: 'asc' | 'desc' }>({
    key: 'value',
    dir: 'desc',
  })

  const stateDisplayById = useMemo(() => {
    const out: Record<string, number | null> = {}
    if (!statePayload || !metricSlug) return out
    const prevV = prevVintageInList(vintages, displayVintage)
    const nat = nationalBaseline(manifest?.national_ref, displayVintage, metricSlug)
    for (const [sid, row] of Object.entries(statePayload.values)) {
      const raw = typeof row[metricSlug] === 'number' && Number.isFinite(row[metricSlug]) ? row[metricSlug] : null
      let prev: number | null = null
      if (valueMode === 'yoy' && prevV && stateTrends?.by_state?.[sid]) {
        prev = trendCell((stateTrends.by_state[sid] as Record<string, unknown>)[metricSlug], prevV)
      }
      out[sid] = displayValueForMode(valueMode, raw, prev, nat)
    }
    return out
  }, [
    statePayload,
    metricSlug,
    valueMode,
    displayVintage,
    vintages.join(','),
    stateTrends,
    manifest?.national_ref,
  ])

  const stateChoroExtent = useMemo(() => {
    const vals = Object.values(stateDisplayById).filter(
      (x): x is number => typeof x === 'number' && Number.isFinite(x),
    )
    if (!vals.length) return { min: 0, max: 1 }
    return quantileExtent(vals)
  }, [stateDisplayById])

  const stateBubbleExtent = useMemo(() => {
    if (!statePayload || !metricSlug) return { min: 0, max: 1 }
    const vals = Object.values(statePayload.values)
      .map((row) => row[metricSlug])
      .filter((x): x is number => typeof x === 'number' && Number.isFinite(x))
    if (!vals.length) return { min: 0, max: 1 }
    return minMaxExtent(vals)
  }, [statePayload, metricSlug])

  const placeDisplayByGeoid = useMemo(() => {
    const out: Record<string, number | null> = {}
    const g = placeGeoMerged
    if (!g || !metricSlug) return out
    const prevV = prevVintageInList(vintages, displayVintage)
    const nat = nationalBaseline(manifest?.national_ref, displayVintage, metricSlug)
    for (const f of g.features) {
      const p = f.properties as Record<string, unknown> | null
      const raw = typeof p?.[metricSlug] === 'number' && Number.isFinite(p[metricSlug]) ? p[metricSlug] : null
      const rawG = String(p?.GEOID ?? '').replace(/\D/g, '')
      const gid7 = rawG.length <= 7 ? rawG.padStart(7, '0') : rawG.slice(-7).padStart(7, '0')
      let prev: number | null = null
      if (valueMode === 'yoy' && prevV && placeTrends?.byGeoid?.[gid7]) {
        prev = trendCell((placeTrends.byGeoid[gid7] as Record<string, unknown>)[metricSlug], prevV)
      }
      out[gid7] = displayValueForMode(valueMode, raw, prev, nat)
    }
    return out
  }, [
    placeGeoMerged,
    metricSlug,
    valueMode,
    displayVintage,
    vintages.join(','),
    placeTrends,
    manifest?.national_ref,
  ])

  const placeChoroExtent = useMemo(() => {
    const vals = Object.values(placeDisplayByGeoid).filter(
      (x): x is number => typeof x === 'number' && Number.isFinite(x),
    )
    if (!vals.length) return { min: 0, max: 1 }
    return quantileExtent(vals)
  }, [placeDisplayByGeoid])

  const placeBubbleExtent = useMemo(() => {
    const g = placeGeoMerged
    if (!g || !metricSlug) return { min: 0, max: 1 }
    const vals = g.features
      .map((f) => {
        const v = (f.properties as Record<string, unknown> | null)?.[metricSlug]
        return typeof v === 'number' && Number.isFinite(v) ? v : null
      })
      .filter((x): x is number => x != null)
    if (!vals.length) return { min: 0, max: 1 }
    return minMaxExtent(vals)
  }, [placeGeoMerged, metricSlug])

  const stateCountyGeo = useMemo(() => {
    if (mode !== 'stateCounty' || !stateFips || !countyTopo || !countyPayload?.values) return null
    return buildStateCountyGeoJson(countyTopo, countyPayload.values, stateFips, metricSlug)
  }, [mode, stateFips, countyTopo, countyPayload, metricSlug])

  const countyDisplayByGeoid = useMemo(() => {
    const out: Record<string, number | null> = {}
    if (!stateCountyGeo || !metricSlug) return out
    const prevV = prevVintageInList(vintages, displayVintage)
    const nat = nationalBaseline(manifest?.national_ref, displayVintage, metricSlug)
    for (const f of stateCountyGeo.features) {
      const p = f.properties as Record<string, unknown> | null
      const gid = countyGeoidFromFeature(f as GeoJSON.Feature)
      const raw = typeof p?.[metricSlug] === 'number' && Number.isFinite(p[metricSlug]) ? p[metricSlug] : null
      let prev: number | null = null
      if (valueMode === 'yoy' && prevV && countyTrends?.byGeoid?.[gid]) {
        prev = trendCell((countyTrends.byGeoid[gid] as Record<string, unknown>)[metricSlug], prevV)
      }
      out[gid] = displayValueForMode(valueMode, raw, prev, nat)
    }
    return out
  }, [
    stateCountyGeo,
    metricSlug,
    valueMode,
    displayVintage,
    vintages.join(','),
    countyTrends,
    manifest?.national_ref,
  ])

  const countyChoroExtent = useMemo(() => {
    const vals = Object.values(countyDisplayByGeoid).filter(
      (x): x is number => typeof x === 'number' && Number.isFinite(x),
    )
    if (!vals.length) return { min: 0, max: 1 }
    return quantileExtent(vals)
  }, [countyDisplayByGeoid])

  const countyBubbleExtent = useMemo(() => {
    if (!stateCountyGeo || !metricSlug) return { min: 0, max: 1 }
    const vals = stateCountyGeo.features
      .map((f) => {
        const v = (f.properties as Record<string, unknown> | null)?.[metricSlug]
        return typeof v === 'number' && Number.isFinite(v) ? v : null
      })
      .filter((x): x is number => x != null)
    if (!vals.length) return { min: 0, max: 1 }
    return minMaxExtent(vals)
  }, [stateCountyGeo, metricSlug])

  const fmt = useCallback(
    (v: number) => formatMetricValue(metricSlug, v, metrics, valueMode),
    [metricSlug, metrics, valueMode],
  )

  const fmtRaw = useCallback(
    (v: number) => formatMetricValue(metricSlug, v, metrics, 'raw'),
    [metricSlug, metrics],
  )

  const stateRows = useMemo(() => {
    if (!statePayload) return []
    return Object.entries(statePayload.values).map(([st, row]) => {
      const name = typeof row.NAME === 'string' ? row.NAME : st
      const v = row[metricSlug]
      const num = typeof v === 'number' && Number.isFinite(v) ? v : null
      return { geoid: st, name, value: num }
    })
  }, [statePayload, metricSlug])

  const sortedStateRows = useMemo(() => {
    const arr = [...stateRows]
    const mul = tableSort.dir === 'asc' ? 1 : -1
    arr.sort((a, b) => {
      if (tableSort.key === 'geoid') return mul * a.geoid.localeCompare(b.geoid)
      if (tableSort.key === 'name') return mul * a.name.localeCompare(b.name)
      const av = a.value ?? -Infinity
      const bv = b.value ?? -Infinity
      return mul * (av - bv)
    })
    return arr
  }, [stateRows, tableSort])

  const barData = useMemo(() => {
    const withVal = stateRows.filter((r) => r.value != null).sort((a, b) => (b.value! - a.value!))
    return withVal.slice(0, 14).map((r) => ({
      name: r.name.length > 28 ? `${r.name.slice(0, 26)}…` : r.name,
      fullName: r.name,
      value: r.value,
      geoid: r.geoid,
    }))
  }, [stateRows])

  const onMetricChange = (slug: string) => {
    const q = searchParams.toString()
    if (mode === 'place' && stateFips) {
      navigate(`/census-map/place/${stateFips}/${effectiveVintage}/${slug}?${q}`)
    } else if (mode === 'stateCounty' && stateFips) {
      navigate(`/census-map/state/${stateFips}/${effectiveVintage}/${slug}?${q}`)
    } else {
      navigate(`/census-map/us/${effectiveVintage}/${slug}?${q}`)
    }
  }

  const onVintageChange = (v: string) => {
    const q = searchParams.toString()
    if (mode === 'place' && stateFips) {
      navigate(`/census-map/place/${stateFips}/${v}/${metricSlug}?${q}`)
    } else if (mode === 'stateCounty' && stateFips) {
      navigate(`/census-map/state/${stateFips}/${v}/${metricSlug}?${q}`)
    } else {
      navigate(`/census-map/us/${v}/${metricSlug}?${q}`)
    }
  }

  const stateFill = useCallback(
    (stateId: string) => {
      if (!statePayload?.values) return '#e2e8f0'
      const disp = stateDisplayById[stateId]
      const t = metricToDisplayT(disp, stateChoroExtent.min, stateChoroExtent.max, scale)
      return colorFromT(t)
    },
    [statePayload, stateDisplayById, stateChoroExtent.min, stateChoroExtent.max, scale],
  )

  const onStateClick = (stateId: string) => {
    const fid = normalizeStateFips(stateId)
    if (!fid) return
    navigate(`/census-map/state/${fid}/${effectiveVintage}/${metricSlug}?${searchParams.toString()}`)
  }

  const toggleTableSort = (key: 'name' | 'value' | 'geoid') => {
    setTableSort((prev) =>
      prev.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: key === 'value' ? 'desc' : 'asc' },
    )
  }

  if (manifestError) {
    return (
      <div className="max-w-3xl mx-auto p-8 text-slate-700">
        <h1 className="text-xl font-semibold text-slate-900">Census map</h1>
        <p className="mt-2">
          Static data is missing. Run{' '}
          <code className="rounded bg-slate-100 px-1">
            .venv/bin/python scripts/datasources/census/export_census_map_static.py
          </code>{' '}
          from the repo root after caching ACS parquets.
        </p>
      </div>
    )
  }

  if (!manifest) {
    return <div className="p-8 text-slate-600">Loading census map…</div>
  }

  const knownSlugs = new Set(metrics.map((m) => m.slug))
  if (metric && !knownSlugs.has(metric)) {
    const fallback = metrics[0]?.slug ?? 'median_household_income'
    if (mode === 'place' && stateFips) {
      return <Navigate to={`/census-map/place/${stateFips}/${effectiveVintage}/${fallback}`} replace />
    }
    if (mode === 'stateCounty' && stateFips) {
      return <Navigate to={`/census-map/state/${stateFips}/${effectiveVintage}/${fallback}`} replace />
    }
    return <Navigate to={`/census-map/us/${effectiveVintage}/${fallback}`} replace />
  }

  const stateUsps = stateFips ? FIPS2_TO_USPS[stateFips] : undefined
  const stateName = stateUsps ? STATE_CODE_TO_NAME[stateUsps] : undefined

  const singleVintage = vintages.length <= 1

  return (
    <div className="max-w-[1600px] mx-auto p-4 md:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Census explorer</h1>
          <p className="text-sm text-slate-600 mt-1">
            ACS 5-year estimates — US map is <strong>state</strong> level (filled or bubble). Click a state for a{' '}
            <strong>county</strong> map (national <code className="text-xs">county_metrics.json</code>). Optional city
            / place maps use bundled <code className="text-xs">place_*.geojson</code> from export. Color legend is
            hidden in bubble view.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-sm text-slate-600">Metric</label>
          <select
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm"
            value={metricSlug}
            onChange={(e) => onMetricChange(e.target.value)}
          >
            {metrics.map((m) => (
              <option key={m.slug} value={m.slug}>
                {m.label}
              </option>
            ))}
          </select>
          {(mode === 'place' || mode === 'stateCounty') && (
            <div className="flex flex-wrap items-center gap-2">
              <Link
                to={`/census-map/us/${effectiveVintage}/${metricSlug}?${searchParams.toString()}`}
                className="inline-flex items-center gap-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
              >
                <ArrowLeftIcon className="h-4 w-4" />
                US states
              </Link>
              {mode === 'stateCounty' && stateFips && placeStates.includes(stateFips) ? (
                <Link
                  to={`/census-map/place/${stateFips}/${effectiveVintage}/${metricSlug}?${searchParams.toString()}`}
                  className="inline-flex items-center gap-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                >
                  City / places
                </Link>
              ) : null}
              {mode === 'place' && stateFips ? (
                <Link
                  to={`/census-map/state/${stateFips}/${effectiveVintage}/${metricSlug}?${searchParams.toString()}`}
                  className="inline-flex items-center gap-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                >
                  Counties
                </Link>
              ) : null}
            </div>
          )}
        </div>
      </div>

      {mode === 'us' && (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_380px] gap-5 items-start">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <VintageAndPlayControls
                vintages={vintages}
                displayVintage={displayVintage}
                singleVintage={singleVintage}
                showPlay={showPlay}
                playing={playing}
                setPlaying={setPlaying}
                onVintageChange={onVintageChange}
              />
              <div className="h-6 w-px bg-slate-200 hidden sm:block" />
              <div className="flex rounded-md border border-slate-200 overflow-hidden">
                <button
                  type="button"
                  onClick={() => setViz('filled')}
                  className={`px-3 py-1.5 text-xs font-medium ${
                    viz === 'filled' ? 'bg-[#354F52] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  Filled
                </button>
                <button
                  type="button"
                  onClick={() => setViz('bubble')}
                  className={`px-3 py-1.5 text-xs font-medium border-l border-slate-200 ${
                    viz === 'bubble' ? 'bg-[#354F52] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  Bubbles
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase text-slate-500">Scale</span>
                <select
                  className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs shadow-sm"
                  value={scale}
                  onChange={(e) => setScale(e.target.value as CensusScaleId)}
                >
                  {CENSUS_SCALES.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase text-slate-500">Map value</span>
                <select
                  className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs shadow-sm max-w-[240px]"
                  value={valueMode}
                  onChange={(e) => setValueMode(e.target.value as CensusValueMode)}
                  title="YoY uses prior vintage from manifest order. Vs national uses pop-weighted state composite when exported, else Census U.S. row."
                >
                  <option value="raw">ACS value (color spread adjusted)</option>
                  <option value="yoy">% change vs prior vintage</option>
                  <option value="vs_natl">% vs national benchmark</option>
                </select>
              </div>
            </div>

            <div className="relative rounded-lg border border-slate-200 bg-white p-2 shadow-sm overflow-hidden">
              {!statePayload ? (
                <div className="h-[480px] flex flex-col items-center justify-center gap-2 px-4 text-center text-slate-500 text-sm">
                  <span>Loading state map…</span>
                  <span className="text-xs text-slate-400">
                    If this hangs, run export (needs <code className="text-[11px]">state_metrics.json</code>).
                  </span>
                </div>
              ) : (
                <>
                  <div className="w-full overflow-x-auto">
                    <ComposableMap
                      key={`census-us-${metricSlug}-${viz}-${scale}`}
                      projection="geoAlbersUsa"
                      projectionConfig={{ scale: 1000 }}
                      width={960}
                      height={520}
                    >
                      <Geographies geography={manifest.state_topo_cdn || STATES_TOPO}>
                        {({ geographies, projection }) => (
                          <>
                            {geographies.map((geo) => {
                              const sid = normalizeStateFips(geo.id) ?? String(geo.id)
                              const row = statePayload.values[sid]
                              const name = (row as { NAME?: string } | undefined)?.NAME
                              const isBubble = viz === 'bubble'
                              const fill = isBubble ? 'rgba(248,250,252,0.94)' : stateFill(sid)
                              const stroke = isBubble ? '#64748b' : '#fff'
                              const sw = isBubble ? 0.55 : 0.5
                              return (
                                <Geography
                                  key={geo.rsmKey}
                                  geography={geo}
                                  style={{
                                    default: {
                                      outline: 'none',
                                      cursor: 'default',
                                      fill,
                                      stroke,
                                      strokeWidth: sw,
                                      transition: CENSUS_CHORO_FILL_TRANSITION,
                                    },
                                    hover: {
                                      outline: 'none',
                                      cursor: 'pointer',
                                      fill: isBubble ? 'rgba(226,232,240,0.98)' : '#64748b',
                                      stroke,
                                      strokeWidth: sw,
                                      transition:
                                        'fill 0.2s cubic-bezier(0.65, 0, 0.35, 1), stroke 0.2s cubic-bezier(0.65, 0, 0.35, 1)',
                                    },
                                    pressed: {
                                      outline: 'none',
                                      fill,
                                      stroke,
                                      strokeWidth: sw,
                                    },
                                  }}
                                  onMouseEnter={() => {
                                    const v = row?.[metricSlug]
                                    setHoverRegion({
                                      id: sid,
                                      name: typeof name === 'string' ? name : sid,
                                      value: typeof v === 'number' ? v : null,
                                    })
                                  }}
                                  onMouseLeave={() => setHoverRegion(null)}
                                  onClick={() => onStateClick(sid)}
                                />
                              )
                            })}
                            {viz === 'bubble' &&
                              geographies.map((geo) => {
                                const sid = normalizeStateFips(geo.id) ?? String(geo.id)
                                const row = statePayload.values[sid]
                                const v = row?.[metricSlug]
                                const num = typeof v === 'number' && Number.isFinite(v) ? v : null
                                if (num == null) return null
                                const geom = geo.geometry
                                if (!geom) return null
                                let raw
                                try {
                                  raw = geoCentroid({
                                    type: 'Feature',
                                    properties: {},
                                    geometry: geom,
                                  } as GeoJSON.Feature)
                                } catch {
                                  return null
                                }
                                const pair = toLonLatPair(raw)
                                if (!pair) return null
                                const xy = safeProjectScreen(projection, pair)
                                if (!xy) return null
                                const r = bubbleRadiusPx(num, stateBubbleExtent.min, stateBubbleExtent.max, scale, 4, 20)
                                return (
                                  <g
                                    key={`bubble-${geo.rsmKey}`}
                                    transform={`translate(${xy[0]},${xy[1]})`}
                                    style={{ pointerEvents: 'none' }}
                                  >
                                    <circle
                                      r={r}
                                      fill="rgba(225,29,72,0.82)"
                                      stroke="#fff"
                                      strokeWidth={0.6}
                                    />
                                  </g>
                                )
                              })}
                          </>
                        )}
                      </Geographies>
                    </ComposableMap>
                  </div>
                  {hoverRegion && (
                    <div className="absolute bottom-3 left-3 rounded-md bg-slate-900/90 px-3 py-2 text-sm text-white shadow-lg pointer-events-none max-w-xs">
                      <div className="font-medium leading-snug">{hoverRegion.name}</div>
                      <div>{formatMetricValue(metricSlug, hoverRegion.value, metrics, valueMode)}</div>
                      <div className="text-xs text-slate-300 mt-1">Click for county-level map</div>
                    </div>
                  )}
                </>
              )}
              <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 px-1">
                <span>
                  U.S. Census Bureau ACS 5-year · state estimates (
                  <code className="text-[10px]">state_metrics.json</code>)
                </span>
                <span>
                  Color scale range (~4th–96th pct.): {fmt(stateChoroExtent.min)} — {fmt(stateChoroExtent.max)}
                </span>
              </div>
            </div>
          </div>

          <aside className="flex flex-col gap-4 xl:sticky xl:top-4">
            {viz === 'filled' && (
              <ChoroplethLegend
                min={stateChoroExtent.min}
                max={stateChoroExtent.max}
                scale={scale}
                format={fmt}
                valueMode={valueMode}
              />
            )}
            {viz === 'bubble' && (
              <BubbleLegend
                min={stateBubbleExtent.min}
                max={stateBubbleExtent.max}
                scale={scale}
                format={fmtRaw}
              />
            )}

            {stateTrends && hoverRegion ? (
              <AcTrendChart
                title={`${hoverRegion.name} · ${metrics.find((m) => m.slug === metricSlug)?.label ?? metricSlug}`}
                points={trendPointsFromSeries(
                  stateTrends.vintages,
                  stateTrends.by_state[hoverRegion.id]?.[metricSlug] as Record<string, unknown> | undefined,
                )}
                format={fmt}
              />
            ) : null}

            <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600 mb-2">
                <ChartBarSquareIcon className="h-4 w-4" />
                Top states
              </div>
              <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} layout="vertical" margin={{ left: 4, right: 8, top: 4, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200" horizontal={false} />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 10 }}
                      tickFormatter={(x) => {
                        const n = Number(x)
                        if (!Number.isFinite(n)) return ''
                        if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
                        if (Math.abs(n) >= 1000) return `${Math.round(n / 1000)}k`
                        return String(Math.round(n))
                      }}
                    />
                    <YAxis type="category" dataKey="name" width={118} tick={{ fontSize: 9 }} interval={0} />
                    <RechartsTooltip
                      formatter={(value: number) => [formatMetricValue(metricSlug, value, metrics, valueMode), '']}
                      labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName ?? ''}
                    />
                    <Bar dataKey="value" fill="#52796F" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col max-h-[min(420px,50vh)]">
              <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-100 bg-slate-50/90">
                <TableCellsIcon className="h-4 w-4 text-slate-600" />
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-600">All states</span>
                <span className="text-[10px] text-slate-500 ml-auto">{sortedStateRows.length} rows</span>
              </div>
              <div className="overflow-auto flex-1">
                <table className="min-w-full text-xs">
                  <thead className="sticky top-0 bg-white shadow-sm z-10">
                    <tr className="text-left text-slate-500 border-b border-slate-200">
                      <th className="px-2 py-2 font-medium">
                        <button type="button" className="hover:text-slate-900" onClick={() => toggleTableSort('geoid')}>
                          FIPS {tableSort.key === 'geoid' ? (tableSort.dir === 'asc' ? '↑' : '↓') : ''}
                        </button>
                      </th>
                      <th className="px-2 py-2 font-medium">
                        <button type="button" className="hover:text-slate-900" onClick={() => toggleTableSort('name')}>
                          Name {tableSort.key === 'name' ? (tableSort.dir === 'asc' ? '↑' : '↓') : ''}
                        </button>
                      </th>
                      <th className="px-2 py-2 font-medium text-right">
                        <button type="button" className="hover:text-slate-900" onClick={() => toggleTableSort('value')}>
                          Value {tableSort.key === 'value' ? (tableSort.dir === 'asc' ? '↑' : '↓') : ''}
                        </button>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sortedStateRows.map((row) => (
                      <tr
                        key={row.geoid}
                        className="hover:bg-slate-50 cursor-pointer"
                        onClick={() => onStateClick(row.geoid)}
                      >
                        <td className="px-2 py-1.5 font-mono text-slate-600">{row.geoid}</td>
                        <td className="px-2 py-1.5 text-slate-800 leading-snug">{row.name}</td>
                        <td className="px-2 py-1.5 text-right tabular-nums text-slate-800">
                          {formatMetricValue(metricSlug, row.value, metrics, valueMode)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </aside>
        </div>
      )}

      {mode === 'stateCounty' && stateFips && (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_380px] gap-5 items-start">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <VintageAndPlayControls
                vintages={vintages}
                displayVintage={displayVintage}
                singleVintage={singleVintage}
                showPlay={showPlay}
                playing={playing}
                setPlaying={setPlaying}
                onVintageChange={onVintageChange}
              />
              <div className="h-6 w-px bg-slate-200 hidden sm:block" />
              <div className="flex rounded-md border border-slate-200 overflow-hidden">
                <button
                  type="button"
                  onClick={() => setViz('filled')}
                  className={`px-3 py-1.5 text-xs font-medium ${
                    viz === 'filled' ? 'bg-[#354F52] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  Filled
                </button>
                <button
                  type="button"
                  onClick={() => setViz('bubble')}
                  className={`px-3 py-1.5 text-xs font-medium border-l border-slate-200 ${
                    viz === 'bubble' ? 'bg-[#354F52] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  Bubbles
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase text-slate-500">Scale</span>
                <select
                  className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs text-slate-900 shadow-sm"
                  value={scale}
                  onChange={(e) => setScale(e.target.value as CensusScaleId)}
                >
                  {CENSUS_SCALES.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase text-slate-500">Map value</span>
                <select
                  className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs shadow-sm max-w-[240px]"
                  value={valueMode}
                  onChange={(e) => setValueMode(e.target.value as CensusValueMode)}
                  title="YoY uses prior vintage from manifest order. Vs national uses pop-weighted state composite when exported, else Census U.S. row."
                >
                  <option value="raw">ACS value (color spread adjusted)</option>
                  <option value="yoy">% change vs prior vintage</option>
                  <option value="vs_natl">% vs national benchmark</option>
                </select>
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="border-b border-slate-100 px-4 py-2 text-sm text-slate-700 flex flex-wrap items-center gap-2">
                {stateName ? (
                  <span>
                    <span className="font-medium">{stateName}</span>
                    {stateUsps && <span className="text-slate-500"> ({stateUsps})</span>}
                    <span className="text-slate-500"> · Counties</span>
                  </span>
                ) : (
                  <span>State FIPS {stateFips} · Counties</span>
                )}
                {!countyPayload && countyPayloadLoading && <span className="text-slate-500">Loading metrics…</span>}
                {countyTopoLoading && <span className="text-slate-500">Loading boundaries…</span>}
                {countyPayloadError && (
                  <span className="text-amber-800 text-sm">
                    Missing <code className="text-xs">county_metrics.json</code> for this vintage — run census export
                    with county ACS cached.
                  </span>
                )}
                {countyPayload && countyTopo && !stateCountyGeo && (
                  <span className="text-amber-800 text-sm">No county features for this state (check state FIPS).</span>
                )}
              </div>
              <div className="h-[min(70vh,560px)] w-full bg-white relative z-0">
                {stateCountyGeo && (
                  <MapContainer
                    center={[37.8, -86.8]}
                    zoom={7}
                    className="h-full w-full census-choropleth-map"
                    scrollWheelZoom
                    style={{ minHeight: 400 }}
                  >
                    {viz === 'filled' && (
                      <GeoJSON
                        key={`${metricSlug}-${scale}-county-filled`}
                        data={stateCountyGeo}
                        style={(feature) => {
                          const p = feature?.properties as Record<string, unknown> | undefined
                          const gid = countyGeoidFromFeature(feature as GeoJSON.Feature)
                          const disp = countyDisplayByGeoid[gid]
                          const t = metricToDisplayT(disp, countyChoroExtent.min, countyChoroExtent.max, scale)
                          return {
                            fillColor: colorFromT(t),
                            color: '#334155',
                            weight: 0.5,
                            fillOpacity: 0.88,
                          }
                        }}
                        onEachFeature={(feature, layer) => {
                          const p = feature.properties as Record<string, unknown>
                          const gid = countyGeoidFromFeature(feature as GeoJSON.Feature)
                          const name = String(p?.NAME ?? gid ?? '')
                          const v = p?.[metricSlug]
                          const num = typeof v === 'number' && Number.isFinite(v) ? v : null
                          layer.bindPopup(
                            `<div><strong>${name}</strong><br/>${formatMetricValue(metricSlug, num, metrics, valueMode)}</div>`,
                          )
                          layer.on('mouseover', () => {
                            setCountyHover({ id: gid, name, value: num })
                          })
                          layer.on('mouseout', () => setCountyHover(null))
                        }}
                      />
                    )}
                    {viz === 'bubble' &&
                      stateCountyGeo.features.map((f, idx) => {
                        const p = f.properties as Record<string, unknown> | null
                        const id = String(p?.GEOID ?? idx)
                        const v = p?.[metricSlug]
                        const num = typeof v === 'number' && Number.isFinite(v) ? v : null
                        if (num == null || f.geometry == null) return null
                        const ll = featureLatLng(f)
                        if (!ll) return null
                        const r = bubbleRadiusPx(num, countyBubbleExtent.min, countyBubbleExtent.max, scale, 2.5, 16)
                        const name = String(p?.NAME ?? id)
                        return (
                          <CircleMarker
                            key={id}
                            center={[ll.lat, ll.lng]}
                            radius={r}
                            pathOptions={{
                              color: '#fff',
                              weight: 1,
                              fillColor: '#e11d48',
                              fillOpacity: 0.82,
                            }}
                          >
                            <LeafletTooltip direction="top" offset={[0, -4]} opacity={0.95}>
                              <div className="text-xs">
                                <div className="font-semibold">{name}</div>
                                <div>{formatMetricValue(metricSlug, num, metrics, valueMode)}</div>
                              </div>
                            </LeafletTooltip>
                          </CircleMarker>
                        )
                      })}
                    {viz === 'bubble' && (
                      <GeoJSON
                        data={stateCountyGeo}
                        interactive={false}
                        style={{
                          fillColor: 'transparent',
                          color: '#64748b',
                          weight: 0.4,
                          fillOpacity: 0,
                        }}
                      />
                    )}
                    <FlyToDataBounds data={stateCountyGeo} />
                  </MapContainer>
                )}
              </div>
            </div>
          </div>

          <aside className="flex flex-col gap-4 xl:sticky xl:top-4">
            {viz === 'filled' && (
              <ChoroplethLegend
                min={countyChoroExtent.min}
                max={countyChoroExtent.max}
                scale={scale}
                format={fmt}
                valueMode={valueMode}
              />
            )}
            {viz === 'bubble' && (
              <BubbleLegend
                min={countyBubbleExtent.min}
                max={countyBubbleExtent.max}
                scale={scale}
                format={fmtRaw}
              />
            )}
            {countyTrends && countyHover && stateFips ? (
              <AcTrendChart
                title={`${countyHover.name} · ${metrics.find((m) => m.slug === metricSlug)?.label ?? metricSlug}`}
                points={trendPointsFromSeries(
                  countyTrends.vintages,
                  countyTrends.byGeoid[countyHover.id]?.[metricSlug] as Record<string, unknown> | undefined,
                )}
                format={fmt}
              />
            ) : null}
            {stateCountyGeo && (
              <>
                <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600 mb-2">
                    <ChartBarSquareIcon className="h-4 w-4" />
                    Top counties
                  </div>
                  <div className="h-[220px] w-full">
                    <PlaceBarChart features={stateCountyGeo.features} metricSlug={metricSlug} metrics={metrics} />
                  </div>
                </div>
                <PlaceTable
                  features={stateCountyGeo.features}
                  metricSlug={metricSlug}
                  metrics={metrics}
                  tableLabel="All counties"
                />
              </>
            )}
          </aside>
        </div>
      )}

      {mode === 'place' && (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_380px] gap-5 items-start">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-sm">
              <VintageAndPlayControls
                vintages={vintages}
                displayVintage={displayVintage}
                singleVintage={singleVintage}
                showPlay={showPlay}
                playing={playing}
                setPlaying={setPlaying}
                onVintageChange={onVintageChange}
              />
              <div className="h-6 w-px bg-slate-200 hidden sm:block" />
              <div className="flex rounded-md border border-slate-200 overflow-hidden">
                <button
                  type="button"
                  onClick={() => setViz('filled')}
                  className={`px-3 py-1.5 text-xs font-medium ${
                    viz === 'filled' ? 'bg-[#354F52] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  Filled
                </button>
                <button
                  type="button"
                  onClick={() => setViz('bubble')}
                  className={`px-3 py-1.5 text-xs font-medium border-l border-slate-200 ${
                    viz === 'bubble' ? 'bg-[#354F52] text-white' : 'bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  Bubbles
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase text-slate-500">Scale</span>
                <select
                  className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs shadow-sm"
                  value={scale}
                  onChange={(e) => setScale(e.target.value as CensusScaleId)}
                >
                  {CENSUS_SCALES.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase text-slate-500">Map value</span>
                <select
                  className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-xs shadow-sm max-w-[240px]"
                  value={valueMode}
                  onChange={(e) => setValueMode(e.target.value as CensusValueMode)}
                  title="YoY uses prior vintage from manifest order. Vs national uses pop-weighted state composite when exported, else Census U.S. row."
                >
                  <option value="raw">ACS value (color spread adjusted)</option>
                  <option value="yoy">% change vs prior vintage</option>
                  <option value="vs_natl">% vs national benchmark</option>
                </select>
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="border-b border-slate-100 px-4 py-2 text-sm text-slate-700 flex flex-wrap items-center gap-2">
                {stateName ? (
                  <span>
                    <span className="font-medium">{stateName}</span>
                    {stateUsps && <span className="text-slate-500"> ({stateUsps})</span>}
                  </span>
                ) : (
                  <span>State FIPS {stateFips}</span>
                )}
                {!placeGeo && !placeGeoError && <span className="text-slate-500">Loading…</span>}
                {placeGeoError && (
                  <span className="text-amber-800 text-sm leading-snug">
                    Missing <code className="text-xs">place_{stateFips}.geojson</code>
                    <span className="block mt-1 text-xs font-normal text-amber-900/90">
                      From repo root: cache place ACS, then export —{' '}
                      <code className="rounded bg-amber-50 px-1 text-[11px]">
                        .venv/bin/python scripts/datasources/census/download_census_acs_data.py --geography place
                        --state {stateFips} --year {effectiveVintage}
                      </code>{' '}
                      then{' '}
                      <code className="rounded bg-amber-50 px-1 text-[11px]">
                        .venv/bin/python scripts/datasources/census/export_census_map_static.py --year{' '}
                        {effectiveVintage} --place-states {stateFips}
                      </code>
                    </span>
                  </span>
                )}
              </div>
              <div className="h-[min(70vh,560px)] w-full bg-white relative z-0">
                {placeGeoMerged && (
                  <MapContainer
                    center={[37.8, -86.8]}
                    zoom={7}
                    className="h-full w-full census-choropleth-map"
                    scrollWheelZoom
                    style={{ minHeight: 400 }}
                  >
                    {viz === 'filled' && (
                      <GeoJSON
                        key={`${metricSlug}-${scale}-place-filled`}
                        data={placeGeoMerged}
                        style={(feature) => {
                          const p = feature?.properties as Record<string, unknown> | undefined
                          const raw = String(p?.GEOID ?? '').replace(/\D/g, '')
                          const gid7 = raw.length <= 7 ? raw.padStart(7, '0') : raw.slice(-7).padStart(7, '0')
                          const disp = placeDisplayByGeoid[gid7]
                          const t = metricToDisplayT(disp, placeChoroExtent.min, placeChoroExtent.max, scale)
                          return {
                            fillColor: colorFromT(t),
                            color: '#334155',
                            weight: 0.5,
                            fillOpacity: 0.88,
                          }
                        }}
                        onEachFeature={(feature, layer) => {
                          const p = feature.properties as Record<string, unknown>
                          const raw = String(p?.GEOID ?? '').replace(/\D/g, '')
                          const gid7 = raw.length <= 7 ? raw.padStart(7, '0') : raw.slice(-7)
                          const name = String(p?.NAME ?? gid7 ?? '')
                          const v = p?.[metricSlug]
                          const num = typeof v === 'number' && Number.isFinite(v) ? v : null
                          layer.bindPopup(
                            `<div><strong>${name}</strong><br/>${formatMetricValue(metricSlug, num, metrics, valueMode)}</div>`,
                          )
                          layer.on('mouseover', () => {
                            setPlaceHover({ id: gid7, name, value: num })
                          })
                          layer.on('mouseout', () => setPlaceHover(null))
                        }}
                      />
                    )}
                    {viz === 'bubble' &&
                      placeGeoMerged.features.map((f, idx) => {
                        const p = f.properties as Record<string, unknown> | null
                        const id = String(p?.GEOID ?? idx)
                        const v = p?.[metricSlug]
                        const num = typeof v === 'number' && Number.isFinite(v) ? v : null
                        if (num == null || f.geometry == null) return null
                        const ll = featureLatLng(f)
                        if (!ll) return null
                        const r = bubbleRadiusPx(num, placeBubbleExtent.min, placeBubbleExtent.max, scale, 4, 22)
                        const name = String(p?.NAME ?? id)
                        return (
                          <CircleMarker
                            key={id}
                            center={[ll.lat, ll.lng]}
                            radius={r}
                            pathOptions={{
                              color: '#fff',
                              weight: 1,
                              fillColor: '#e11d48',
                              fillOpacity: 0.82,
                            }}
                          >
                            <LeafletTooltip direction="top" offset={[0, -4]} opacity={0.95}>
                              <div className="text-xs">
                                <div className="font-semibold">{name}</div>
                                <div>{formatMetricValue(metricSlug, num, metrics, valueMode)}</div>
                              </div>
                            </LeafletTooltip>
                          </CircleMarker>
                        )
                      })}
                    {viz === 'bubble' && (
                      <GeoJSON
                        data={placeGeoMerged}
                        interactive={false}
                        style={{
                          fillColor: 'transparent',
                          color: '#64748b',
                          weight: 0.4,
                          fillOpacity: 0,
                        }}
                      />
                    )}
                    <FlyToDataBounds data={placeGeoMerged} />
                  </MapContainer>
                )}
              </div>
            </div>
          </div>

          <aside className="flex flex-col gap-4 xl:sticky xl:top-4">
            {viz === 'filled' && (
              <ChoroplethLegend
                min={placeChoroExtent.min}
                max={placeChoroExtent.max}
                scale={scale}
                format={fmt}
                valueMode={valueMode}
              />
            )}
            {viz === 'bubble' && (
              <BubbleLegend
                min={placeBubbleExtent.min}
                max={placeBubbleExtent.max}
                scale={scale}
                format={fmtRaw}
              />
            )}
            {placeTrends && placeHover ? (
              <AcTrendChart
                title={`${placeHover.name} · ${metrics.find((m) => m.slug === metricSlug)?.label ?? metricSlug}`}
                points={trendPointsFromSeries(
                  placeTrends.vintages,
                  placeTrends.byGeoid[placeHover.id]?.[metricSlug] as Record<string, unknown> | undefined,
                )}
                format={fmt}
              />
            ) : null}
            {placeGeoMerged && (
              <>
                <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
                  <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600 mb-2">
                    <ChartBarSquareIcon className="h-4 w-4" />
                    Top places
                  </div>
                  <div className="h-[220px] w-full">
                    <PlaceBarChart features={placeGeoMerged.features} metricSlug={metricSlug} metrics={metrics} />
                  </div>
                </div>
                <PlaceTable features={placeGeoMerged.features} metricSlug={metricSlug} metrics={metrics} />
              </>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}

function PlaceBarChart({
  features,
  metricSlug,
  metrics,
}: {
  features: GeoJSON.Feature[]
  metricSlug: string
  metrics: CensusMetric[]
}) {
  const rows = useMemo(() => {
    const list = features
      .map((f, i) => {
        const p = f.properties as Record<string, unknown> | null
        const v = p?.[metricSlug]
        const num = typeof v === 'number' && Number.isFinite(v) ? v : null
        const name = String(p?.NAME ?? p?.GEOID ?? i)
        return { name, fullName: name, value: num }
      })
      .filter((r) => r.value != null)
      .sort((a, b) => (b.value! - a.value!))
      .slice(0, 14)
      .map((r) => ({
        ...r,
        name: r.name.length > 26 ? `${r.name.slice(0, 24)}…` : r.name,
      }))
    return list
  }, [features, metricSlug])

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={rows} layout="vertical" margin={{ left: 4, right: 8, top: 4, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 10 }}
          tickFormatter={(x) => {
            const n = Number(x)
            if (!Number.isFinite(n)) return ''
            if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
            if (Math.abs(n) >= 1000) return `${Math.round(n / 1000)}k`
            return String(Math.round(n))
          }}
        />
        <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 9 }} interval={0} />
        <RechartsTooltip
          formatter={(value: number) => [formatMetricValue(metricSlug, value, metrics, valueMode), '']}
          labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName ?? ''}
        />
        <Bar dataKey="value" fill="#52796F" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

function PlaceTable({
  features,
  metricSlug,
  metrics,
  tableLabel = 'All places',
}: {
  features: GeoJSON.Feature[]
  metricSlug: string
  metrics: CensusMetric[]
  tableLabel?: string
}) {
  const [sort, setSort] = useState<{ key: 'name' | 'value' | 'geoid'; dir: 'asc' | 'desc' }>({
    key: 'value',
    dir: 'desc',
  })
  const rows = useMemo(() => {
    return features.map((f, i) => {
      const p = f.properties as Record<string, unknown> | null
      const geoid = String(p?.GEOID ?? i)
      const name = String(p?.NAME ?? geoid)
      const v = p?.[metricSlug]
      const num = typeof v === 'number' && Number.isFinite(v) ? v : null
      return { geoid, name, value: num }
    })
  }, [features, metricSlug])

  const sorted = useMemo(() => {
    const arr = [...rows]
    const mul = sort.dir === 'asc' ? 1 : -1
    arr.sort((a, b) => {
      if (sort.key === 'geoid') return mul * a.geoid.localeCompare(b.geoid)
      if (sort.key === 'name') return mul * a.name.localeCompare(b.name)
      const av = a.value ?? -Infinity
      const bv = b.value ?? -Infinity
      return mul * (av - bv)
    })
    return arr
  }, [rows, sort])

  const toggle = (key: 'name' | 'value' | 'geoid') => {
    setSort((prev) =>
      prev.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: key === 'value' ? 'desc' : 'asc' },
    )
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col max-h-[min(420px,50vh)]">
      <div className="flex items-center gap-2 px-3 py-2 border-b border-slate-100 bg-slate-50/90">
        <TableCellsIcon className="h-4 w-4 text-slate-600" />
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-600">{tableLabel}</span>
        <span className="text-[10px] text-slate-500 ml-auto">{sorted.length} rows</span>
      </div>
      <div className="overflow-auto flex-1">
        <table className="min-w-full text-xs">
          <thead className="sticky top-0 bg-white shadow-sm z-10">
            <tr className="text-left text-slate-500 border-b border-slate-200">
              <th className="px-2 py-2 font-medium">
                <button type="button" className="hover:text-slate-900" onClick={() => toggle('geoid')}>
                  GEOID {sort.key === 'geoid' ? (sort.dir === 'asc' ? '↑' : '↓') : ''}
                </button>
              </th>
              <th className="px-2 py-2 font-medium">
                <button type="button" className="hover:text-slate-900" onClick={() => toggle('name')}>
                  Name {sort.key === 'name' ? (sort.dir === 'asc' ? '↑' : '↓') : ''}
                </button>
              </th>
              <th className="px-2 py-2 font-medium text-right">
                <button type="button" className="hover:text-slate-900" onClick={() => toggle('value')}>
                  Value {sort.key === 'value' ? (sort.dir === 'asc' ? '↑' : '↓') : ''}
                </button>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sorted.map((row) => (
              <tr key={row.geoid} className="hover:bg-slate-50">
                <td className="px-2 py-1.5 font-mono text-slate-600">{row.geoid}</td>
                <td className="px-2 py-1.5 text-slate-800 leading-snug">{row.name}</td>
                <td className="px-2 py-1.5 text-right tabular-nums text-slate-800">
                  {formatMetricValue(metricSlug, row.value, metrics, valueMode)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default CensusMapPage
