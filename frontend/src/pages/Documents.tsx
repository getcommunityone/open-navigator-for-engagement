import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

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
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['documents', searchQuery, page],
    queryFn: async () => {
      const response = await axios.get('/api/documents', {
        params: { search: searchQuery, page, limit: 20 },
      })
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="card">
        <input
          type="text"
          placeholder="Search documents..."
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
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
  )
}
