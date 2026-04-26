import { useState } from 'react'
import { MapPinIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface LocationData {
  address: string
  state: string
  county: string
  city: string
  latitude?: number
  longitude?: number
}

interface AddressLookupProps {
  onLocationFound: (location: LocationData) => void
  initialAddress?: string
  compact?: boolean
}

export default function AddressLookup({ onLocationFound, initialAddress = '', compact = false }: AddressLookupProps) {
  const [address, setAddress] = useState(initialAddress)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [suggestions, setSuggestions] = useState<any[]>([])

  const lookupAddress = async (addressToLookup: string) => {
    if (!addressToLookup.trim()) {
      setError('Please enter an address')
      return
    }

    setIsLoading(true)
    setError(null)
    setSuggestions([])

    try {
      // Use Nominatim (OpenStreetMap) geocoding service
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(addressToLookup)}&` +
        `format=json&` +
        `addressdetails=1&` +
        `countrycodes=us&` +
        `limit=5`,
        {
          headers: {
            'User-Agent': 'CommunityOne-Navigator/1.0'
          }
        }
      )

      if (!response.ok) {
        throw new Error('Failed to lookup address')
      }

      const data = await response.json()

      if (data.length === 0) {
        setError('Address not found. Please try a different address or be more specific.')
        return
      }

      // If we have multiple results, show suggestions
      if (data.length > 1) {
        setSuggestions(data)
        return
      }

      // Single result - process it
      processResult(data[0])
    } catch (err) {
      console.error('Address lookup error:', err)
      setError('Failed to lookup address. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const processResult = (result: any) => {
    const addr = result.address

    const locationData: LocationData = {
      address: result.display_name,
      state: addr.state || '',
      county: addr.county || '',
      city: addr.city || addr.town || addr.village || addr.municipality || '',
      latitude: parseFloat(result.lat),
      longitude: parseFloat(result.lon),
    }

    // Validate we got the essential data
    if (!locationData.state || !locationData.city) {
      setError('Could not determine city and state from this address. Please be more specific.')
      setSuggestions([])
      return
    }

    setSuggestions([])
    onLocationFound(locationData)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    lookupAddress(address)
  }

  const handleSuggestionClick = (suggestion: any) => {
    processResult(suggestion)
  }

  if (compact) {
    return (
      <form onSubmit={handleSubmit} className="w-full">
        <div className="relative">
          <input
            key="address-input-compact"
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Enter your address..."
            className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
            disabled={isLoading}
          />
          <MapPinIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
          <button
            type="submit"
            disabled={isLoading}
            className="absolute right-2 top-1.5 px-3 py-1 text-white rounded-md transition-colors text-sm disabled:opacity-50"
            style={{ backgroundColor: '#354F52' }}
            onMouseEnter={(e) => !isLoading && (e.currentTarget.style.backgroundColor = '#2e4346')}
            onMouseLeave={(e) => !isLoading && (e.currentTarget.style.backgroundColor = '#354F52')}
          >
            {isLoading ? 'Finding...' : 'Find'}
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
      </form>
    )
  }

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
            <span className="flex items-center gap-2">
              <MapPinIcon className="h-5 w-5" />
              Enter Your Address
            </span>
          </label>
          <div className="relative">
            <input
              key="address-input"
              type="text"
              id="address"
              name="addresslookup"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="123 Main St, Los Angeles, CA 90001"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-base text-gray-900"
              disabled={isLoading}
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">
            We'll find your local organizations based on your address
          </p>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full px-6 py-3 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          style={{ backgroundColor: '#354F52' }}
          onMouseEnter={(e) => !isLoading && (e.currentTarget.style.backgroundColor = '#2e4346')}
          onMouseLeave={(e) => !isLoading && (e.currentTarget.style.backgroundColor = '#354F52')}
        >
          {isLoading ? (
            <>
              <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
              <span>Looking up address...</span>
            </>
          ) : (
            <>
              <MagnifyingGlassIcon className="h-5 w-5" />
              <span>Find My Local Government</span>
            </>
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
            <p className="text-sm font-medium text-gray-700">
              Multiple addresses found. Please select one:
            </p>
          </div>
          <div className="divide-y divide-gray-200">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
              >
                <p className="text-sm font-medium text-gray-900">
                  {suggestion.display_name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {suggestion.address.city || suggestion.address.town}, {suggestion.address.state}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
