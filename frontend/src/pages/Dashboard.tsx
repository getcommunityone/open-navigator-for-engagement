import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#0ea5e9', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6']

interface DashboardStats {
  total_documents: number
  total_opportunities: number
  states_monitored: number
  topics: Record<string, number>
  recent_opportunities: Array<{
    state: string
    municipality: string
    topic: string
    urgency: string
    date: string
  }>
}

export default function Dashboard() {
  const { data, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard')
      return response.data
    },
  })

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>
  }

  const topicData = Object.entries(data?.topics || {}).map(([name, value]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value,
  }))

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Total Documents</h3>
          <p className="mt-2 text-3xl font-bold text-primary-600">
            {data?.total_documents?.toLocaleString()}
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Opportunities Found</h3>
          <p className="mt-2 text-3xl font-bold text-amber-600">
            {data?.total_opportunities?.toLocaleString()}
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">States Monitored</h3>
          <p className="mt-2 text-3xl font-bold text-emerald-600">
            {data?.states_monitored}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topics Bar Chart */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Policy Topics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topicData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Topics Pie Chart */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Topic Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={topicData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.name}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {topicData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Opportunities */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">Recent Opportunities</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Topic
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Urgency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.recent_opportunities?.map((opp, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{opp.municipality}</div>
                    <div className="text-sm text-gray-500">{opp.state}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {opp.topic.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        opp.urgency === 'critical'
                          ? 'bg-red-100 text-red-800'
                          : opp.urgency === 'high'
                          ? 'bg-orange-100 text-orange-800'
                          : opp.urgency === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {opp.urgency}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(opp.date).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
