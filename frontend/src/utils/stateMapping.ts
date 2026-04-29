/**
 * US State name to 2-letter code mapping
 */
export const STATE_NAME_TO_CODE: Record<string, string> = {
  'Alabama': 'AL',
  'Alaska': 'AK',
  'Arizona': 'AZ',
  'Arkansas': 'AR',
  'California': 'CA',
  'Colorado': 'CO',
  'Connecticut': 'CT',
  'Delaware': 'DE',
  'Florida': 'FL',
  'Georgia': 'GA',
  'Hawaii': 'HI',
  'Idaho': 'ID',
  'Illinois': 'IL',
  'Indiana': 'IN',
  'Iowa': 'IA',
  'Kansas': 'KS',
  'Kentucky': 'KY',
  'Louisiana': 'LA',
  'Maine': 'ME',
  'Maryland': 'MD',
  'Massachusetts': 'MA',
  'Michigan': 'MI',
  'Minnesota': 'MN',
  'Mississippi': 'MS',
  'Missouri': 'MO',
  'Montana': 'MT',
  'Nebraska': 'NE',
  'Nevada': 'NV',
  'New Hampshire': 'NH',
  'New Jersey': 'NJ',
  'New Mexico': 'NM',
  'New York': 'NY',
  'North Carolina': 'NC',
  'North Dakota': 'ND',
  'Ohio': 'OH',
  'Oklahoma': 'OK',
  'Oregon': 'OR',
  'Pennsylvania': 'PA',
  'Rhode Island': 'RI',
  'South Carolina': 'SC',
  'South Dakota': 'SD',
  'Tennessee': 'TN',
  'Texas': 'TX',
  'Utah': 'UT',
  'Vermont': 'VT',
  'Virginia': 'VA',
  'Washington': 'WA',
  'West Virginia': 'WV',
  'Wisconsin': 'WI',
  'Wyoming': 'WY',
  'District of Columbia': 'DC',
  'Puerto Rico': 'PR'
}

/**
 * Convert a full state name to its 2-letter code
 * @param stateName - Full state name (e.g., "Massachusetts")
 * @returns 2-letter state code (e.g., "MA") or the original string if not found
 */
export function stateNameToCode(stateName: string): string {
  // If it's already a 2-letter code, return as-is
  if (stateName && stateName.length === 2 && stateName === stateName.toUpperCase()) {
    return stateName
  }
  
  // Try exact match
  if (STATE_NAME_TO_CODE[stateName]) {
    return STATE_NAME_TO_CODE[stateName]
  }
  
  // Try case-insensitive match
  const normalizedName = Object.keys(STATE_NAME_TO_CODE).find(
    key => key.toLowerCase() === stateName.toLowerCase()
  )
  
  if (normalizedName) {
    return STATE_NAME_TO_CODE[normalizedName]
  }
  
  // Return original if not found
  console.warn(`State name "${stateName}" not found in mapping`)
  return stateName
}
