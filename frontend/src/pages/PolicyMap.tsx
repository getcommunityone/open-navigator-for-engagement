import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'

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

export default function PolicyMap() {
  const [selectedState, setSelectedState] = useState('AL')
  const [selectedSession, setSelectedSession] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const limit = 20

  // Fetch sessions
  const { data: sessionsData } = useQuery({
    queryKey: ['sessions', selectedState],
    queryFn: async () => {
      const response = await api.get(`/bills/sessions?state=${selectedState}`)
      return response.data
    },
  })

  // Fetch bills
  const { data: billsData, isLoading } = useQuery<{
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
  })

  const totalPages = Math.ceil((billsData?.total || 0) / limit)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1) // Reset to first page on new search
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📜 Legislative Policy Map
          </h1>
          <p className="text-lg text-gray-600">
            Track state legislation, bills, and resolutions with full search and filtering
          </p>
        </div>

        {/* Stats Summary */}
        {billsData && (
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

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FunnelIcon className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
          </div>

          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* State Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  State
                </label>
                <select
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  value={selectedState}
                  onChange={(e) => {
                    setSelectedState(e.target.value)
                    setPage(1)
                  }}
                >
                  <option value="AL">Alabama</option>
                  <option value="GA">Georgia</option>
                  <option value="MA">Massachusetts</option>
                </select>
              </div>

              {/* Session Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Legislative Session
                </label>
                <select
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
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

              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Bills
                </label>
                <div className="relative">
                  <input
                    type="text"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-10"
                    placeholder="dental, health, education..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
              >
                Apply Filters
              </button>
              {(searchQuery || selectedSession) && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('')
                    setSelectedSession('')
                    setPage(1)
                  }}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Bills List */}
        {isLoading ? (
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
          </>
        )}

        {/* No Results */}
        {!isLoading && billsData && billsData.bills.length === 0 && (
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
      </div>
    </div>
  )
}
