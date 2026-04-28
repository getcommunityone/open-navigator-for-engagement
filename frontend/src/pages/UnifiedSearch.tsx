import { useState, useRef, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { 
  MagnifyingGlassIcon, 
  UserIcon, 
  CalendarIcon,
  BuildingOfficeIcon,
  HeartIcon,
  XMarkIcon,
  AdjustmentsHorizontalIcon,
  CheckIcon
} from '@heroicons/react/24/outline'

interface SearchResult {
  type: 'contact' | 'meeting' | 'organization' | 'cause'
  title: string
  subtitle: string
  description: string
  url: string
  score: number
  metadata: Record<string, any>
}

interface SearchResponse {
  query: string
  total_results: number
  results: {
    contacts: SearchResult[]
    meetings: SearchResult[]
    organizations: SearchResult[]
    causes: SearchResult[]
  }
  pagination: {
    page: number
    limit: number
    offset: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  filters: {
    state?: string
    ntee_code?: string
    types: string[]
  }
}

export default function UnifiedSearch() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Initialize state directly from URL params (lazy initializer for performance)
  const [query, setQuery] = useState(() => searchParams.get('q') || '')
  const [activeQuery, setActiveQuery] = useState(() => searchParams.get('q') || '')
  const [selectedTypes, setSelectedTypes] = useState<string[]>(() => {
    const typesParam = searchParams.get('types')
    if (typesParam) {
      const types = typesParam.split(',').filter(t => 
        ['contacts', 'meetings', 'organizations', 'causes'].includes(t.trim())
      )
      return types.length > 0 ? types : ['contacts', 'meetings', 'organizations', 'causes']
    }
    return ['contacts', 'meetings', 'organizations', 'causes']
  })
  const [selectedState, setSelectedState] = useState(() => searchParams.get('state') || '')
  const [currentPage, setCurrentPage] = useState(() => parseInt(searchParams.get('page') || '1'))
  const [showFilters, setShowFilters] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Initialize from URL parameters on mount
  useEffect(() => {
    const queryParam = searchParams.get('q')
    const stateParam = searchParams.get('state')
    const typesParam = searchParams.get('types')
    const pageParam = searchParams.get('page')
    
    if (queryParam) {
      setQuery(queryParam)
      setActiveQuery(queryParam)
    }
    if (stateParam) {
      setSelectedState(stateParam)
    }
    if (typesParam) {
      const types = typesParam.split(',').filter(t => 
        ['contacts', 'meetings', 'organizations', 'causes'].includes(t.trim())
      )
      if (types.length > 0) {
        setSelectedTypes(types)
      }
    }
    if (pageParam) {
      setCurrentPage(parseInt(pageParam))
    }
  }, [searchParams])

  // Live search preview (type-ahead with actual results)
  const { data: previewResults } = useQuery<SearchResponse>({
    queryKey: ['search-preview', query],
    queryFn: async () => {
      if (!query || query.length < 2) return null
      
      const response = await axios.get('/api/search/', {
        params: {
          q: query,
          types: 'causes,contacts,organizations',
          limit: 3
        }
      })
      return response.data
    },
    enabled: query.length >= 2 && showSuggestions,
    staleTime: 1000 // Cache for 1 second to avoid excessive requests
  })

  // Main search results
  const { data: searchResults, isLoading, error } = useQuery<SearchResponse>({
    queryKey: ['unified-search', activeQuery, selectedTypes, selectedState, currentPage],
    queryFn: async () => {
      // Allow searching with query OR with filters (browse mode)
      if (!activeQuery && !selectedState && !selectedTypes.length) {
        return null
      }
      
      const params: any = {
        types: selectedTypes.join(','),
        limit: 20,
        page: currentPage
      }
      
      // Query is optional - can browse by state/type
      if (activeQuery) {
        params.q = activeQuery
      }
      
      if (selectedState) {
        params.state = selectedState
      }
      
      const response = await axios.get('/api/search/', { params })
      return response.data
    },
    // Enable if we have query OR filters (browse mode)
    enabled: (activeQuery && activeQuery.length >= 2) || selectedState !== '' || selectedTypes.length > 0
  })

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault()
    // Allow search with query OR just filters (browse mode)
    if (query.trim().length >= 2 || selectedState || selectedTypes.length > 0) {
      setActiveQuery(query)
      setShowSuggestions(false)
      setCurrentPage(1) // Reset to first page on new search
      
      // Update URL
      const params: any = {}
      if (query.trim()) params.q = query
      if (selectedState) params.state = selectedState
      if (selectedTypes.length > 0 && selectedTypes.length < 4) {
        params.types = selectedTypes.join(',')
      }
      setSearchParams(params)
    }
  }

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage)
    
    // Update URL
    const params: any = {}
    if (activeQuery) params.q = activeQuery
    if (selectedState) params.state = selectedState
    if (selectedTypes.length > 0 && selectedTypes.length < 4) {
      params.types = selectedTypes.join(',')
    }
    if (newPage > 1) params.page = newPage.toString()
    setSearchParams(params)
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    setActiveQuery(suggestion)
    setShowSuggestions(false)
  }

  const handleViewAllCategory = (category: string) => {
    setActiveQuery(query)
    setShowSuggestions(false)
    setSelectedTypes([category])
    
    // Update URL
    const params: any = { q: query }
    if (selectedState) params.state = selectedState
    params.types = category
    setSearchParams(params)
  }

  const toggleType = (type: string) => {
    if (selectedTypes.includes(type)) {
      setSelectedTypes(selectedTypes.filter(t => t !== type))
    } else {
      setSelectedTypes([...selectedTypes, type])
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'contact':
        return <UserIcon className="h-5 w-5" />
      case 'meeting':
        return <CalendarIcon className="h-5 w-5" />
      case 'organization':
        return <BuildingOfficeIcon className="h-5 w-5" />
      case 'cause':
        return <HeartIcon className="h-5 w-5" />
      default:
        return null
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'contact':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'meeting':
        return 'bg-green-100 text-green-700 border-green-200'
      case 'organization':
        return 'bg-purple-100 text-purple-700 border-purple-200'
      case 'cause':
        return 'bg-pink-100 text-pink-700 border-pink-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const ResultCard = ({ result }: { result: SearchResult }) => (
    <div
      className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg border ${getTypeColor(result.type)}`}>
          {getTypeIcon(result.type)}
        </div>
        
        <div className="flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h3 
                onClick={() => navigate(result.url)}
                className="font-semibold text-gray-900 cursor-pointer hover:text-blue-600 mb-1"
              >
                {result.title}
              </h3>
              <p className="text-sm text-gray-600 mb-2">{result.subtitle}</p>
            </div>
            
            {/* Logo for organizations */}
            {result.type === 'organization' && result.metadata?.logo_url && (
              <img 
                src={result.metadata.logo_url} 
                alt={result.title}
                className="w-12 h-12 rounded object-cover flex-shrink-0"
              />
            )}
          </div>
          
          <p className="text-sm text-gray-500 line-clamp-2 mb-2">{result.description}</p>
          
          {/* Website link for organizations */}
          {result.type === 'organization' && result.metadata?.website && (
            <a
              href={result.metadata.website}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-sm text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center gap-1 mb-2"
            >
              🔗 {result.metadata.website}
            </a>
          )}
          
          {/* Additional metadata for organizations */}
          {result.type === 'organization' && result.metadata && (
            <div className="mt-2 flex flex-wrap gap-2 text-xs">
              {result.metadata.ein && (
                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded">
                  EIN: {result.metadata.ein}
                </span>
              )}
              {result.metadata.revenue && result.metadata.revenue > 0 && (
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded">
                  💰 Revenue: ${(result.metadata.revenue / 1000000).toFixed(1)}M
                </span>
              )}
              {result.metadata.assets && result.metadata.assets > 0 && (
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                  📊 Assets: ${(result.metadata.assets / 1000000).toFixed(1)}M
                </span>
              )}
              {result.metadata.causes && result.metadata.causes.length > 0 && (
                <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                  🏷️ {result.metadata.causes.slice(0, 3).join(', ')}
                </span>
              )}
            </div>
          )}
          
          {/* Type badge */}
          <div className="mt-2">
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(result.type)}`}>
              {getTypeIcon(result.type)}
              {result.type.charAt(0).toUpperCase() + result.type.slice(1)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Search Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Search</h1>
          
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="relative">
            <div className="relative">
              <input
                ref={searchInputRef}
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value)
                  setShowSuggestions(true)
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                placeholder="Search for people, meetings, organizations, causes..."
                className="w-full px-12 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg text-gray-900"
              />
              <MagnifyingGlassIcon className="absolute left-4 top-3.5 h-6 w-6 text-gray-400" />
              
              {query && (
                <button
                  type="button"
                  onClick={() => {
                    setQuery('')
                    setActiveQuery('')
                    searchInputRef.current?.focus()
                  }}
                  className="absolute right-4 top-3.5 text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              )}
            </div>
            
            {/* Rich Preview Dropdown with Grouped Results */}
            {showSuggestions && previewResults && previewResults.total_results > 0 && (
              <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-xl max-h-96 overflow-y-auto">
                
                {/* Causes Section */}
                {previewResults.results.causes.length > 0 && (
                  <div className="border-b border-gray-200">
                    <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <HeartIcon className="h-4 w-4 text-gray-500" />
                        <span className="text-xs font-semibold text-gray-700 uppercase">Causes</span>
                      </div>
                      {previewResults.results.causes.length > 0 && (
                        <button
                          onClick={() => handleViewAllCategory('causes')}
                          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                        >
                          View All
                        </button>
                      )}
                    </div>
                    {previewResults.results.causes.slice(0, 3).map((result, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(result.title)}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-3 transition-colors"
                      >
                        <HeartIcon className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 truncate">{result.title}</div>
                          <div className="text-sm text-gray-600 truncate">{result.subtitle}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* People (Contacts) Section */}
                {previewResults.results.contacts.length > 0 && (
                  <div className="border-b border-gray-200">
                    <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <UserIcon className="h-4 w-4 text-gray-500" />
                        <span className="text-xs font-semibold text-gray-700 uppercase">People</span>
                      </div>
                      {previewResults.results.contacts.length > 0 && (
                        <button
                          onClick={() => handleViewAllCategory('contacts')}
                          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                        >
                          View All
                        </button>
                      )}
                    </div>
                    {previewResults.results.contacts.slice(0, 3).map((result, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(result.title)}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-3 transition-colors"
                      >
                        <UserIcon className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 truncate">{result.title}</div>
                          <div className="text-sm text-gray-600 truncate">{result.subtitle}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Organizations Section */}
                {previewResults.results.organizations.length > 0 && (
                  <div>
                    <div className="px-4 py-2 bg-gray-50 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <BuildingOfficeIcon className="h-4 w-4 text-gray-500" />
                        <span className="text-xs font-semibold text-gray-700 uppercase">Organizations</span>
                      </div>
                      {previewResults.results.organizations.length > 0 && (
                        <button
                          onClick={() => handleViewAllCategory('organizations')}
                          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                        >
                          View All
                        </button>
                      )}
                    </div>
                    {previewResults.results.organizations.slice(0, 3).map((result, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(result.title)}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start gap-3 transition-colors last:rounded-b-lg"
                      >
                        <BuildingOfficeIcon className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 truncate">{result.title}</div>
                          <div className="text-sm text-gray-600 truncate">{result.subtitle}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Footer with total results */}
                <div className="px-4 py-2 bg-gray-50 text-center border-t border-gray-200">
                  <button
                    onClick={() => handleSearch()}
                    className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    See all {previewResults.total_results} results →
                  </button>
                </div>
              </div>
            )}
          </form>

          {/* Filter Bar */}
          <div className="mt-4 flex items-center gap-3 flex-wrap">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-colors ${
                showFilters 
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-gray-50'
              }`}
            >
              <AdjustmentsHorizontalIcon className="h-5 w-5" />
              Filters
            </button>

            {/* Quick Type Filters */}
            {(['contacts', 'meetings', 'organizations', 'causes'] as const).map((type) => (
              <button
                key={type}
                onClick={() => toggleType(type)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full border-2 transition-all ${
                  selectedTypes.includes(type)
                    ? `${getTypeColor(type)} border-current font-medium shadow-sm`
                    : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400 hover:bg-gray-50'
                }`}
              >
                {selectedTypes.includes(type) && (
                  <CheckIcon className="h-4 w-4 flex-shrink-0" />
                )}
                {getTypeIcon(type)}
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>

          {/* Advanced Filters Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    State
                  </label>
                  <select
                    value={selectedState}
                    onChange={(e) => setSelectedState(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 bg-white"
                  >
                    <option value="" className="text-gray-900">All States</option>
                    <option value="AL" className="text-gray-900">Alabama</option>
                    <option value="GA" className="text-gray-900">Georgia</option>
                    <option value="MA" className="text-gray-900">Massachusetts</option>
                    <option value="WA" className="text-gray-900">Washington</option>
                    <option value="WI" className="text-gray-900">Wisconsin</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Search Results */}
        {(activeQuery || selectedState || searchResults) && (
          <div>
            {isLoading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                <p className="mt-4 text-gray-600">Searching...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <p className="text-red-600">Error loading search results. Please try again.</p>
              </div>
            )}

            {searchResults && (
              <>
                {/* Results Summary */}
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    {searchResults.query ? (
                      <>{searchResults.total_results} results for "{searchResults.query}"</>
                    ) : (
                      <>{searchResults.total_results} results</>
                    )}
                  </h2>
                  {selectedState && (
                    <p className="text-sm text-gray-600 mt-1">
                      Filtered by state: {selectedState}
                    </p>
                  )}
                </div>

                {/* Results by Type */}
                {selectedTypes.includes('contacts') && searchResults.results.contacts.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <UserIcon className="h-6 w-6 text-blue-600" />
                      People ({searchResults.results.contacts.length})
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      {searchResults.results.contacts.map((result, idx) => (
                        <ResultCard key={idx} result={result} />
                      ))}
                    </div>
                  </div>
                )}

                {selectedTypes.includes('meetings') && searchResults.results.meetings.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <CalendarIcon className="h-6 w-6 text-green-600" />
                      Meetings ({searchResults.results.meetings.length})
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      {searchResults.results.meetings.map((result, idx) => (
                        <ResultCard key={idx} result={result} />
                      ))}
                    </div>
                  </div>
                )}

                {selectedTypes.includes('organizations') && searchResults.results.organizations.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <BuildingOfficeIcon className="h-6 w-6 text-purple-600" />
                      Organizations ({searchResults.results.organizations.length})
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      {searchResults.results.organizations.map((result, idx) => (
                        <ResultCard key={idx} result={result} />
                      ))}
                    </div>
                  </div>
                )}

                {selectedTypes.includes('causes') && searchResults.results.causes.length > 0 && (
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <HeartIcon className="h-6 w-6 text-pink-600" />
                      Causes ({searchResults.results.causes.length})
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      {searchResults.results.causes.map((result, idx) => (
                        <ResultCard key={idx} result={result} />
                      ))}
                    </div>
                  </div>
                )}

                {/* No Results */}
                {searchResults.total_results === 0 && (
                  <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
                    <MagnifyingGlassIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No results found</h3>
                    <p className="text-gray-600">
                      Try different keywords or adjust your filters
                    </p>
                  </div>
                )}

                {/* Pagination Controls */}
                {searchResults.total_results > 0 && searchResults.pagination.total_pages > 1 && (
                  <div className="mt-8 flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
                    <div className="text-sm text-gray-600">
                      Page {searchResults.pagination.page} of {searchResults.pagination.total_pages}
                      <span className="ml-2">•</span>
                      <span className="ml-2">{searchResults.total_results} total results</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handlePageChange(searchResults.pagination.page - 1)}
                        disabled={!searchResults.pagination.has_prev}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                          searchResults.pagination.has_prev
                            ? 'bg-primary-600 text-white hover:bg-primary-700'
                            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        ← Previous
                      </button>
                      
                      {/* Page numbers */}
                      <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, searchResults.pagination.total_pages) }, (_, i) => {
                          const pageNum = Math.max(
                            1,
                            Math.min(
                              searchResults.pagination.page - 2 + i,
                              searchResults.pagination.total_pages - 4
                            )
                          ) + Math.min(i, 4)
                          
                          if (pageNum > searchResults.pagination.total_pages) return null
                          
                          return (
                            <button
                              key={pageNum}
                              onClick={() => handlePageChange(pageNum)}
                              className={`px-3 py-1 rounded ${
                                pageNum === searchResults.pagination.page
                                  ? 'bg-primary-600 text-white font-semibold'
                                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                              }`}
                            >
                              {pageNum}
                            </button>
                          )
                        })}
                      </div>
                      
                      <button
                        onClick={() => handlePageChange(searchResults.pagination.page + 1)}
                        disabled={!searchResults.pagination.has_next}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                          searchResults.pagination.has_next
                            ? 'bg-primary-600 text-white hover:bg-primary-700'
                            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        Next →
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Initial State - Search Examples */}
        {!activeQuery && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            {(selectedState || selectedTypes.length < 4) && (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-800 font-medium">
                  {selectedState && `State filter: ${selectedState}`}
                  {selectedState && selectedTypes.length < 4 && ' • '}
                  {selectedTypes.length < 4 && `Type filter: ${selectedTypes.join(', ')}`}
                </p>
                <p className="text-blue-700 text-sm mt-1">
                  Enter a search query above to see results with these filters applied.
                </p>
              </div>
            )}
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Try searching for:</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { query: 'dental health', icon: HeartIcon, description: 'Find organizations and meetings about dental health' },
                { query: 'affordable housing', icon: BuildingOfficeIcon, description: 'Discover housing-related initiatives' },
                { query: 'school board', icon: CalendarIcon, description: 'View school board meetings and decisions' },
                { query: 'mental health', icon: HeartIcon, description: 'Explore mental health programs and services' },
              ].map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuery(example.query)
                    setActiveQuery(example.query)
                  }}
                  className="text-left p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <example.icon className="h-6 w-6 text-primary-600" />
                    <span className="font-semibold text-gray-900">{example.query}</span>
                  </div>
                  <p className="text-sm text-gray-600">{example.description}</p>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
