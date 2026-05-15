/**
 * Entity-first jurisdiction mapping quality dashboard (layout inspired by internal mock:
 * entity tiles (incl. State) → sub-sections Overview / Population / Income when a type tile is selected).
 * Uses live JSON from export_jurisdiction_mapping_quality_json.py including entity_state_rollup.
 * Styling stays on the light `.jmq-quality-page` tokens — do not switch the page to a dark/black background.
 */
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import {
  ArrowLeftIcon,
  ChevronDownIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { DATA_EXPLORER_MAP_BASE } from '../../utils/dataExplorerPaths'

const US_STATE_NAMES: Record<string, string> = {
  AL: 'Alabama',
  AK: 'Alaska',
  AZ: 'Arizona',
  AR: 'Arkansas',
  CA: 'California',
  CO: 'Colorado',
  CT: 'Connecticut',
  DE: 'Delaware',
  FL: 'Florida',
  GA: 'Georgia',
  HI: 'Hawaii',
  ID: 'Idaho',
  IL: 'Illinois',
  IN: 'Indiana',
  IA: 'Iowa',
  KS: 'Kansas',
  KY: 'Kentucky',
  LA: 'Louisiana',
  ME: 'Maine',
  MD: 'Maryland',
  MA: 'Massachusetts',
  MI: 'Michigan',
  MN: 'Minnesota',
  MS: 'Mississippi',
  MO: 'Missouri',
  MT: 'Montana',
  NE: 'Nebraska',
  NV: 'Nevada',
  NH: 'New Hampshire',
  NJ: 'New Jersey',
  NM: 'New Mexico',
  NY: 'New York',
  NC: 'North Carolina',
  ND: 'North Dakota',
  OH: 'Ohio',
  OK: 'Oklahoma',
  OR: 'Oregon',
  PA: 'Pennsylvania',
  RI: 'Rhode Island',
  SC: 'South Carolina',
  SD: 'South Dakota',
  TN: 'Tennessee',
  TX: 'Texas',
  UT: 'Utah',
  VT: 'Vermont',
  VA: 'Virginia',
  WA: 'Washington',
  WV: 'West Virginia',
  WI: 'Wisconsin',
  WY: 'Wyoming',
}

type SummaryRow = {
  jurisdiction_type: string
  total_jurisdictions: number
  with_primary_website: number
  pct_with_primary_website: number | null
  with_primary_url_syntax_ok?: number
  with_primary_url_likely_wrong_host?: number
  jurisdictions_touching_naco: number
  jurisdictions_touching_uscm: number
  jurisdictions_touching_nces: number
  jurisdictions_touching_gsa: number
  jurisdictions_touching_override: number
}

type MunicipalityPlaceSummaryRow = {
  municipality_place_kind: string
  total_jurisdictions: number
  with_primary_website: number
  pct_with_primary_website: number | null
  with_primary_url_syntax_ok?: number
  jurisdictions_touching_naco: number
  jurisdictions_touching_uscm: number
  jurisdictions_touching_nces: number
  jurisdictions_touching_gsa: number
  jurisdictions_touching_override: number
}

type SourceRow = { website_source: string; distinct_jurisdictions: number }

type StateRollupRow = {
  state_code: string
  total_jurisdictions: number
  with_primary_website: number
  pct_with_primary_website: number | null
}

type UnmappedDrillRow = {
  jurisdiction_id: string
  name: string
  state_code: string
  jurisdiction_type: string
  geoid?: string | null
  municipality_place_kind?: string | null
  n_website_candidate_rows?: number | null
  has_naco_source?: boolean | null
  has_uscm_source?: boolean | null
  has_nces_directory_source?: boolean | null
  has_gsa_source?: boolean | null
  has_override_source?: boolean | null
  acs_population_tier?: string | null
  acs_income_level?: string | null
}

type MappedUrlIssueDrillRow = UnmappedDrillRow & {
  primary_website_url: string | null
  primary_website_source: string | null
  primary_url_syntax_ok: boolean | null
  primary_url_likely_wrong_host: boolean | null
  primary_url_passes_basic_checks: boolean | null
}

type DrilldownPayload = {
  unmapped: UnmappedDrillRow[]
  mapped_url_issues: MappedUrlIssueDrillRow[]
}

export type QualityPayload = {
  generated_at: string | null
  database_host?: string | null
  summary_by_type: SummaryRow[]
  summary_municipality_by_place_kind?: MunicipalityPlaceSummaryRow[]
  summary_by_acs_population_tier?: {
    jurisdiction_type: string
    acs_population_tier: string
    total_jurisdictions: number
    with_primary_website: number
    pct_with_primary_website: number | null
  }[]
  summary_by_acs_income_level?: {
    jurisdiction_type: string
    acs_income_level: string
    total_jurisdictions: number
    with_primary_website: number
    pct_with_primary_website: number | null
  }[]
  candidates_by_source: SourceRow[]
  n_source_detail_rows?: number
  sources_explained?: Record<string, string>
  drilldown?: DrilldownPayload
  entity_state_rollup?: {
    county: StateRollupRow[]
    municipality_incorporated_city: StateRollupRow[]
    municipality_towns_and_cdp: StateRollupRow[]
    school_district: StateRollupRow[]
  }
}

export type EntityKey = 'cities' | 'towns' | 'counties' | 'schools' | 'state'

const ENTITY_ROLLUP_KEY: Record<Exclude<EntityKey, 'state'>, keyof NonNullable<QualityPayload['entity_state_rollup']>> = {
  cities: 'municipality_incorporated_city',
  towns: 'municipality_towns_and_cdp',
  counties: 'county',
  schools: 'school_district',
}

const ENTITY_STATE_ROLLUP_KEYS = [
  'county',
  'municipality_incorporated_city',
  'municipality_towns_and_cdp',
  'school_district',
] as const satisfies readonly (keyof NonNullable<QualityPayload['entity_state_rollup']>)[]

/** Per-state totals summed across counties, cities, towns/CDP, and school districts (disjoint jurisdiction types). */
function mergeStateRollups(rollups: NonNullable<QualityPayload['entity_state_rollup']>): StateRollupRow[] {
  const byState = new Map<string, { total: number; withUrl: number }>()
  for (const key of ENTITY_STATE_ROLLUP_KEYS) {
    for (const r of rollups[key] ?? []) {
      const sc = String(r.state_code ?? '').trim()
      if (!sc) continue
      const prev = byState.get(sc) ?? { total: 0, withUrl: 0 }
      prev.total += Number(r.total_jurisdictions)
      prev.withUrl += Number(r.with_primary_website)
      byState.set(sc, prev)
    }
  }
  return Array.from(byState.entries())
    .map(([state_code, { total, withUrl }]) => {
      const pct = total > 0 ? Math.round((1000 * withUrl) / total) / 10 : null
      return {
        state_code,
        total_jurisdictions: total,
        with_primary_website: withUrl,
        pct_with_primary_website: pct,
      }
    })
    .sort((a, b) => a.state_code.localeCompare(b.state_code))
}

const ENTITY_META: Record<
  EntityKey,
  { label: string; icon: string; accentVar: string; sourceKeys: string[] }
> = {
  state: {
    label: 'State',
    icon: '📍',
    accentVar: '--jmq-teal',
    sourceKeys: ['naco', 'uscm', 'nces_directory', 'gsa', 'override'],
  },
  cities: {
    label: 'Cities',
    icon: '🏙',
    accentVar: '--jmq-amber',
    sourceKeys: ['uscm', 'gsa', 'override'],
  },
  towns: {
    label: 'Towns & Villages',
    icon: '🏘',
    accentVar: '--jmq-red',
    sourceKeys: ['gsa', 'override'],
  },
  counties: {
    label: 'Counties',
    icon: '🗺',
    accentVar: '--jmq-teal',
    sourceKeys: ['naco', 'gsa', 'override'],
  },
  schools: {
    label: 'School Districts',
    icon: '🏫',
    accentVar: '--jmq-blue',
    sourceKeys: ['nces_directory', 'gsa', 'override'],
  },
}

function fmt(n: number): string {
  return Number(n).toLocaleString()
}

/** Shared Y-axis title for bar charts that plot share with a primary website URL. */
const AXIS_LABEL_PCT_WITH_PRIMARY_URL = '% with primary URL'

function barColor(p: number): string {
  if (p >= 80) return '#117a72'
  if (p >= 50) return '#0969da'
  if (p >= 25) return '#9a6700'
  return '#a40e26'
}

function aggregateMuniKinds(
  rows: MunicipalityPlaceSummaryRow[] | undefined,
  kinds: string[],
): {
  total: number
  withUrl: number
  pct: number
  syntaxOk: number
  touch: Pick<
    MunicipalityPlaceSummaryRow,
    | 'jurisdictions_touching_naco'
    | 'jurisdictions_touching_uscm'
    | 'jurisdictions_touching_nces'
    | 'jurisdictions_touching_gsa'
    | 'jurisdictions_touching_override'
  >
} {
  let total = 0
  let withUrl = 0
  let syntaxOk = 0
  const touch = { naco: 0, uscm: 0, nces: 0, gsa: 0, override: 0 }
  for (const r of rows ?? []) {
    if (!kinds.includes(r.municipality_place_kind)) continue
    total += Number(r.total_jurisdictions)
    withUrl += Number(r.with_primary_website)
    syntaxOk += Number(r.with_primary_url_syntax_ok ?? 0)
    touch.naco += Number(r.jurisdictions_touching_naco)
    touch.uscm += Number(r.jurisdictions_touching_uscm)
    touch.nces += Number(r.jurisdictions_touching_nces)
    touch.gsa += Number(r.jurisdictions_touching_gsa)
    touch.override += Number(r.jurisdictions_touching_override)
  }
  const pct = total > 0 ? (100 * withUrl) / total : 0
  return {
    total,
    withUrl,
    pct,
    syntaxOk,
    touch: {
      jurisdictions_touching_naco: touch.naco,
      jurisdictions_touching_uscm: touch.uscm,
      jurisdictions_touching_nces: touch.nces,
      jurisdictions_touching_gsa: touch.gsa,
      jurisdictions_touching_override: touch.override,
    },
  }
}

function entityMetrics(
  entity: EntityKey,
  summaryByType: SummaryRow[],
  muniRows: MunicipalityPlaceSummaryRow[] | undefined,
): {
  total: number
  withUrl: number
  pct: number
  syntaxErr: number
  touch: MunicipalityPlaceSummaryRow | SummaryRow | null
} {
  if (entity === 'state') {
    const county = summaryByType.find((x) => x.jurisdiction_type === 'county')
    const school = summaryByType.find((x) => x.jurisdiction_type === 'school_district')
    const city = muniRows?.find((x) => x.municipality_place_kind === 'incorporated_city')
    const agg = aggregateMuniKinds(muniRows, ['incorporated_other', 'unknown', 'census_designated_place'])
    const total =
      Number(county?.total_jurisdictions ?? 0) +
      Number(school?.total_jurisdictions ?? 0) +
      Number(city?.total_jurisdictions ?? 0) +
      agg.total
    const withUrl =
      Number(county?.with_primary_website ?? 0) +
      Number(school?.with_primary_website ?? 0) +
      Number(city?.with_primary_website ?? 0) +
      agg.withUrl
    const syn =
      Number(county?.with_primary_url_syntax_ok ?? 0) +
      Number(school?.with_primary_url_syntax_ok ?? 0) +
      Number(city?.with_primary_url_syntax_ok ?? 0) +
      agg.syntaxOk
    const pct = total > 0 ? (100 * withUrl) / total : 0
    const touch: SummaryRow = {
      jurisdiction_type: 'state_view',
      total_jurisdictions: total,
      with_primary_website: withUrl,
      pct_with_primary_website: pct,
      with_primary_url_syntax_ok: syn,
      jurisdictions_touching_naco:
        Number(county?.jurisdictions_touching_naco ?? 0) +
        Number(school?.jurisdictions_touching_naco ?? 0) +
        Number(city?.jurisdictions_touching_naco ?? 0) +
        Number(agg.touch.jurisdictions_touching_naco ?? 0),
      jurisdictions_touching_uscm:
        Number(county?.jurisdictions_touching_uscm ?? 0) +
        Number(school?.jurisdictions_touching_uscm ?? 0) +
        Number(city?.jurisdictions_touching_uscm ?? 0) +
        Number(agg.touch.jurisdictions_touching_uscm ?? 0),
      jurisdictions_touching_nces:
        Number(county?.jurisdictions_touching_nces ?? 0) +
        Number(school?.jurisdictions_touching_nces ?? 0) +
        Number(city?.jurisdictions_touching_nces ?? 0) +
        Number(agg.touch.jurisdictions_touching_nces ?? 0),
      jurisdictions_touching_gsa:
        Number(county?.jurisdictions_touching_gsa ?? 0) +
        Number(school?.jurisdictions_touching_gsa ?? 0) +
        Number(city?.jurisdictions_touching_gsa ?? 0) +
        Number(agg.touch.jurisdictions_touching_gsa ?? 0),
      jurisdictions_touching_override:
        Number(county?.jurisdictions_touching_override ?? 0) +
        Number(school?.jurisdictions_touching_override ?? 0) +
        Number(city?.jurisdictions_touching_override ?? 0) +
        Number(agg.touch.jurisdictions_touching_override ?? 0),
    } as SummaryRow
    return {
      total,
      withUrl,
      pct,
      syntaxErr: Math.max(0, withUrl - syn),
      touch,
    }
  }
  if (entity === 'counties') {
    const r = summaryByType.find((x) => x.jurisdiction_type === 'county')
    if (!r) return { total: 0, withUrl: 0, pct: 0, syntaxErr: 0, touch: null }
    const w = Number(r.with_primary_website)
    const syn = Number(r.with_primary_url_syntax_ok ?? 0)
    return {
      total: Number(r.total_jurisdictions),
      withUrl: w,
      pct: Number(r.pct_with_primary_website ?? 0),
      syntaxErr: Math.max(0, w - syn),
      touch: r,
    }
  }
  if (entity === 'schools') {
    const r = summaryByType.find((x) => x.jurisdiction_type === 'school_district')
    if (!r) return { total: 0, withUrl: 0, pct: 0, syntaxErr: 0, touch: null }
    const w = Number(r.with_primary_website)
    const syn = Number(r.with_primary_url_syntax_ok ?? 0)
    return {
      total: Number(r.total_jurisdictions),
      withUrl: w,
      pct: Number(r.pct_with_primary_website ?? 0),
      syntaxErr: Math.max(0, w - syn),
      touch: r,
    }
  }
  if (entity === 'cities') {
    const row = muniRows?.find((x) => x.municipality_place_kind === 'incorporated_city')
    if (!row) return { total: 0, withUrl: 0, pct: 0, syntaxErr: 0, touch: null }
    const w = Number(row.with_primary_website)
    const syn = Number(row.with_primary_url_syntax_ok ?? 0)
    return {
      total: Number(row.total_jurisdictions),
      withUrl: w,
      pct: Number(row.pct_with_primary_website ?? 0),
      syntaxErr: Math.max(0, w - syn),
      touch: row,
    }
  }
  const agg = aggregateMuniKinds(muniRows, ['incorporated_other', 'unknown', 'census_designated_place'])
  const syntaxErr = Math.max(0, agg.withUrl - agg.syntaxOk)
  return { total: agg.total, withUrl: agg.withUrl, pct: agg.pct, syntaxErr, touch: null }
}

function sourcePie(
  touch: SummaryRow | MunicipalityPlaceSummaryRow | null,
  entity: EntityKey,
): { name: string; value: number; fill: string }[] {
  if (!touch) return []
  const allowed = new Set(ENTITY_META[entity].sourceKeys)
  const defs: { sourceKey: string; field: keyof SummaryRow; short: string; fill: string }[] = [
    { sourceKey: 'naco', field: 'jurisdictions_touching_naco', short: 'naco', fill: '#6e40c9' },
    { sourceKey: 'uscm', field: 'jurisdictions_touching_uscm', short: 'uscm', fill: '#0969da' },
    { sourceKey: 'nces_directory', field: 'jurisdictions_touching_nces', short: 'nces', fill: '#117a72' },
    { sourceKey: 'gsa', field: 'jurisdictions_touching_gsa', short: 'gsa', fill: '#9a6700' },
    { sourceKey: 'override', field: 'jurisdictions_touching_override', short: 'override', fill: '#116329' },
  ]
  const out: { name: string; value: number; fill: string }[] = []
  for (const d of defs) {
    if (!allowed.has(d.sourceKey)) continue
    const v = Number((touch as SummaryRow)[d.field] ?? 0)
    if (v > 0) out.push({ name: d.short, value: v, fill: d.fill })
  }
  return out
}

function matchesEntityUnmapped(entity: EntityKey, r: UnmappedDrillRow): boolean {
  if (entity === 'state') return true
  if (entity === 'counties') return r.jurisdiction_type === 'county'
  if (entity === 'schools') return r.jurisdiction_type === 'school_district'
  if (r.jurisdiction_type !== 'municipality') return false
  const k = r.municipality_place_kind ?? 'unknown'
  if (entity === 'cities') return k === 'incorporated_city'
  return k === 'incorporated_other' || k === 'unknown' || k === 'census_designated_place'
}

function sourceBadgeClass(src: string): string {
  const base = 'jmq-src-badge !m-0'
  const m: Record<string, string> = {
    naco: 'jmq-src-badge--naco',
    uscm: 'jmq-src-badge--uscm',
    nces_directory: 'jmq-src-badge--nces_directory',
    gsa: 'jmq-src-badge--gsa',
    override: 'jmq-src-badge--override',
  }
  return `${base} ${m[src] ?? ''}`.trim()
}

function CovBarLite({ pct, width = 100 }: { pct: number; width?: number }) {
  const c = barColor(pct)
  const w = Math.min(100, Math.max(0, pct))
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-1.5 shrink-0 overflow-hidden rounded bg-[var(--jmq-surface2)]"
        style={{ width }}
      >
        <div className="h-full rounded" style={{ width: `${w}%`, background: c }} />
      </div>
      <span className="w-10 shrink-0 text-right font-mono text-[11px]" style={{ color: c }}>
        {pct.toFixed(0)}%
      </span>
    </div>
  )
}

