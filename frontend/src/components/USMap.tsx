// @ts-nocheck
import { ComposableMap, Geographies, Geography } from 'react-simple-maps'

const geoUrl = 'https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json'

interface StateData {
  state: string
  total_bills: number
  type_counts: {
    ban: number
    restriction: number
    protection: number
    other: number
  }
  status_counts: {
    enacted: number
    failed: number
    pending: number
  }
  primary_type: string
  primary_status: string
  map_category: string
}

interface USMapProps {
  stateData: Record<string, StateData>
  onStateClick?: (stateCode: string) => void
}

// State code to FIPS mapping
const STATE_FIPS: Record<string, string> = {
  'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
  'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
  'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
  'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
  'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29',
  'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
  'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
  'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
  'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
  'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56',
  'DC': '11', 'PR': '72'
}

const FIPS_STATE: Record<string, string> = Object.fromEntries(
  Object.entries(STATE_FIPS).map(([k, v]) => [v, k])
)

// Color scheme based on the user's description
const getStateColor = (stateCode: string, stateData: Record<string, StateData>): string => {
  const data = stateData[stateCode]
  
  if (!data || data.total_bills === 0) {
    return '#E3F2FD' // Light blue - no legislation
  }
  
  const { primary_type, primary_status } = data
  
  // Base colors by type
  let baseColor = '#E3F2FD' // default light blue
  
  if (primary_type === 'ban') {
    baseColor = '#FF9800' // Orange - Outright Ban
  } else if (primary_type === 'restriction') {
    baseColor = '#FFD54F' // Yellow - Restriction
  } else if (primary_type === 'protection') {
    baseColor = '#1976D2' // Dark Blue - Protection
  }
  
  // Adjust shade based on status
  if (primary_status === 'enacted') {
    // Darker shade for enacted
    if (primary_type === 'ban') return '#F57C00'
    if (primary_type === 'restriction') return '#FBC02D'
    if (primary_type === 'protection') return '#1565C0'
  } else if (primary_status === 'failed') {
    // Lighter shade for failed
    if (primary_type === 'ban') return '#FFB74D'
    if (primary_type === 'restriction') return '#FFF176'
    if (primary_type === 'protection') return '#42A5F5'
  }
  
  return baseColor
}

const getPatternForState = (stateCode: string, stateData: Record<string, StateData>): string | null => {
  const data = stateData[stateCode]
  
  if (!data || data.total_bills === 0) {
    return null
  }
  
  const { primary_status } = data
  
  if (primary_status === 'failed') {
    return 'crosshatch'
  } else if (primary_status === 'enacted') {
    return 'diagonal'
  }
  
  return null
}

export default function USMap({ stateData, onStateClick }: USMapProps) {
  return (
    <div className="relative">
      {/* SVG Patterns for overlays */}
      <svg width="0" height="0">
        <defs>
          {/* Crosshatch pattern for failed */}
          <pattern id="crosshatch" width="10" height="10" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="10" y2="10" stroke="#000" strokeWidth="1" opacity="0.3" />
            <line x1="10" y1="0" x2="0" y2="10" stroke="#000" strokeWidth="1" opacity="0.3" />
          </pattern>
          
          {/* Diagonal stripes for enacted */}
          <pattern id="diagonal" width="10" height="10" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="10" y2="10" stroke="#000" strokeWidth="2" opacity="0.4" />
          </pattern>
        </defs>
      </svg>
      
      <ComposableMap
        projection="geoAlbersUsa"
        projectionConfig={{
          scale: 1000,
        }}
        className="w-full h-auto"
      >
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const fips = geo.id
              const stateCode = FIPS_STATE[fips] || fips
              const data = stateData[stateCode]
              const pattern = getPatternForState(stateCode, stateData)
              
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={pattern ? `url(#${pattern})` : getStateColor(stateCode, stateData)}
                  stroke="#FFFFFF"
                  strokeWidth={0.5}
                  style={{
                    default: {
                      fill: getStateColor(stateCode, stateData),
                      outline: 'none',
                    },
                    hover: {
                      fill: '#607D8B',
                      outline: 'none',
                      cursor: 'pointer',
                    },
                    pressed: {
                      fill: '#455A64',
                      outline: 'none',
                    },
                  }}
                  onClick={() => onStateClick?.(stateCode)}
                  onMouseEnter={() => {
                    if (data) {
                      // Could trigger tooltip here
                    }
                  }}
                />
              )
            })
          }
        </Geographies>
      </ComposableMap>
      
      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white/95 rounded-lg shadow-lg p-4 border border-gray-200">
        <div className="text-sm font-semibold text-gray-800 mb-3">Legend</div>
        
        {/* Type of Legislation */}
        <div className="mb-3">
          <div className="text-xs font-medium text-gray-600 mb-2">Type of Legislation</div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FF9800' }} />
              <span className="text-xs text-gray-700">Outright Ban</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#FFD54F' }} />
              <span className="text-xs text-gray-700">Restriction</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#1976D2' }} />
              <span className="text-xs text-gray-700">Protection</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded" style={{ backgroundColor: '#E3F2FD' }} />
              <span className="text-xs text-gray-700">No Legislation</span>
            </div>
          </div>
        </div>
        
        {/* Status of Legislation */}
        <div>
          <div className="text-xs font-medium text-gray-600 mb-2">Status</div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-300" style={{ background: 'url(#diagonal)' }} />
              <span className="text-xs text-gray-700">Enacted</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-300" style={{ background: 'url(#crosshatch)' }} />
              <span className="text-xs text-gray-700">Failed</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-300 bg-white" />
              <span className="text-xs text-gray-700">Pending</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
