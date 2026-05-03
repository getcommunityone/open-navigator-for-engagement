import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../lib/api'
import { MagnifyingGlassIcon, MapIcon as MapIconOutline, ListBulletIcon, AdjustmentsHorizontalIcon, XMarkIcon } from '@heroicons/react/24/outline'
import USMap from '../components/USMap'
import MultiSelect from '../components/MultiSelect'

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
  latest_action_description: string
  jurisdiction: string
  jurisdiction_name: string
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
  const [searchParams, setSearchParams] = useSearchParams()
  const [viewMode, setViewMode] = useState<'map' | 'list'>('map')
  const [selectedState, setSelectedState] = useState('AL')
  const [selectedSession, setSelectedSession] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'name'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [expandedBill, setExpandedBill] = useState<string | null>(null)
  
  // Multi-select filter states
  const [selectedSessions, setSelectedSessions] = useState<string[]>([])
  const [selectedChambers, setSelectedChambers] = useState<string[]>([])
  const [selectedBillTypes, setSelectedBillTypes] = useState<string[]>([])
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([])
  
  // Read topic from URL - use state that syncs with URL
  const [selectedTopic, setSelectedTopic] = useState<string>('')
  const [showTopicSelector, setShowTopicSelector] = useState(true)
  
  // Advanced filters sidebar state
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  
  // Sync topic FROM URL to state (on mount and URL changes)
  useEffect(() => {
    const topicFromUrl = searchParams.get('topic') || ''
    if (topicFromUrl) {
      setSelectedTopic(topicFromUrl)
      setShowTopicSelector(false)
      console.log('🔗 Initialized topic from URL:', topicFromUrl)
    } else {
      setSelectedTopic('')
      setShowTopicSelector(true)
    }
  }, [searchParams]) // Re-run when URL changes
  
  // Sync topic changes TO URL (when user selects a topic)
  // IMPORTANT: Don't include searchParams in deps to avoid circular updates
  useEffect(() => {
    const currentTopicInUrl = searchParams.get('topic') || ''
    
    if (selectedTopic && !showTopicSelector) {
      // Only update URL if topic is different
      if (currentTopicInUrl !== selectedTopic) {
        setSearchParams({ topic: selectedTopic }, { replace: true })
        console.log('📝 Updated URL with topic:', selectedTopic)
      }
    } else if (showTopicSelector && currentTopicInUrl) {
      // Clear topic from URL if selector is shown
      setSearchParams({}, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTopic, showTopicSelector, setSearchParams])
  
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
    staleTime: 5 * 60 * 1000, // 5 minutes - prevent refetch jitters
    refetchOnWindowFocus: false,
    retry: 1, // Reduce retries on mobile
    retryDelay: 1000,
    gcTime: 10 * 60 * 1000, // Cache for 10 minutes
  })

  // Fetch sessions
  const { data: sessionsData } = useQuery<{
    total_sessions: number
    sessions: Session[]
  }>({
    queryKey: ['sessions', selectedState, selectedTopic, selectedChambers, selectedBillTypes, selectedStatuses, searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams({ state: selectedState })
      if (selectedTopic) params.append('topic', selectedTopic)
      if (selectedChambers.length > 0) params.append('chambers', selectedChambers.join(','))
      if (selectedBillTypes.length > 0) params.append('bill_types', selectedBillTypes.join(','))
      if (selectedStatuses.length > 0) params.append('statuses', selectedStatuses.join(','))
      if (searchQuery) params.append('q', searchQuery)
      
      // Debug logging
      console.log('🔍 Fetching sessions with params:', {
        state: selectedState,
        topic: selectedTopic,
        chambers: selectedChambers,
        bill_types: selectedBillTypes,
        statuses: selectedStatuses,
        q: searchQuery,
        url: `/bills/sessions?${params}`
      })
      
      const response = await api.get(`/bills/sessions?${params}`)
      console.log('✅ Sessions response:', {
        total_sessions: response.data.total_sessions,
        sessions: response.data.sessions?.length
      })
      return response.data
    },
    enabled: viewMode === 'list' && !showTopicSelector && (
      selectedTopic !== '' || 
      searchQuery !== '' || 
      selectedChambers.length > 0 || 
      selectedBillTypes.length > 0 || 
      selectedStatuses.length > 0
    ), // Fetch sessions filtered by any active criteria
    staleTime: 1 * 60 * 1000, // 1 minute - ensure filters are respected
    refetchOnWindowFocus: false,
    retry: 1, // Reduce retries on mobile
    retryDelay: 1000,
    gcTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  // Auto-select most recent session ONLY when drilling down from map (state/topic change with no active filters)
  useEffect(() => {
    // Only run if we have sessions data and no filters are active
    const hasNoFilters = selectedChambers.length === 0 && 
                        selectedBillTypes.length === 0 && 
                        selectedStatuses.length === 0 && 
                        !searchQuery

    if (
      sessionsData?.sessions && 
      sessionsData.sessions.length > 0 && 
      selectedSessions.length === 0 &&
      hasNoFilters
    ) {
      // Auto-select most recent session
      const mostRecentSession = sessionsData.sessions[0]
      console.log('📅 Auto-selecting most recent session:', mostRecentSession.session_name)
      setSelectedSessions([mostRecentSession.session])
    }
    // Only depend on state/topic changes and sessions data, NOT on selectedSessions to avoid loops
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedState, selectedTopic, sessionsData?.sessions])

  // Fetch bills
  const { data: billsData, isLoading, error: billsError } = useQuery<{
    total: number
    bills: Bill[]
    pagination: { limit: number; offset: number; has_more: boolean }
  }>({
    queryKey: ['bills', selectedState, selectedSessions, searchQuery, selectedTopic, selectedChambers, selectedBillTypes, selectedStatuses, page],
    queryFn: async () => {
      const params = new URLSearchParams({
        state: selectedState,
        limit: limit.toString(),
        offset: ((page - 1) * limit).toString(),
      })
      if (selectedSessions.length > 0) params.append('sessions', selectedSessions.join(','))
      if (searchQuery) params.append('q', searchQuery)
      if (selectedTopic) params.append('topic', selectedTopic)
      if (selectedChambers.length > 0) params.append('chambers', selectedChambers.join(','))
      if (selectedBillTypes.length > 0) params.append('bill_types', selectedBillTypes.join(','))
      if (selectedStatuses.length > 0) params.append('statuses', selectedStatuses.join(','))

      const response = await api.get(`/bills?${params}`)
      return response.data
    },
    enabled: viewMode === 'list' && !showTopicSelector && (
      selectedTopic !== '' || 
      searchQuery !== '' || 
      selectedSessions.length > 0 || 
      selectedChambers.length > 0 || 
      selectedBillTypes.length > 0 || 
      selectedStatuses.length > 0
    ), // Allow querying with topic, search, OR any advanced filters
    staleTime: 1 * 60 * 1000, // 1 minute - ensure filters are respected
    refetchOnWindowFocus: false,
    retry: 1, // Reduce retries on mobile
    retryDelay: 1000,
    gcTime: 5 * 60 * 1000, // Cache for 5 minutes
  })

  const totalPages = Math.ceil((billsData?.total || 0) / limit)

  const handleStateClick = (stateCode: string) => {
    console.log('🗺️ State clicked:', stateCode, 'Current topic:', selectedTopic)
    // Batch updates to prevent flickering - setState calls are already batched in React 18
    setSelectedState(stateCode)
    // Clear any existing filters to start fresh
    setSelectedSessions([])
    setSelectedChambers([])
    setSelectedBillTypes([])
    setSelectedStatuses([])
    setSearchQuery('')
    setPage(1)
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
  
  // Sort bills client-side
  const sortedBills = billsData?.bills ? [...billsData.bills].sort((a, b) => {
    if (sortBy === 'date') {
      const dateA = a.latest_action_date ? new Date(a.latest_action_date).getTime() : 0
      const dateB = b.latest_action_date ? new Date(b.latest_action_date).getTime() : 0
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA
    } else {
      // Sort by bill number
      const numA = a.bill_number
      const numB = b.bill_number
      return sortOrder === 'asc' 
        ? numA.localeCompare(numB)
        : numB.localeCompare(numA)
    }
  }) : []

  const totalStatesWithLegislation = mapData ? Object.values(mapData.states).filter(s => s.total_bills > 0).length : 0
  const totalBillsAcrossStates = mapData ? Object.values(mapData.states).reduce((sum, s) => sum + s.total_bills, 0) : 0

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">
                📜 Legislative Policy Map
              </h1>
              <p className="text-gray-600">
                {showTopicSelector 
                  ? 'Choose a topic to explore state-by-state legislation' 
                  : 'Track state legislation initiatives compared across the country'
                }
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Back to Map button - show when in list view */}
              {!showTopicSelector && viewMode === 'list' && (
                <button
                  onClick={() => setViewMode('map')}
                  className="flex items-center gap-2 px-4 py-2 rounded-md font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                >
                  ← Back to Map
                </button>
              )}
              
              {/* Back to Topics button */}
              {!showTopicSelector && (
                <button
                  onClick={handleBackToTopics}
                  className="flex items-center gap-2 px-4 py-2 rounded-md font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
                >
                  ← Back to Topics
                </button>
              )}

              {/* View Mode Toggle - only show when topic is selected */}
              {!showTopicSelector && (
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
              )}
            </div>
          </div>
        </div>

        {/* Topic Selection View */}
        {showTopicSelector && (
          <div className="space-y-8">
            <div className="text-center max-w-3xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                Select a Policy Topic
              </h2>
              <p className="text-gray-600">
                Choose a topic below to see how states across the country are addressing it through legislation
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Fluoridation Card */}
              <button
                onClick={() => handleTopicSelect('fluoride')}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 text-left border-2 border-transparent hover:border-blue-500"
              >
                <div className="text-5xl mb-4">💧</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Water Fluoridation
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Track mandates, removals, funding initiatives, and studies on community water fluoridation programs
                </p>
                <div className="text-blue-600 font-medium text-sm">
                  View Legislation →
                </div>
              </button>

              {/* Dental Health Card */}
              <button
                onClick={() => handleTopicSelect('dental')}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 text-left border-2 border-transparent hover:border-blue-500"
              >
                <div className="text-5xl mb-4">🦷</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Dental Health
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Monitor coverage expansions, screening programs, provider access, and funding for dental health services
                </p>
                <div className="text-blue-600 font-medium text-sm">
                  View Legislation →
                </div>
              </button>

              {/* Oral Health Card */}
              <button
                onClick={() => handleTopicSelect('oral health')}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 text-left border-2 border-transparent hover:border-blue-500"
              >
                <div className="text-5xl mb-4">😁</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Oral Health (General)
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Explore comprehensive oral health policies including prevention, treatment, and public health initiatives
                </p>
                <div className="text-blue-600 font-medium text-sm">
                  View Legislation →
                </div>
              </button>

              {/* Medicaid Card */}
              <button
                onClick={() => handleTopicSelect('medicaid')}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 text-left border-2 border-transparent hover:border-blue-500"
              >
                <div className="text-5xl mb-4">🏥</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Medicaid
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Follow Medicaid expansions, coverage changes, reimbursement rates, and eligibility requirements
                </p>
                <div className="text-blue-600 font-medium text-sm">
                  View Legislation →
                </div>
              </button>

              {/* Education Card */}
              <button
                onClick={() => handleTopicSelect('education')}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 text-left border-2 border-transparent hover:border-blue-500"
              >
                <div className="text-5xl mb-4">🎓</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Education
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  View educational requirements, curriculum changes, funding initiatives, and school health programs
                </p>
                <div className="text-blue-600 font-medium text-sm">
                  View Legislation →
                </div>
              </button>

              {/* General Health Card */}
              <button
                onClick={() => handleTopicSelect('health')}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 text-left border-2 border-transparent hover:border-blue-500"
              >
                <div className="text-5xl mb-4">🏨</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Health (General)
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  Examine broader health policies including protections, restrictions, funding, and healthcare reforms
                </p>
                <div className="text-blue-600 font-medium text-sm">
                  View Legislation →
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Map and List View - only show when topic is selected */}
        {!showTopicSelector && (
          <>
            {/* Selected Topic Badge */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {selectedTopic === 'fluoride' && '💧'}
                    {selectedTopic === 'dental' && '🦷'}
                    {selectedTopic === 'oral health' && '😁'}
                    {selectedTopic === 'medicaid' && '🏥'}
                    {selectedTopic === 'education' && '🎓'}
                    {selectedTopic === 'health' && '🏨'}
                  </span>
                  <div>
                    <div className="text-sm text-gray-600">Viewing legislation for:</div>
                    <div className="text-lg font-bold text-gray-900 capitalize">
                      {selectedTopic === 'fluoride' ? 'Water Fluoridation' :
                       selectedTopic === 'dental' ? 'Dental Health' :
                       selectedTopic === 'oral health' ? 'Oral Health' :
                       selectedTopic === 'medicaid' ? 'Medicaid' :
                       selectedTopic === 'education' ? 'Education' :
                       'Health'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Basic Filters - Clean and Spacious */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* State Filter - list view only */}
                {viewMode === 'list' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      State
                    </label>
                    <select
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900 py-2.5"
                      value={selectedState}
                      onChange={(e) => {
                        setSelectedState(e.target.value)
                        setPage(1)
                      }}
                    >
                      <option value="AL">Alabama</option>
                      <option value="AK">Alaska</option>
                      <option value="AZ">Arizona</option>
                      <option value="AR">Arkansas</option>
                      <option value="CA">California</option>
                      <option value="CO">Colorado</option>
                      <option value="CT">Connecticut</option>
                      <option value="DE">Delaware</option>
                      <option value="FL">Florida</option>
                      <option value="GA">Georgia</option>
                      <option value="HI">Hawaii</option>
                      <option value="ID">Idaho</option>
                      <option value="IL">Illinois</option>
                      <option value="IN">Indiana</option>
                      <option value="IA">Iowa</option>
                      <option value="KS">Kansas</option>
                      <option value="KY">Kentucky</option>
                      <option value="LA">Louisiana</option>
                      <option value="ME">Maine</option>
                      <option value="MD">Maryland</option>
                      <option value="MA">Massachusetts</option>
                      <option value="MI">Michigan</option>
                      <option value="MN">Minnesota</option>
                      <option value="MS">Mississippi</option>
                      <option value="MO">Missouri</option>
                      <option value="MT">Montana</option>
                      <option value="NE">Nebraska</option>
                      <option value="NV">Nevada</option>
                      <option value="NH">New Hampshire</option>
                      <option value="NJ">New Jersey</option>
                      <option value="NM">New Mexico</option>
                      <option value="NY">New York</option>
                      <option value="NC">North Carolina</option>
                      <option value="ND">North Dakota</option>
                      <option value="OH">Ohio</option>
                      <option value="OK">Oklahoma</option>
                      <option value="OR">Oregon</option>
                      <option value="PA">Pennsylvania</option>
                      <option value="RI">Rhode Island</option>
                      <option value="SC">South Carolina</option>
                      <option value="SD">South Dakota</option>
                      <option value="TN">Tennessee</option>
                      <option value="TX">Texas</option>
                      <option value="UT">Utah</option>
                      <option value="VT">Vermont</option>
                      <option value="VA">Virginia</option>
                      <option value="WA">Washington</option>
                      <option value="WV">West Virginia</option>
                      <option value="WI">Wisconsin</option>
                      <option value="WY">Wyoming</option>
                    </select>
                  </div>
                )}

                {/* Search - Prominent */}
                <div className={viewMode === 'list' ? 'md:col-span-2' : 'md:col-span-3'}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {viewMode === 'map' ? 'Search Keywords' : 'Search Bills'}
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-10 text-gray-900 py-2.5"
                      placeholder="Search within results..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && setPage(1)}
                    />
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </div>

              {/* Advanced Filters Button & Active Filter Indicator */}
              {viewMode === 'list' && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                  >
                    <AdjustmentsHorizontalIcon className="h-5 w-5" />
                    Advanced Filters
                    {(selectedSessions.length > 0 || selectedChambers.length > 0 || selectedBillTypes.length > 0 || selectedStatuses.length > 0) && (
                      <span className="ml-1 bg-blue-800 text-white rounded-full px-2 py-0.5 text-xs font-bold">
                        {selectedSessions.length + selectedChambers.length + selectedBillTypes.length + selectedStatuses.length}
                      </span>
                    )}
                  </button>

                  {/* Active Filters Summary */}
                  {(selectedSessions.length > 0 || selectedChambers.length > 0 || selectedBillTypes.length > 0 || selectedStatuses.length > 0 || searchQuery) && (
                    <button
                      onClick={() => {
                        setSearchQuery('')
                        setSelectedSessions([])
                        setSelectedChambers([])
                        setSelectedBillTypes([])
                        setSelectedStatuses([])
                        setPage(1)
                      }}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm font-medium"
                    >
                      Clear All Filters
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Advanced Filters Sidebar */}
            {viewMode === 'list' && showAdvancedFilters && (
              <>
                {/* Backdrop */}
                <div 
                  className="fixed inset-0 bg-black bg-opacity-50 z-40"
                  onClick={() => setShowAdvancedFilters(false)}
                />
                
                {/* Sidebar */}
                <div className="fixed right-0 top-0 h-full w-full md:w-96 bg-white shadow-2xl z-50 overflow-y-auto">
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-gray-900">Advanced Filters</h3>
                      <button
                        onClick={() => setShowAdvancedFilters(false)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        <XMarkIcon className="h-6 w-6" />
                      </button>
                    </div>

                    {/* Filters */}
                    <div className="space-y-6">
                      {/* Session Filter */}
                      <div>
                        <MultiSelect
                          label="Legislative Session"
                          options={
                            sessionsData?.sessions
                              ?.slice()
                              .sort((a: Session, b: Session) => {
                                const dateA = a.end_date ? new Date(a.end_date).getTime() : 0
                                const dateB = b.end_date ? new Date(b.end_date).getTime() : 0
                                return dateB - dateA
                              })
                              .map((session: Session) => ({
                                value: session.session,
                                label: session.session_name,
                                count: session.bill_count
                              })) || []
                          }
                          selected={selectedSessions}
                          onChange={(values) => {
                            setSelectedSessions(values)
                            setPage(1)
                          }}
                          placeholder="All Sessions"
                        />
                      </div>
                      
                      {/* Chamber Filter */}
                      <div>
                        <MultiSelect
                          label="Chamber"
                          options={[
                            { value: 'house', label: 'House' },
                            { value: 'senate', label: 'Senate' },
                            { value: 'joint', label: 'Joint' }
                          ]}
                          selected={selectedChambers}
                          onChange={(values) => {
                            setSelectedChambers(values)
                            setPage(1)
                          }}
                          placeholder="All Chambers"
                        />
                      </div>
                      
                      {/* Bill Type Filter */}
                      <div>
                        <MultiSelect
                          label="Bill Type"
                          options={[
                            { value: 'bill', label: 'Bill (HB/SB)' },
                            { value: 'resolution', label: 'Resolution (HR/SR)' },
                            { value: 'joint_resolution', label: 'Joint Resolution (HJR/SJR)' },
                            { value: 'concurrent_resolution', label: 'Concurrent Resolution (HCR/SCR)' },
                            { value: 'memorial', label: 'Memorial (HJM/SJM)' }
                          ]}
                          selected={selectedBillTypes}
                          onChange={(values) => {
                            setSelectedBillTypes(values)
                            setPage(1)
                          }}
                          placeholder="All Types"
                        />
                      </div>
                      
                      {/* Status Filter */}
                      <div>
                        <MultiSelect
                          label="Status"
                          options={[
                            { value: 'enacted', label: 'Enacted' },
                            { value: 'passed', label: 'Passed' },
                            { value: 'adopted', label: 'Adopted' },
                            { value: 'failed', label: 'Failed' },
                            { value: 'introduced', label: 'Introduced' },
                            { value: 'referred', label: 'Referred to Committee' },
                            { value: 'reported', label: 'Reported from Committee' }
                          ]}
                          selected={selectedStatuses}
                          onChange={(values) => {
                            setSelectedStatuses(values)
                            setPage(1)
                          }}
                          placeholder="All Statuses"
                        />
                      </div>

                      {/* Sort Controls */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Sort By
                        </label>
                        <div className="space-y-2">
                          <select
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-gray-900 py-2.5"
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as 'date' | 'name')}
                          >
                            <option value="date">Latest Action</option>
                            <option value="name">Bill Number</option>
                          </select>
                          <button
                            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                            className="w-full px-4 py-2.5 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium flex items-center justify-center gap-2"
                          >
                            {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="mt-8 pt-6 border-t border-gray-200 space-y-3">
                      <button
                        onClick={() => {
                          setSelectedSessions([])
                          setSelectedChambers([])
                          setSelectedBillTypes([])
                          setSelectedStatuses([])
                          setPage(1)
                        }}
                        className="w-full px-4 py-2.5 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
                      >
                        Clear Advanced Filters
                      </button>
                      <button
                        onClick={() => setShowAdvancedFilters(false)}
                        className="w-full px-4 py-2.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
                      >
                        Apply Filters
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Map Visualization */}
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
                {selectedTopic === 'fluoride' && (
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
        
            {/* List View */}
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
                ) : billsData && billsData.total === 0 ? (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
                    <div className="text-yellow-600 text-5xl mb-4">📭</div>
                    <h3 className="text-xl font-semibold text-yellow-900 mb-2">
                      No Bills Found
                    </h3>
                    <p className="text-yellow-700 mb-4">
                      {selectedState === 'LA' || selectedState === 'Louisiana' ? (
                        <>Louisiana data is not yet available in our database. We currently have data for Alabama, Georgia, Massachusetts, Washington, and Wisconsin.</>
                      ) : (
                        <>No bills found for the selected filters. Try adjusting your search criteria or clearing filters.</>
                      )}
                    </p>
                    <div className="flex gap-3 justify-center">
                      {(selectedSessions.length > 0 || selectedChambers.length > 0 || selectedBillTypes.length > 0 || selectedStatuses.length > 0 || searchQuery) ? (
                        <button
                          onClick={() => {
                            setSearchQuery('')
                            setSelectedSessions([])
                            setSelectedChambers([])
                            setSelectedBillTypes([])
                            setSelectedStatuses([])
                            setPage(1)
                          }}
                          className="px-6 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors font-medium"
                        >
                          Clear Filters
                        </button>
                      ) : null}
                      <button
                        onClick={() => setViewMode('map')}
                        className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
                      >
                        Back to Map
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="space-y-4 mb-6">
                      {sortedBills.map((bill) => {
                        const isExpanded = expandedBill === bill.bill_id
                        return (
                        <div
                          key={bill.bill_id}
                          className="bg-white rounded-lg shadow-sm border-l-4 border-blue-500 overflow-hidden transition-shadow hover:shadow-md"
                        >
                          {/* Bill Header - Always Visible */}
                          <div 
                            className="p-6 cursor-pointer"
                            onClick={() => setExpandedBill(isExpanded ? null : bill.bill_id)}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2 flex-wrap">
                                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                    {bill.bill_number}
                                  </span>
                                  {bill.classification && bill.classification.length > 0 && (
                                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                                      {bill.classification.join(', ')}
                                    </span>
                                  )}
                                  <span className="text-sm text-gray-500">
                                    {bill.session_name}
                                  </span>
                                </div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                  {bill.title}
                                </h3>
                                <div className="flex items-center gap-4 text-sm text-gray-600">
                                  <span>
                                    <strong>Latest Action:</strong> {bill.latest_action_description || bill.latest_action || 'N/A'}
                                  </span>
                                  {bill.latest_action_date && (
                                    <span>
                                      <strong>Date:</strong>{' '}
                                      {new Date(bill.latest_action_date).toLocaleDateString()}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <button className="ml-4 text-gray-400 hover:text-gray-600">
                                {isExpanded ? '▼' : '▶'}
                              </button>
                            </div>
                          </div>
                          
                          {/* Expanded Details */}
                          {isExpanded && (
                            <div className="px-6 pb-6 border-t border-gray-100">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                <div>
                                  <p className="text-sm font-medium text-gray-700 mb-1">Jurisdiction</p>
                                  <p className="text-sm text-gray-900">{bill.jurisdiction_name}</p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-gray-700 mb-1">Session</p>
                                  <p className="text-sm text-gray-900">{bill.session_name} ({bill.session})</p>
                                </div>
                                {bill.first_action_date && (
                                  <div>
                                    <p className="text-sm font-medium text-gray-700 mb-1">First Action</p>
                                    <p className="text-sm text-gray-900">
                                      {new Date(bill.first_action_date).toLocaleDateString()}
                                    </p>
                                  </div>
                                )}
                                <div>
                                  <p className="text-sm font-medium text-gray-700 mb-1">Bill ID</p>
                                  <p className="text-xs text-gray-600 font-mono break-all">{bill.bill_id}</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )})}
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
          </>
        )}
      </div>
    </div>
  )
}
