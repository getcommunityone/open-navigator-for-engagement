import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { MagnifyingGlassIcon, MapIcon as MapIconOutline, ListBulletIcon } from '@heroicons/react/24/outline'
import USMap from '../components/USMap'

interface Bill {
  bill_id: string
  bill_number: string
  title: string
  classification: string[]
  session: string
  session_name: string
  first_action_date: string
  latest_action_date: string
  latest_action: string
  jurisdiction: string
}

interface Session {
  session: string
  session_name: string
  start_date: string
  end_date: string
  bill_count: number
}

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

export default function PolicyMap() {
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map')
  const [selectedState, setSelectedState] = useState('AL')
  const [selectedSession, setSelectedSession] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTopic, setSelectedTopic] = useState('')
  const [showTopicSelector, setShowTopicSelector] = useState(true)
  const [page, setPage] = useState(1)
  const limit = 20

  // Fetch map aggregation data
  const { data: mapData, isLoading: mapLoading, error: mapError } = useQuery<{
    states: Record<string, StateData>
    topic: string | null
    session: string | null
    legend: {
      types: Record<string, string>
      statuses: Record<string, string>
    }
  }>({
    queryKey: ['billsMap', selectedTopic, selectedSession],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedTopic) params.append('topic', selectedTopic)
      if (selectedSession) params.append('session', selectedSession)
      
      const response = await api.get(`/bills/map?${params}`)
      return response.data
    },
    enabled: viewMode === 'map' && !showTopicSelector && selectedTopic !== '',
    retry: 2,
    retryDelay: 1000,
  })

  // Fetch sessions
  const { data: sessionsData } = useQuery({
    queryKey: ['sessions', selectedState],
    queryFn: async () => {
      const response = await api.get(`/bills/sessions?state=${selectedState}`)
      return response.data
    },
    enabled: viewMode === 'list', // Only fetch sessions in list view
    retry: 2,
    retryDelay: 1000,
  })

  // Fetch bills
  const { data: billsData, isLoading, error: billsError } = useQuery<{
    total: number
    bills: Bill[]
    pagination: { limit: number; offset: number; has_more: boolean }
  }>({
    queryKey: ['bills', selectedState, selectedSession, searchQuery, page],
    queryFn: async () => {
      const params = new URLSearchParams({
        state: selectedState,
        limit: limit.toString(),
        offset: ((page - 1) * limit).toString(),
      })
      if (selectedSession) params.append('session', selectedSession)
      if (searchQuery) params.append('q', searchQuery)

      const response = await api.get(`/bills?${params}`)
      return response.data
    },
    enabled: viewMode === 'list',
    retry: 2,
    retryDelay: 1000,
  })

  const totalPages = Math.ceil((billsData?.total || 0) / limit)

  const handleStateClick = (stateCode: string) => {
    setSelectedState(stateCode)
    setViewMode('list')
  }

  const handleTopicSelect = (topic: string) => {
    setSelectedTopic(topic)
    setShowTopicSelector(false)
    setViewMode('map')
  }

  const handleBackToTopics = () => {
    setShowTopicSelector(true)
    setSelectedTopic('')
  }

  const totalStatesWithLegislation = mapData ? Object.values(mapData.states).filter(s => s.total_bills > 0).length : 0
  const totalBillsAcrossStates = mapData ? Object.values(mapData.states).reduce((sum, s) => sum + s.total_bills, 0) : 0

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header with Compact Controls */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">
                📜 Legislative Policy Map
              </h1>
              <p className="text-gray-600">
                Track state legislation initiatives compared across the country
              </p>
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode('map')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${
                  viewMode === 'map'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <MapIconOutline className="h-5 w-5" />
                Map View
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <ListBulletIcon className="h-5 w-5" />
                List View
              </button>
            </div>
          </div>
        </div>

        {/* Compact Filters - Always visible at top */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
          <div className="flex flex-wrap items-end gap-4">
            {/* Topic Filter */}
            {viewMode === 'map' && (
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Topic
                </label>
                <select
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm text-gray-900 py-2"
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                >
                  <option value="">All Topics</option>
                  <option value="dental">Dental Health</option>
                  <option value="fluorid">Fluoridation</option>
                  <option value="oral health">Oral Health</option>
                  <option value="medicaid">Medicaid</option>
                  <option value="education">Education</option>
                  <option value="health">Health</option>
                </select>
              </div>
            )}

            {/* State Filter - list view */}
            {viewMode === 'list' && (
              <div className="flex-1 min-w-[150px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  State
                </label>
                <select
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm text-gray-900 py-2"
                  value={selectedState}
                  onChange={(e) => {
                    setSelectedState(e.target.value)
                    setPage(1)
                  }}
                >
                  <option value="AL">Alabama</option>
                  <option value="GA">Georgia</option>
                  <option value="IN">Indiana</option>
                  <option value="MA">Massachusetts</option>
                  <option value="WA">Washington</option>
                  <option value="WI">Wisconsin</option>
                </select>
              </div>
            )}

            {/* Session Filter - list view */}
            {viewMode === 'list' && (
              <div className="flex-1 min-w-[200px]">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Legislative Session
                </label>
                <select
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm text-gray-900 py-2"
                  value={selectedSession}
                  onChange={(e) => {
                    setSelectedSession(e.target.value)
                    setPage(1)
                  }}
                >
                  <option value="">All Sessions</option>
                  {sessionsData?.sessions?.map((session: Session) => (
                    <option key={session.session} value={session.session}>
                      {session.session_name} ({session.bill_count.toLocaleString()} bills)
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Search */}
            <div className="flex-1 min-w-[250px]">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {viewMode === 'map' ? 'Search Keywords' : 'Search Bills'}
              </label>
              <div className="relative">
                <input
                  type="text"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-10 text-sm text-gray-900 py-2"
                  placeholder="dental, health, education..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && setPage(1)}
                />
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              </div>
            </div>

            {/* Clear button */}
            {(searchQuery || selectedSession || selectedTopic) && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('')
                  setSelectedSession('')
                  setSelectedTopic('')
                  setPage(1)
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm font-medium"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Map Visualization - Visible on Page Load */}
        {viewMode === 'map' && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            {/* Clear Explanatory Title */}
            <div className="mb-6 border-b border-gray-200 pb-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {selectedTopic ? (
                  <>
                    {selectedTopic.charAt(0).toUpperCase() + selectedTopic.slice(1)} Legislation Across the US
                  </>
                ) : (
                  <>State-by-State Legislative Policy Overview</>
                )}
              </h2>
              <p className="text-base text-gray-600">
                {selectedTopic === 'fluorid' && (
                  <>See which states mandate water fluoridation, which have removed it, and where funding or studies are underway. Each state's color shows the primary type of legislation, while darker/lighter shades indicate whether bills have been enacted, are pending, or have failed.</>
                )}
                {selectedTopic === 'dental' && (
                  <>Track dental health policies including coverage expansion, screening programs, provider access initiatives, and funding. Colors show the main focus of legislation in each state, with shading indicating current status.</>
                )}
                {selectedTopic === 'medicaid' && (
                  <>Monitor Medicaid program changes across states, including expansions, coverage modifications, reimbursement adjustments, and eligibility requirements. The map shows what type of Medicaid legislation is most active in each state.</>
                )}
                {selectedTopic === 'health' && (
                  <>View health-related legislation including protections, restrictions, funding initiatives, and healthcare reforms. Each state's color indicates the dominant type of health policy being considered or enacted.</>
                )}
                {selectedTopic === 'education' && (
                  <>Explore educational policy across states, from new requirements and curriculum changes to funding initiatives and system reforms. Colors represent the primary focus of education legislation in each state.</>
                )}
                {!selectedTopic && (
                  <>This interactive map shows legislative activity across all 50 states. Click any state to drill down into specific bills, or use the topic filter above to focus on a particular policy area. Colors indicate the primary type of legislation, while shading shows whether bills have been enacted (darker), are pending (normal), or failed (lighter).</>
                )}
              </p>
            </div>

            {mapError ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                <div className="text-red-600 text-5xl mb-4">⚠️</div>
                <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to load map data</h3>
                <p className="text-red-700">{String(mapError)}</p>
              </div>
            ) : mapLoading ? (
              <div className="flex justify-center items-center h-96">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading map...</p>
                </div>
              </div>
            ) : (
              <USMap
                stateData={mapData?.states || {}}
                onStateClick={handleStateClick}
                legend={mapData?.legend}
              />
            )}
          </div>
        )}

        {/* Stats Summary - Below Map */}
        {viewMode === 'map' && mapData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
              <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                States with Legislation
              </div>
              <div className="mt-2 text-3xl font-bold text-gray-900">
                {totalStatesWithLegislation}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {selectedTopic ? `matching "${selectedTopic}"` : 'all topics'}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
              <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                Total Bills
              </div>
              <div className="mt-2 text-3xl font-bold text-gray-900">
                {totalBillsAcrossStates.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                across all states
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
              <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                Filter Topic
              </div>
              <div className="mt-2 text-xl font-bold text-gray-900">
                {selectedTopic || 'All Topics'}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                Click map to drill down
              </div>
            </div>
          </div>
        )}
        
        {viewMode === 'list' && billsData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
              <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                Total Bills
              </div>
              <div className="mt-2 text-3xl font-bold text-gray-900">
                {billsData.total.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {selectedSession ? `in ${selectedSession}` : 'all sessions'}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
              <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                Sessions Available
              </div>
              <div className="mt-2 text-3xl font-bold text-gray-900">
                {sessionsData?.total_sessions || 0}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {sessionsData?.sessions?.[0]?.session} - {sessionsData?.sessions?.[sessionsData.sessions.length - 1]?.session}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
              <div className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                Showing
              </div>
              <div className="mt-2 text-3xl font-bold text-gray-900">
                {billsData.bills.length}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                Page {page} of {totalPages}
              </div>
            </div>
          </div>
        )}

        {/* Bills List */}
        {viewMode === 'list' && (
          <>
            {billsError ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                <div className="text-red-600 text-5xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold text-red-900 mb-2">
                  Unable to Load Bills
                </h3>
                <p className="text-red-700 mb-4">
                  {billsError instanceof Error 
                    ? billsError.message 
                    : 'There was an error fetching bills data. The API server may be unavailable.'}
                </p>
                <div className="flex gap-3 justify-center">
                  <button
                    onClick={() => window.location.reload()}
                    className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium"
                  >
                    Retry
                  </button>
                  <button
                    onClick={() => setViewMode('map')}
                    className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
                  >
                    Switch to Map View
                  </button>
                </div>
              </div>
            ) : isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading bills...</p>
              </div>
            ) : (
              <>
            <div className="space-y-4 mb-6">
              {billsData?.bills.map((bill) => (
                <div
                  key={bill.bill_id}
                  className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow border-l-4 border-blue-500"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                          {bill.bill_number}
                        </span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                          {bill.classification.join(', ')}
                        </span>
                        <span className="text-sm text-gray-500">
                          {bill.session_name}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {bill.title}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>
                          <strong>Latest Action:</strong> {bill.latest_action}
                        </span>
                        {bill.latest_action_date && (
                          <span>
                            <strong>Date:</strong>{' '}
                            {new Date(bill.latest_action_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between bg-white rounded-lg shadow-sm p-4">
                <div className="text-sm text-gray-600">
                  Showing {(page - 1) * limit + 1} to{' '}
                  {Math.min(page * limit, billsData?.total || 0)} of{' '}
                  {billsData?.total.toLocaleString()} bills
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 text-gray-700">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}

            {/* No Results */}
            {!isLoading && !billsError && billsData && billsData.bills.length === 0 && (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <p className="text-gray-600 text-lg">No bills found matching your filters.</p>
                <button
                  onClick={() => {
                    setSearchQuery('')
                    setSelectedSession('')
                    setPage(1)
                  }}
                  className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            )}
          </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