function DrillPanel({
  rows,
  title,
  subtitle,
  onClose,
  bannerExtra,
}: {
  rows: UnmappedDrillRow[]
  title: string
  subtitle: string
  onClose: () => void
  /** Optional second line in the amber banner (e.g. fallback sample explanation). */
  bannerExtra?: string | null
}) {
  const modal = (
    <div
      className="jmq-modal-portal-root jmq-modal-scrim fixed inset-0 z-[300] flex items-start justify-end p-4"
      role="dialog"
      aria-modal
      aria-labelledby="jmq-drill-title"
      onClick={(ev) => {
        if (ev.target === ev.currentTarget) onClose()
      }}
    >
      <div
        className="flex max-h-[92vh] w-full max-w-2xl flex-col overflow-hidden rounded-xl border border-[var(--jmq-border)] bg-[var(--jmq-surface)] shadow-2xl"
        onClick={(ev) => ev.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b border-[var(--jmq-border)] px-4 py-3">
          <div className="h-7 w-1 shrink-0 rounded bg-[var(--jmq-teal)]" />
          <div className="min-w-0 flex-1">
            <div id="jmq-drill-title" className="text-[15px] font-bold text-[var(--jmq-text)]">
              {title}
            </div>
            <div className="mt-0.5 font-mono text-xs text-[var(--jmq-text-muted)]">{subtitle}</div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-md border border-[var(--jmq-border)] bg-[var(--jmq-surface2)] px-3 py-1 text-xs text-[var(--jmq-text-muted)] hover:bg-[#e6eaef]"
          >
            ✕ Close
          </button>
        </div>
        <div className="border-b border-[var(--jmq-border)] bg-[var(--jmq-amber-dim)] px-4 py-2 text-[11px] text-[#4d2d00]">
          <div>Sample from JSON export (capped). Query Postgres for full unmapped set.</div>
          {bannerExtra ? <div className="mt-1 font-medium">{bannerExtra}</div> : null}
        </div>
        <div className="flex-1 overflow-y-auto">
          {rows.length === 0 ? (
            <div className="p-10 text-center text-sm text-[var(--jmq-green)]">No matching rows in this sample.</div>
          ) : (
            <table className="w-full border-collapse text-xs">
              <thead className="sticky top-0 bg-[var(--jmq-surface2)]">
                <tr>
                  {['Jurisdiction', 'State', 'GEOID', 'ACS pop', 'ACS income', 'Directories'].map((h) => (
                    <th
                      key={h}
                      className="border-b border-[var(--jmq-border)] px-3 py-2 text-left font-mono text-[10px] font-semibold uppercase tracking-wide text-[var(--jmq-text-muted)]"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.jurisdiction_id} className="border-b border-[var(--jmq-border)]/60 hover:bg-[var(--jmq-surface2)]">
                    <td className="px-3 py-2 font-medium text-[var(--jmq-text)]">{r.name}</td>
                    <td className="px-3 py-2 font-mono text-[var(--jmq-text-muted)]">{r.state_code}</td>
                    <td className="px-3 py-2 font-mono text-[10px] text-[var(--jmq-text-muted)]">{r.geoid ?? '—'}</td>
                    <td className="px-3 py-2 font-mono text-[10px]">{r.acs_population_tier ?? '—'}</td>
                    <td className="px-3 py-2 font-mono text-[10px]">{r.acs_income_level ?? '—'}</td>
                    <td className="px-3 py-2 font-mono text-[10px] text-[var(--jmq-text-muted)]">
                      {[r.has_naco_source && 'NACo', r.has_uscm_source && 'USCM', r.has_nces_directory_source && 'NCES', r.has_gsa_source && 'GSA', r.has_override_source && 'ovr']
                        .filter(Boolean)
                        .join(', ') || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
  if (typeof document === 'undefined') return null
  return createPortal(modal, document.body)
}

function StateAnalysisSection({
  entity,
  rollup,
  unmapped,
}: {
  entity: EntityKey
  rollup: StateRollupRow[]
  unmapped: UnmappedDrillRow[]
}) {
  const [view, setView] = useState<'worst' | 'best' | 'all'>('worst')
  const [search, setSearch] = useState('')
  const [sortCol, setSortCol] = useState<'pct' | 'missing' | 'total_jurisdictions' | 'state_code'>('pct')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  type EnrichedState = StateRollupRow & { name: string; missing: number; pct: number }
  const [drill, setDrill] = useState<EnrichedState | null>(null)

  const enriched = useMemo(
    () =>
      rollup.map((r) => {
        const total = Number(r.total_jurisdictions)
        const withUrl = Number(r.with_primary_website)
        const pct = r.pct_with_primary_website != null ? Number(r.pct_with_primary_website) : total > 0 ? (100 * withUrl) / total : 0
        return {
          ...r,
          name: US_STATE_NAMES[r.state_code] ?? r.state_code,
          missing: Math.max(0, total - withUrl),
          pct,
        }
      }),
    [rollup],
  )

  const filtered = useMemo(() => {
    let rows = [...enriched]
    const q = search.trim().toLowerCase()
    if (q) rows = rows.filter((r) => r.name.toLowerCase().includes(q) || r.state_code.toLowerCase().includes(q))
    rows.sort((a, b) => {
      let c = 0
      if (sortCol === 'state_code') c = a.state_code.localeCompare(b.state_code)
      else if (sortCol === 'total_jurisdictions')
        c = Number(a.total_jurisdictions) - Number(b.total_jurisdictions)
      else c = Number(a[sortCol]) - Number(b[sortCol])
      return sortDir === 'asc' ? c : -c
    })
    if (!q && view === 'worst') return rows.slice(0, 15)
    if (!q && view === 'best') return [...enriched].sort((a, b) => b.pct - a.pct).slice(0, 15)
    return rows
  }, [enriched, search, sortCol, sortDir, view])

  const chartData = useMemo(() => {
    const base = [...enriched].sort((a, b) => a.pct - b.pct)
    if (view === 'best') return base.slice(-20).reverse()
    return base.slice(0, 20)
  }, [enriched, view])

  const worst = [...enriched].sort((a, b) => a.pct - b.pct)[0]
  const best = [...enriched].sort((a, b) => b.pct - a.pct)[0]
  const spread = worst && best ? (best.pct - worst.pct).toFixed(1) : '0'

  const drillRows = useMemo(() => {
    if (!drill) return []
    return unmapped.filter((r) => r.state_code === drill.state_code && matchesEntityUnmapped(entity, r)).slice(0, 80)
  }, [drill, unmapped, entity])

  const setDrillFromBar = (barData: unknown) => {
    const p = (barData as { payload?: EnrichedState } | null)?.payload
    if (p?.state_code) setDrill(p)
  }

  const toggleSort = (col: 'pct' | 'missing' | 'total_jurisdictions' | 'state_code') => {
    if (sortCol === col) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    else {
      setSortCol(col)
      setSortDir(col === 'missing' ? 'desc' : 'asc')
    }
  }

  return (
    <div>
      {drill ? (
        <DrillPanel
          rows={drillRows}
          title="Unmapped sample"
          subtitle={`${drill.name} (${drill.state_code}) · ${fmt(drill.missing)} missing in warehouse`}
          bannerExtra={
            drillRows.length === 0
              ? 'No rows for this state + entity in the exported unmapped sample (list is capped globally). Re-export with a higher JURIS_MAPPING_QUALITY_UNMAPPED_CAP or query Postgres.'
              : null
          }
          onClose={() => setDrill(null)}
        />
      ) : null}

      <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { label: 'States in snapshot', val: fmt(enriched.length) },
          { label: 'Worst coverage', val: worst ? `${worst.state_code} (${worst.pct.toFixed(1)}%)` : '—' },
          { label: 'Best coverage', val: best ? `${best.state_code} (${best.pct.toFixed(1)}%)` : '—' },
          { label: 'Spread (pp)', val: `Δ ${spread}` },
        ].map((k) => (
          <div key={k.label} className="rounded-lg border border-[var(--jmq-border)] bg-[var(--jmq-surface2)] px-3 py-2">
            <div className="font-mono text-[10px] font-semibold uppercase tracking-wide text-[var(--jmq-text-muted)]">
              {k.label}
            </div>
            <div className="mt-1 font-mono text-sm font-bold text-[var(--jmq-text)]">{k.val}</div>
          </div>
        ))}
      </div>

      <div className="jmq-pill-row mb-3">
        {(
          [
            ['worst', '15 Worst states'],
            ['best', '15 Best states'],
            ['all', 'All states'],
          ] as const
        ).map(([id, lbl]) => (
          <button
            key={id}
            type="button"
            className={`jmq-pill text-xs ${view === id && !search ? 'jmq-pill--active' : ''}`}
            onClick={() => {
              setView(id)
              setSearch('')
              setSortCol('pct')
              setSortDir(id === 'best' ? 'desc' : 'asc')
            }}
          >
            {lbl}
          </button>
        ))}
        <input
          type="search"
          placeholder="Search state…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setView('all')
          }}
          className="ml-auto w-44 rounded-md border border-[var(--jmq-border)] bg-[var(--jmq-surface)] px-2 py-1.5 text-xs text-[var(--jmq-text)]"
        />
      </div>

      <div className="jmq-card mb-4">
        <div className="jmq-card-title">Coverage % by state (click a bar)</div>
        <p className="jmq-card-sub">States sorted {view === 'best' ? 'best' : 'worst'} first in chart below.</p>
        <div className="h-56 w-full sm:h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="horizontal"
              margin={{ top: 8, right: 12, bottom: 48, left: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--jmq-border)" />
              <XAxis dataKey="state_code" tick={{ fontSize: 10, fill: 'var(--jmq-text-muted)' }} interval={0} angle={-40} textAnchor="end" height={50} />
              <YAxis
                domain={[0, 100]}
                tickFormatter={(v) => `${v}%`}
                tick={{ fontSize: 10, fill: 'var(--jmq-text-muted)' }}
                width={44}
                label={{
                  value: AXIS_LABEL_PCT_WITH_PRIMARY_URL,
                  angle: -90,
                  position: 'insideLeft',
                  offset: 4,
                  fill: 'var(--jmq-text-muted)',
                  fontSize: 11,
                  fontWeight: 600,
                }}
              />
              <Tooltip
                formatter={(v: number) => [`${Number(v).toFixed(1)}%`, AXIS_LABEL_PCT_WITH_PRIMARY_URL]}
                contentStyle={{ background: 'var(--jmq-surface2)', border: '1px solid var(--jmq-border)', fontSize: 12 }}
              />
              <Bar dataKey="pct" name={AXIS_LABEL_PCT_WITH_PRIMARY_URL} radius={[3, 3, 0, 0]} cursor="pointer" onClick={setDrillFromBar}>
                {chartData.map((d, i) => (
                  <Cell key={i} fill={barColor(d.pct)} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="jmq-card mb-4">
        <div className="jmq-card-title">Missing URL volume — top 15 states</div>
        <p className="jmq-card-sub">Click a bar to open unmapped sample for that state.</p>
        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={[...enriched].sort((a, b) => b.missing - a.missing).slice(0, 15)}
              margin={{ top: 8, right: 12, bottom: 36, left: 8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--jmq-border)" />
              <XAxis
                type="number"
                tickFormatter={(v) => fmt(v)}
                tick={{ fontSize: 10, fill: 'var(--jmq-text-muted)' }}
                label={{
                  value: 'Without primary URL (count)',
                  position: 'insideBottom',
                  offset: -2,
                  fill: 'var(--jmq-text-muted)',
                  fontSize: 11,
                  fontWeight: 600,
                }}
              />
              <YAxis
                type="category"
                dataKey="state_code"
                width={40}
                tick={{ fontSize: 10, fill: 'var(--jmq-text-muted)' }}
                label={{
                  value: 'State',
                  angle: 0,
                  position: 'insideLeft',
                  offset: 6,
                  fill: 'var(--jmq-text-muted)',
                  fontSize: 11,
                  fontWeight: 600,
                }}
              />
              <Tooltip contentStyle={{ background: 'var(--jmq-surface2)', border: '1px solid var(--jmq-border)' }} />
              <Bar dataKey="missing" name="Missing" radius={[0, 4, 4, 0]} cursor="pointer" onClick={setDrillFromBar}>
                {[...enriched]
                  .sort((a, b) => b.missing - a.missing)
                  .slice(0, 15)
                  .map((d, i) => (
                    <Cell key={i} fill={barColor(d.pct)} fillOpacity={0.85} />
                  ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="jmq-card">
        <div className="jmq-card-title">
          {search ? `Search: “${search}”` : view === 'worst' ? '15 lowest coverage' : view === 'best' ? '15 highest coverage' : 'All states'}
        </div>
        <p className="jmq-card-sub">Click column headers to sort. Use ↗ to drill when missing &gt; 0.</p>
        <div className="jmq-tbl-wrap mt-2">
          <table className="jmq-dt text-xs">
            <thead>
              <tr>
                {(
                  [
                    { k: null, l: '#' },
                    { k: 'state_code', l: 'St' },
                    { k: null, l: 'Name' },
                    { k: 'total_jurisdictions', l: 'Total' },
                    { k: null, l: 'With URL' },
                    { k: 'pct', l: 'Cov %' },
                    { k: 'missing', l: 'Missing' },
                    { k: null, l: 'Drill' },
                  ] as { k: 'pct' | 'missing' | 'total_jurisdictions' | 'state_code' | null; l: string }[]
                ).map(({ k, l }) => (
                  <th
                    key={l}
                    className={`${k ? 'cursor-pointer select-none' : ''} ${sortCol === k ? 'text-[var(--jmq-teal)]' : ''}`}
                    onClick={k ? () => toggleSort(k) : undefined}
                  >
                    {l}
                    {k ? <span className="ml-1 opacity-60">{sortCol === k ? (sortDir === 'asc' ? '↑' : '↓') : '↕'}</span> : null}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((r, i) => {
                const rank = !search && view !== 'all' ? i + 1 : null
                return (
                  <tr key={r.state_code}>
                    <td className="font-mono text-[10px] text-[var(--jmq-text-muted)]">{rank ? `#${rank}` : ''}</td>
                    <td className="font-mono font-semibold">{r.state_code}</td>
                    <td>{r.name}</td>
                    <td className="jmq-dt-num tabular-nums">{fmt(r.total_jurisdictions)}</td>
                    <td className="jmq-dt-num tabular-nums" style={{ color: barColor(r.pct) }}>
                      {fmt(r.with_primary_website)}
                    </td>
                    <td>
                      <CovBarLite pct={r.pct} width={72} />
                    </td>
                    <td className="jmq-dt-num font-mono">{fmt(r.missing)}</td>
                    <td>
                      {r.missing > 0 ? (
                        <button
                          type="button"
                          className="rounded border border-[var(--jmq-red)] bg-[var(--jmq-red-dim)] px-2 py-0.5 font-mono text-[10px] text-[var(--jmq-red)] hover:opacity-90"
                          onClick={() => setDrill(r)}
                        >
                          ↗ {fmt(r.missing)}
                        </button>
                      ) : (
                        <span className="text-[var(--jmq-green)] font-mono text-[10px]">✓</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function SectionTable({
  rows,
  onDrillMissing,
}: {
  rows: { bucket: string; n: number; withUrl: number; pct: number; missing: number }[]
  onDrillMissing: (bucket: string) => void
}) {
  const data = rows.filter((r) => r.n > 0)
  return (
    <table className="jmq-dt w-full text-xs">
      <thead>
        <tr>
          {['Bucket', 'In bucket', 'With URL', 'Coverage', 'Missing', 'Drill'].map((h) => (
            <th key={h}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((r) => (
          <tr key={r.bucket}>
            <td className="font-semibold text-[var(--jmq-text)]">{r.bucket}</td>
            <td className="font-mono text-[var(--jmq-text-muted)]">{fmt(r.n)}</td>
            <td className="font-mono" style={{ color: barColor(r.pct) }}>
              {fmt(r.withUrl)}
            </td>
            <td>
              <CovBarLite pct={r.pct} width={90} />
            </td>
            <td className="font-mono text-[var(--jmq-red)]">{fmt(r.missing)}</td>
            <td>
              {r.missing > 0 ? (
                <button
                  type="button"
                  className="rounded border border-[var(--jmq-red)] bg-[var(--jmq-red-dim)] px-2 py-0.5 font-mono text-[10px]"
                  onClick={() => onDrillMissing(r.bucket)}
                >
                  ↗
                </button>
              ) : (
                <span className="text-[var(--jmq-green)] text-[10px]">✓</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function EntityQualityDashboard({
  data,
  refreshOpen,
  setRefreshOpen,
}: {
  data: QualityPayload
  refreshOpen: boolean
  setRefreshOpen: (v: boolean | ((b: boolean) => boolean)) => void
}) {
  const [entity, setEntity] = useState<EntityKey>('cities')
  const [section, setSection] = useState<'overview' | 'population' | 'income'>('overview')
  type BucketDrill =
    | { field: 'acs_population_tier'; value: string }
    | { field: 'acs_income_level'; value: string }
  const [bucketDrill, setBucketDrill] = useState<BucketDrill | null>(null)
  const [mappedIssuesOpen, setMappedIssuesOpen] = useState(false)

  const location = useLocation()
  const navigate = useNavigate()
  const prevEntityRef = useRef(entity)

  useEffect(() => {
    if (location.hash === '#state') setEntity('state')
  }, [location.hash])

  useEffect(() => {
    if (prevEntityRef.current === 'state' && entity !== 'state' && location.hash === '#state') {
      navigate({ pathname: location.pathname, search: location.search, hash: '' }, { replace: true })
    }
    prevEntityRef.current = entity
  }, [entity, location.hash, location.pathname, location.search, navigate])

  const summaryByType = data.summary_by_type ?? []
  const muniRows = data.summary_municipality_by_place_kind ?? []
  const popRowsAll = data.summary_by_acs_population_tier ?? []
  const incRowsAll = data.summary_by_acs_income_level ?? []
  const drill = data.drilldown
  const unmapped = drill?.unmapped ?? []
  const mappedIssues = drill?.mapped_url_issues ?? []

  const metrics = useMemo(() => entityMetrics(entity, summaryByType, muniRows), [entity, summaryByType, muniRows])
  const touchForPie = useMemo(() => {
    if (entity === 'state') return entityMetrics('state', summaryByType, muniRows).touch as SummaryRow | null
    if (entity === 'cities') return muniRows.find((x) => x.municipality_place_kind === 'incorporated_city') ?? null
    if (entity === 'towns') {
      const agg = aggregateMuniKinds(muniRows, ['incorporated_other', 'unknown', 'census_designated_place'])
      return {
        jurisdictions_touching_naco: agg.touch.jurisdictions_touching_naco,
        jurisdictions_touching_uscm: agg.touch.jurisdictions_touching_uscm,
        jurisdictions_touching_nces: agg.touch.jurisdictions_touching_nces,
        jurisdictions_touching_gsa: agg.touch.jurisdictions_touching_gsa,
        jurisdictions_touching_override: agg.touch.jurisdictions_touching_override,
      } as MunicipalityPlaceSummaryRow
    }
    return (summaryByType.find((x) => x.jurisdiction_type === (entity === 'counties' ? 'county' : 'school_district')) ??
      null) as SummaryRow | null
  }, [entity, summaryByType, muniRows])

  const pieData = useMemo(() => sourcePie(touchForPie, entity), [touchForPie, entity])

  const acsJurisdictionFilter = entity === 'counties' ? 'county' : entity === 'schools' ? 'school_district' : 'municipality'

  const popTableRows = useMemo(() => {
    return popRowsAll
      .filter((r) => r.jurisdiction_type === acsJurisdictionFilter)
      .map((r) => {
        const n = Number(r.total_jurisdictions)
        const w = Number(r.with_primary_website)
        const pct = r.pct_with_primary_website != null ? Number(r.pct_with_primary_website) : n > 0 ? (100 * w) / n : 0
        return { bucket: r.acs_population_tier, n, withUrl: w, pct, missing: Math.max(0, n - w) }
      })
  }, [popRowsAll, acsJurisdictionFilter])

  const incTableRows = useMemo(() => {
    return incRowsAll
      .filter((r) => r.jurisdiction_type === acsJurisdictionFilter)
      .map((r) => {
        const n = Number(r.total_jurisdictions)
        const w = Number(r.with_primary_website)
        const pct = r.pct_with_primary_website != null ? Number(r.pct_with_primary_website) : n > 0 ? (100 * w) / n : 0
        return { bucket: r.acs_income_level, n, withUrl: w, pct, missing: Math.max(0, n - w) }
      })
  }, [incRowsAll, acsJurisdictionFilter])

  const popChartData = popTableRows.filter((r) => r.n > 0)
  const incChartData = incTableRows.filter((r) => r.n > 0)

  const rollup = useMemo(() => {
    const roll = data.entity_state_rollup
    if (!roll) return []
    if (entity === 'state') return mergeStateRollups(roll)
    return roll[ENTITY_ROLLUP_KEY[entity]] ?? []
  }, [data.entity_state_rollup, entity])

  const insight = useMemo(() => {
    const { total, withUrl, pct } = metrics
    const miss = total - withUrl
    if (entity === 'towns')
      return `${fmt(miss)} incorporated towns/CDPs/unknown-LSAD rows still lack a primary URL (${(100 - pct).toFixed(1)}% gap). GSA seeds only part of the long tail — new municipal sources are the lever.`
    if (entity === 'cities')
      return `Incorporated cities sit near ${pct.toFixed(1)}% coverage. USCM + GSA still miss ${fmt(miss)} cities — mostly smaller places outside directory coverage.`
    if (entity === 'counties')
      return `Counties are the best-covered class in most snapshots (~${pct.toFixed(1)}%). Remaining ${fmt(miss)} gaps skew rural / edge cases.`
    if (entity === 'state')
      return `All jurisdiction types combined (~${pct.toFixed(1)}% with a primary URL). ${fmt(miss)} still lack one — use the state chart below, then pick a type tile for ACS or source detail.`
    return `School districts are NCES-driven (~${pct.toFixed(1)}%). ${fmt(miss)} districts still lack a warehouse primary; URL-shape flags are counted separately.`
  }, [entity, metrics])

  const bucketUnmappedResult = useMemo(() => {
    if (!bucketDrill) return { rows: [] as UnmappedDrillRow[], bannerExtra: null as string | null }
    const base = unmapped.filter((r) => matchesEntityUnmapped(entity, r))
    const key = bucketDrill.field
    const val = bucketDrill.value
    const strict = base.filter((r) => String(r[key] ?? '') === val)
    if (strict.length > 0) return { rows: strict.slice(0, 80), bannerExtra: null }
    const tail = base.slice(0, 60)
    if (tail.length === 0) {
      return {
        rows: [],
        bannerExtra:
          'No unmapped rows for this entity appear in the exported sample (raise JURIS_MAPPING_QUALITY_UNMAPPED_CAP and re-export, or query Postgres).',
      }
    }
    return {
      rows: tail,
      bannerExtra: `No rows in this sample matched “${val}” on ${key}. Showing ${tail.length} unmapped ${ENTITY_META[entity].label.toLowerCase()} rows from the export sample instead.`,
    }
  }, [bucketDrill, unmapped, entity])

  const syntaxIssueRows = useMemo(() => {
    if (entity !== 'schools') return []
    return mappedIssues.filter((r) => r.jurisdiction_type === 'school_district').slice(0, 40)
  }, [mappedIssues, entity])

  const hasAcs = popRowsAll.length > 0 || incRowsAll.length > 0

  return (
    <div className="jmq-main pb-16">
      {/* top-16 + z-40: align with Layout main pt-16; stay below global fixed header (z-50) when scrolling */}
      <header className="sticky top-16 z-40 mb-6 border-b border-[var(--jmq-border)] bg-[var(--jmq-surface)] py-4 shadow-md [isolation:isolate]">
        <div className="jmq-header !border-b-0 !px-0 !py-0">
          <Link
            to={`${DATA_EXPLORER_MAP_BASE}/us/2024/median_household_income`}
            className="order-last inline-flex shrink-0 items-center gap-1.5 font-mono text-xs font-semibold text-[var(--jmq-teal)] hover:opacity-90 sm:order-none"
          >
            <ArrowLeftIcon className="h-3.5 w-3.5" />
            Map
          </Link>
          <div className="jmq-logo">C1</div>
          <div className="min-w-0">
            <div className="jmq-hdr-title">Open Navigator — Data Quality</div>
            <div className="font-mono text-[11px] text-[var(--jmq-text-muted)]">
              jurisdiction_mapping_quality.json · NACo / USCM / NCES / GSA
            </div>
          </div>
          <div className="jmq-hdr-sub hidden flex-wrap justify-end gap-2 lg:flex">
            <span className="rounded border border-[var(--jmq-border)] bg-[var(--jmq-surface2)] px-2 py-0.5 font-mono text-[10px]">
              {hasAcs ? 'ACS in JSON' : 'ACS empty'}
            </span>
            <span className="rounded border border-[var(--jmq-border)] px-2 py-0.5 font-mono text-[10px] text-[var(--jmq-text-muted)]">
              Snapshot
            </span>
          </div>
        </div>
        {entity !== 'state' ? (
        <nav
          className="mt-3 flex flex-wrap items-center gap-1 border-t border-[var(--jmq-border)] pt-3"
          aria-label="Dashboard sections"
        >
          {(
            [
              ['overview', 'Overview'],
              ['population', 'By population'],
              ['income', 'By income'],
            ] as const
          ).map(([id, lbl]) => (
            <button
              key={id}
              type="button"
              onClick={() => {
                setSection(id)
                if (location.hash === '#state') {
                  navigate({ pathname: location.pathname, search: location.search, hash: '' }, { replace: true })
                }
              }}
              className={`rounded-t-md border border-b-0 px-3 py-2 text-xs font-medium ${
                section === id
                  ? 'border-[var(--jmq-border)] bg-[var(--jmq-surface)] text-[var(--jmq-teal)]'
                  : 'border-transparent text-[var(--jmq-text-muted)] hover:text-[var(--jmq-text)]'
              }`}
            >
              {lbl}
            </button>
          ))}
          {entity === 'schools' && mappedIssues.length > 0 ? (
            <button
              type="button"
              className="ml-auto self-center rounded border border-[var(--jmq-amber)] bg-[var(--jmq-amber-dim)] px-2 py-1 font-mono text-[11px] text-[#4d2d00]"
              onClick={() => setMappedIssuesOpen(true)}
            >
              URL shape sample ({syntaxIssueRows.length})
            </button>
          ) : null}
        </nav>
        ) : null}
      </header>

      {bucketDrill ? (
        <DrillPanel
          rows={bucketUnmappedResult.rows}
          title="Unmapped sample"
          subtitle={`${ENTITY_META[entity].label} · ${bucketDrill.value} (${bucketDrill.field})`}
          bannerExtra={bucketUnmappedResult.bannerExtra}
          onClose={() => setBucketDrill(null)}
        />
      ) : null}

      {mappedIssuesOpen ? (
        <div
          className="fixed inset-0 z-[200] flex items-start justify-end bg-black/40 p-4"
          role="dialog"
          aria-modal
        >
          <div className="flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-xl border border-[var(--jmq-border)] bg-[var(--jmq-surface)] shadow-2xl">
            <div className="flex items-center justify-between border-b border-[var(--jmq-border)] px-4 py-3">
              <div className="text-sm font-bold text-[var(--jmq-text)]">Mapped URL static-check sample (school districts)</div>
              <button
                type="button"
                className="rounded-md border border-[var(--jmq-border)] bg-[var(--jmq-surface2)] px-2 py-1 text-xs"
                onClick={() => setMappedIssuesOpen(false)}
              >
                ✕ Close
              </button>
            </div>
            <div className="overflow-auto p-2">
              {syntaxIssueRows.length === 0 ? (
                <p className="p-6 text-center text-sm text-[var(--jmq-text-muted)]">No school-district rows in mapped_url_issues sample.</p>
              ) : (
                <table className="jmq-dt w-full text-[11px]">
                  <thead>
                    <tr>
                      {['State', 'Name', 'Source', 'URL', 'Flags'].map((h) => (
                        <th key={h}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {syntaxIssueRows.map((r) => (
                      <tr key={r.jurisdiction_id}>
                        <td className="font-mono">{r.state_code}</td>
                        <td>{r.name}</td>
                        <td className="font-mono">{r.primary_website_source ?? '—'}</td>
                        <td className="max-w-[14rem] break-all font-mono text-[10px]">{r.primary_website_url ?? '—'}</td>
                        <td className="font-mono text-[10px] text-[var(--jmq-red)]">
                          {[
                            r.primary_url_syntax_ok === false && 'syntax',
                            r.primary_url_likely_wrong_host && 'host',
                            r.primary_url_passes_basic_checks === false && 'basic',
                          ]
                            .filter(Boolean)
                            .join(' · ') || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      ) : null}

      <div className="mb-6 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
        {(Object.keys(ENTITY_META) as EntityKey[]).map((ek) => {
          const m = entityMetrics(ek, summaryByType, muniRows)
          const active = entity === ek
          return (
            <button
              key={ek}
              type="button"
              onClick={() => {
                setEntity(ek)
                if (ek === 'state') {
                  navigate({ pathname: location.pathname, search: location.search, hash: 'state' }, { replace: true })
                  return
                }
                setSection('overview')
                if (location.hash === '#state') {
                  navigate({ pathname: location.pathname, search: location.search, hash: '' }, { replace: true })
                }
              }}
              className={`rounded-[10px] border p-3 text-left transition-colors ${
                active ? 'border-[var(--jmq-teal)] bg-[var(--jmq-surface)] shadow-sm' : 'border-[var(--jmq-border)] bg-[var(--jmq-surface2)] hover:bg-[#e6eaef]'
              }`}
            >
              <div className="mb-2 flex items-center gap-2">
                <span className="text-lg">{ENTITY_META[ek].icon}</span>
                <span className={`text-[13px] font-bold ${active ? 'text-[var(--jmq-teal)]' : 'text-[var(--jmq-text-muted)]'}`}>
                  {ENTITY_META[ek].label}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-1 flex-1 overflow-hidden rounded bg-[var(--jmq-border)]">
                  <div className="h-full rounded" style={{ width: `${Math.min(100, m.pct)}%`, background: barColor(m.pct) }} />
                </div>
                <span className="font-mono text-xs font-bold" style={{ color: barColor(m.pct) }}>
                  {m.pct.toFixed(1)}%
                </span>
              </div>
              <div className="mt-1 font-mono text-[10px] text-[var(--jmq-text-muted)]">coverage · {fmt(m.withUrl)} / {fmt(m.total)}</div>
            </button>
          )
        })}
      </div>

      <div className="mb-5 grid grid-cols-2 gap-2 sm:grid-cols-5">
        {[
          { label: 'Total', val: fmt(metrics.total), c: 'var(--jmq-text-muted)' },
          { label: 'With URL', val: fmt(metrics.withUrl), c: 'var(--jmq-teal)' },
          { label: 'Coverage', val: `${metrics.pct.toFixed(1)}%`, c: barColor(metrics.pct) },
          { label: 'Missing', val: fmt(Math.max(0, metrics.total - metrics.withUrl)), c: metrics.total - metrics.withUrl > 5000 ? '#a40e26' : '#9a6700' },
          { label: 'Syntax gaps†', val: fmt(metrics.syntaxErr), c: metrics.syntaxErr > 0 ? '#9a6700' : 'var(--jmq-green)' },
        ].map((k) => (
          <div key={k.label} className="jmq-kpi jmq-kpi--info relative overflow-hidden rounded-lg border border-[var(--jmq-border)] bg-[var(--jmq-surface)] p-3">
            <div className="absolute left-0 right-0 top-0 h-0.5" style={{ background: k.c }} />
            <div className="jmq-kpi-label !mb-1">{k.label}</div>
            <div className="font-mono text-xl font-extrabold leading-tight" style={{ color: k.c }}>
              {k.val}
            </div>
          </div>
        ))}
      </div>
      <p className="mb-4 font-mono text-[10px] text-[var(--jmq-text-muted)]">
        † Among rows with a primary URL: jurisdictions failing static syntax vs counted “syntax OK” in summary tables.
      </p>

      {entity === 'state' ? (
        <div className="space-y-4">
          <div className="grid gap-3 lg:grid-cols-[1fr_200px]">
            <div className="rounded-lg border border-[var(--jmq-teal)]/30 bg-[var(--jmq-teal-dim)] px-4 py-3 text-sm leading-relaxed text-[var(--jmq-text)]">
              <span className="font-bold text-[var(--jmq-teal)]">Insight · </span>
              {insight}
            </div>
            <div className="jmq-card !py-3">
              <div className="mb-2 font-mono text-[10px] font-semibold uppercase text-[var(--jmq-text-muted)]">Sources touched (combined)</div>
              <div className="flex flex-col gap-1">
                {ENTITY_META.state.sourceKeys.map((s) => (
                  <span key={s} className={sourceBadgeClass(s)}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
          {rollup.length === 0 ? (
            <div className="jmq-placeholder">
              <strong>No state rollup in JSON</strong>
              Re-run <code>export_jurisdiction_mapping_quality_json.py</code> after updating the repo to populate{' '}
              <code>entity_state_rollup</code>.
            </div>
          ) : (
            <StateAnalysisSection entity={entity} rollup={rollup} unmapped={unmapped} />
          )}
        </div>
      ) : (
        <>
      {section === 'overview' && (
        <div className="space-y-4">
          <div className="grid gap-3 lg:grid-cols-[1fr_200px]">
            <div className="rounded-lg border border-[var(--jmq-teal)]/30 bg-[var(--jmq-teal-dim)] px-4 py-3 text-sm leading-relaxed text-[var(--jmq-text)]">
              <span className="font-bold text-[var(--jmq-teal)]">Insight · </span>
              {insight}
            </div>
            <div className="jmq-card !py-3">
              <div className="mb-2 font-mono text-[10px] font-semibold uppercase text-[var(--jmq-text-muted)]">Sources touched</div>
              <div className="flex flex-col gap-1">
                {ENTITY_META[entity].sourceKeys.map((s) => (
                  <span key={s} className={sourceBadgeClass(s)}>
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="grid gap-3 lg:grid-cols-3">
            <div className="jmq-card">
              <div className="jmq-card-title">By population (ACS)</div>
              <p className="jmq-card-sub">{acsJurisdictionFilter === 'municipality' ? 'All municipalities — not split by city vs town in ACS mart.' : ''}</p>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={popChartData} margin={{ top: 8, right: 8, bottom: 28, left: 12 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--jmq-border)" />
                    <XAxis dataKey="bucket" tick={{ fontSize: 8, fill: 'var(--jmq-text-muted)' }} angle={-20} textAnchor="end" interval={0} height={48} />
                    <YAxis
                      domain={[0, 100]}
                      tickFormatter={(v) => `${v}%`}
                      tick={{ fontSize: 9, fill: 'var(--jmq-text-muted)' }}
                      width={44}
                      label={{
                        value: AXIS_LABEL_PCT_WITH_PRIMARY_URL,
                        angle: -90,
                        position: 'insideLeft',
                        offset: 2,
                        fill: 'var(--jmq-text-muted)',
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    />
                    <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, AXIS_LABEL_PCT_WITH_PRIMARY_URL]} />
                    <Bar dataKey="pct" name={AXIS_LABEL_PCT_WITH_PRIMARY_URL} radius={[3, 3, 0, 0]}>
                      {popChartData.map((d, i) => (
                        <Cell key={i} fill={barColor(d.pct)} fillOpacity={0.85} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="jmq-card">
              <div className="jmq-card-title">By income (ACS)</div>
              <p className="jmq-card-sub"> </p>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={incChartData} margin={{ top: 8, right: 8, bottom: 8, left: 12 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--jmq-border)" />
                    <XAxis dataKey="bucket" tick={{ fontSize: 9, fill: 'var(--jmq-text-muted)' }} />
                    <YAxis
                      tickFormatter={(v) => `${v}%`}
                      tick={{ fontSize: 9, fill: 'var(--jmq-text-muted)' }}
                      width={44}
                      label={{
                        value: AXIS_LABEL_PCT_WITH_PRIMARY_URL,
                        angle: -90,
                        position: 'insideLeft',
                        offset: 2,
                        fill: 'var(--jmq-text-muted)',
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    />
                    <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, AXIS_LABEL_PCT_WITH_PRIMARY_URL]} />
                    <Bar dataKey="pct" radius={[3, 3, 0, 0]}>
                      {incChartData.map((d, i) => (
                        <Cell key={i} fill={barColor(d.pct)} fillOpacity={0.85} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="jmq-card">
              <div className="jmq-card-title">Directory reach (distinct jurisdictions)</div>
              <p className="jmq-card-sub">Global candidate rows — not per-entity exclusive</p>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={40} outerRadius={68} paddingAngle={2}>
                      {pieData.map((_, i) => (
                        <Cell key={i} fill={pieData[i].fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 10 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}

      {section === 'population' && (
        <div className="jmq-card">
          <div className="jmq-card-title">Population buckets</div>
          <p className="jmq-card-sub">Drill uses capped unmapped list filtered by ACS tier when present.</p>
          <SectionTable rows={popTableRows} onDrillMissing={(b) => setBucketDrill({ field: 'acs_population_tier', value: b })} />
        </div>
      )}

      {section === 'income' && (
        <div className="jmq-card">
          <div className="jmq-card-title">Income buckets</div>
          <p className="jmq-card-sub">Drill uses capped unmapped list filtered by ACS income when present.</p>
          <SectionTable rows={incTableRows} onDrillMissing={(b) => setBucketDrill({ field: 'acs_income_level', value: b })} />
        </div>
      )}

        </>
      )}

      <div className="jmq-refresh mt-10">
        <button
          type="button"
          className="jmq-refresh-toggle"
          onClick={() => setRefreshOpen((o) => !o)}
          aria-expanded={refreshOpen}
        >
          <span>Refresh this dashboard</span>
          <ChevronDownIcon className={`h-5 w-5 shrink-0 transition-transform ${refreshOpen ? 'rotate-180' : ''}`} />
        </button>
        {refreshOpen ? (
          <div className="jmq-refresh-panel">
            <div className="jmq-alert jmq-alert--warn">
              <InformationCircleIcon className="jmq-alert-icon h-5 w-5 shrink-0" />
              <ol className="list-inside list-decimal space-y-2 text-sm">
                <li>
                  Build marts:{' '}
                  <code className="text-[11px]">./scripts/dbt.sh run --select jurisdiction_mapping_analysis+</code>
                </li>
                <li>
                  Export:{' '}
                  <code className="text-[11px]">
                    .venv/bin/python scripts/datasources/jurisdictions/export_jurisdiction_mapping_quality_json.py
                  </code>
                </li>
                <li>Hard-refresh this page.</li>
              </ol>
              {data.generated_at ? (
                <p className="mt-2 font-mono text-[11px] text-[var(--jmq-text-muted)]">
                  Generated {data.generated_at}
                  {data.database_host ? ` · ${data.database_host}` : ''}
                </p>
              ) : null}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
