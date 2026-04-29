// @ts-nocheck
import { useState } from 'react'
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
  legend?: {
    types: Record<string, string>
    statuses: Record<string, string>
  }
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

// Flexible color palette for different legislation types
const TYPE_COLOR_PALETTE: Record<string, string> = {
  // Fluoridation categories
  'mandate': '#4CAF50',      // Green - Mandate
  'removal': '#F44336',      // Red - Removal
  'funding': '#2196F3',      // Blue - Funding
  'study': '#9C27B0',        // Purple - Study
  
  // Dental/Oral Health categories  
  'coverage_expansion': '#4CAF50',  // Green - Expansion
  'screening': '#FF9800',          // Orange - Screening
  'provider_access': '#2196F3',    // Blue - Provider Access
  
  // Medicaid categories
  'expansion': '#4CAF50',     // Green - Expansion
  'coverage': '#2196F3',      // Blue - Coverage
  'reimbursement': '#FF9800', // Orange - Reimbursement
  'eligibility': '#9C27B0',   // Purple - Eligibility
  
  // Education categories
  'requirement': '#FF9800',   // Orange - Requirement
  'curriculum': '#2196F3',    // Blue - Curriculum
  'reform': '#9C27B0',        // Purple - Reform
  
  // Health/General categories
  'protection': '#4CAF50',    // Green - Protection
  'restriction': '#F44336',   // Red - Restriction
  
  // Generic categories
  'support': '#4CAF50',       // Green - Support
  'oppose': '#F44336',        // Red - Oppose
  'regulate': '#FF9800',      // Orange - Regulate
  
  // Shared
  'funding': '#2196F3',       // Blue - Funding (appears in multiple)
  'other': '#9E9E9E',         // Gray - Other
}

// Get color for any category with fallback
const getColorForCategory = (category: string): string => {
  return TYPE_COLOR_PALETTE[category] || '#9E9E9E' // Default to gray
}

// Color scheme based on the user's description
const getStateColor = (stateCode: string, stateData: Record<string, StateData>): string => {
  const data = stateData[stateCode]
  
  if (!data || data.total_bills === 0) {
    return '#E3F2FD' // Light blue - no legislation
  }
  
  const { primary_type, primary_status } = data
  
  // Get base color for this type
  let baseColor = getColorForCategory(primary_type)
  
  // Adjust shade based on status
  if (primary_status === 'enacted') {
    // Slightly darker for enacted (reduce lightness)
    return adjustColorBrightness(baseColor, -20)
  } else if (primary_status === 'failed') {
    // Lighter for failed (increase lightness)
    return adjustColorBrightness(baseColor, 40)
  }
  
  return baseColor
}

// Helper to adjust color brightness
const adjustColorBrightness = (hex: string, percent: number): string => {
  // Simple brightness adjustment
  const num = parseInt(hex.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = (num >> 16) + amt
  const G = (num >> 8 & 0x00FF) + amt
  const B = (num & 0x0000FF) + amt
  
  return '#' + (
    0x1000000 +
    (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
    (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
    (B < 255 ? (B < 1 ? 0 : B) : 255)
  ).toString(16).slice(1).toUpperCase()
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

export default function USMap({ stateData, onStateClick, legend }: USMapProps) {
  const [hoveredState, setHoveredState] = useState<string | null>(null)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })
  
  // Get unique types from actual state data if legend not provided
  const legislationTypes = legend?.types || {}
  const legislationStatuses = legend?.statuses || {
    'enacted': 'Enacted',
    'failed': 'Failed', 
    'pending': 'Pending'
  }
  
  const handleMouseEnter = (event: any, stateCode: string) => {
    setHoveredState(stateCode)
    const bounds = event.target.getBoundingClientRect()
    setTooltipPosition({
      x: bounds.left + bounds.width / 2,
      y: bounds.top
    })
  }
  
  const handleMouseLeave = () => {
    setHoveredState(null)
  }
  
  const hoveredData = hoveredState ? stateData[hoveredState] : null
  
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
                  onMouseEnter={(event) => handleMouseEnter(event, stateCode)}
                  onMouseLeave={handleMouseLeave}
                />
              )
            })
          }
        </Geographies>
      </ComposableMap>
      
      {/* Tooltip */}
      {hoveredState && hoveredData && (
        <div 
          className="fixed z-50 pointer-events-none"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y - 10}px`,
            transform: 'translate(-50%, -100%)'
          }}
        >
          <div className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-xl max-w-xs">
            <div className="font-bold text-base mb-2">{hoveredState}</div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between gap-4">
                <span className="text-gray-300">Total Bills:</span>
                <span className="font-semibold">{hoveredData.total_bills.toLocaleString()}</span>
              </div>
              
              {hoveredData.total_bills > 0 && (
                <>
                  <div className="border-t border-gray-700 my-2 pt-2">
                    <div className="text-gray-300 text-xs mb-1">Primary Type:</div>
                    <div className="font-semibold">
                      {legislationTypes[hoveredData.primary_type] || hoveredData.primary_type}
                    </div>
                  </div>
                  
                  <div className="flex justify-between gap-4">
                    <span className="text-gray-300">Status:</span>
                    <span className="font-semibold capitalize">{hoveredData.primary_status}</span>
                  </div>
                  
                  <div className="border-t border-gray-700 my-2 pt-2">
                    <div className="text-gray-300 text-xs mb-1">Breakdown:</div>
                    <div className="grid grid-cols-2 gap-1 text-xs">
                      <div>✓ Enacted: {hoveredData.status_counts.enacted}</div>
                      <div>⏳ Pending: {hoveredData.status_counts.pending}</div>
                      <div className="col-span-2">✗ Failed: {hoveredData.status_counts.failed}</div>
                    </div>
                  </div>
                </>
              )}
              
              {hoveredData.total_bills === 0 && (
                <div className="text-gray-400 text-xs italic">No legislation found</div>
              )}
            </div>
            
            {/* Tooltip arrow */}
            <div 
              className="absolute left-1/2 bottom-0 transform -translate-x-1/2 translate-y-full"
              style={{
                width: 0,
                height: 0,
                borderLeft: '8px solid transparent',
                borderRight: '8px solid transparent',
                borderTop: '8px solid rgb(17, 24, 39)'
              }}
            />
          </div>
        </div>
      )}
      
      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white/95 rounded-lg shadow-lg p-4 border border-gray-200 max-w-xs">
        <div className="text-sm font-semibold text-gray-800 mb-3">Legend</div>
        
        {/* Type of Legislation - Dynamic based on topic */}
        {Object.keys(legislationTypes).length > 0 && (
          <div className="mb-3">
            <div className="text-xs font-medium text-gray-600 mb-2">Type of Legislation</div>
            <div className="space-y-1">
              {Object.entries(legislationTypes).map(([key, label]) => (
                <div key={key} className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded flex-shrink-0" style={{ backgroundColor: getColorForCategory(key) }} />
                  <span className="text-xs text-gray-700">{label}</span>
                </div>
              ))}
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded flex-shrink-0" style={{ backgroundColor: '#E3F2FD' }} />
                <span className="text-xs text-gray-700">No Legislation</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Status of Legislation */}
        <div>
          <div className="text-xs font-medium text-gray-600 mb-2">Status</div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#666' }} />
              <span className="text-xs text-gray-700">Enacted (darker)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-300 flex-shrink-0 bg-white" />
              <span className="text-xs text-gray-700">Pending (normal)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded border border-gray-300 flex-shrink-0" style={{ backgroundColor: '#ddd' }} />
              <span className="text-xs text-gray-700">Failed (lighter)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
