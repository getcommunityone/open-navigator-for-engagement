import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import axios from 'axios'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

interface Document {
  id: string
  state: string
  municipality: string
  title: string
  meeting_date: string
  url: string
  topics: string[]
  sentiment: string
}

export default function Documents() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '')
  const [page, setPage] = useState(1)

  useEffect(() => {
    const searchFromUrl = searchParams.get('search')
    if (searchFromUrl) {
      setSearchQuery(searchFromUrl)
    }
  }, [searchParams])

  const { data, isLoading } = useQuery({
    queryKey: ['documents', searchQuery, page],
    queryFn: async () => {
      const response = await axios.get('/api/documents', {
        params: { search: searchQuery, page, limit: 20 },
      })
      return response.data
    },
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    if (searchQuery) {
      setSearchParams({ search: searchQuery })
    } else {
      setSearchParams({})
    }
  }

  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: '#F1F5F9' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Explorer</h1>
          <p className="text-gray-600">
            Search meeting minutes and budgets from 90,000+ cities, counties, and school districts
          </p>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <form onSubmit={handleSearch}>
            <div className="relative">
              <input
                type="text"
                placeholder="Search by location, topic, keyword..."
                className="w-full px-4 py-3 pl-12 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <MagnifyingGlassIcon className="absolute left-4 top-3.5 h-6 w-6 text-gray-400" />
              <button
                type="submit"
                className="absolute right-2 top-2 bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                Search
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="card">Loading documents...</div>
          ) : (
            <>
              {data?.documents?.map((doc: Document) => (
              <div key={doc.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{doc.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {doc.municipality}, {doc.state} • {new Date(doc.meeting_date).toLocaleDateString()}
                    </p>
                    
                    <div className="mt-3 flex flex-wrap gap-2">
                      {doc.topics.map((topic) => (
                        <span
                          key={topic}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                        >
                          {topic.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <a
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary ml-4"
                  >
                    View Document
                  </a>
                </div>
              </div>
            ))}

            {/* Pagination */}
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <span className="flex items-center px-4">
                Page {page} of {data?.total_pages || 1}
              </span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= (data?.total_pages || 1)}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </>
          )}
        </div>
      </div>
    </div>
  )
}
