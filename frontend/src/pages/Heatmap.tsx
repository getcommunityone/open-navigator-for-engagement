import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import 'leaflet/dist/leaflet.css'

interface Opportunity {
  state: string
  municipality: string
  latitude: number
  longitude: number
  topic: string
  urgency: string
  confidence: number
  meeting_date: string
}

const urgencyColors: Record<string, string> = {
  critical: '#dc2626',
  high: '#f97316',
  medium: '#fbbf24',
  low: '#22c55e',
}

export default function Heatmap() {
  const [selectedState, setSelectedState] = useState<string | null>(null)
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null)

  const { data: opportunities, isLoading } = useQuery<Opportunity[]>({
    queryKey: ['opportunities', selectedState, selectedTopic],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (selectedState) params.append('state', selectedState)
      if (selectedTopic) params.append('topic', selectedTopic)
      
      const response = await axios.get(`/api/opportunities?${params}`)
      return response.data.opportunities || []
    },
  })

  if (isLoading) {
    return <div className="flex justify-center items-center h-96">Loading map...</div>
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="card flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filter by State
          </label>
          <select
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            value={selectedState || ''}
            onChange={(e) => setSelectedState(e.target.value || null)}
          >
            <option value="">All States</option>
            <option value="CA">California</option>
            <option value="TX">Texas</option>
            <option value="NY">New York</option>
            <option value="FL">Florida</option>
          </select>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Filter by Topic
          </label>
          <select
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            value={selectedTopic || ''}
            onChange={(e) => setSelectedTopic(e.target.value || null)}
          >
            <option value="">All Topics</option>
            <option value="water_fluoridation">Water Fluoridation</option>
            <option value="school_dental_screening">School Dental Screening</option>
            <option value="medicaid_dental_expansion">Medicaid Dental</option>
          </select>
        </div>
      </div>

      {/* Legend */}
      <div className="card">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Urgency Level</h3>
        <div className="flex gap-6">
          {Object.entries(urgencyColors).map(([level, color]) => (
            <div key={level} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-sm capitalize">{level}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Map */}
      <div className="card h-[600px]">
        <MapContainer
          center={[39.8283, -98.5795]} // Center of USA
          zoom={4}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {opportunities?.map((opp, idx) => (
            <CircleMarker
              key={idx}
              center={[opp.latitude, opp.longitude]}
              radius={8}
              pathOptions={{
                fillColor: urgencyColors[opp.urgency],
                fillOpacity: 0.7,
                color: urgencyColors[opp.urgency],
                weight: 2,
              }}
            >
              <Popup>
                <div className="p-2">
                  <h4 className="font-bold">{opp.municipality}, {opp.state}</h4>
                  <p className="text-sm mt-1">
                    <strong>Topic:</strong> {opp.topic.replace(/_/g, ' ')}
                  </p>
                  <p className="text-sm">
                    <strong>Urgency:</strong> {opp.urgency}
                  </p>
                  <p className="text-sm">
                    <strong>Confidence:</strong> {(opp.confidence * 100).toFixed(0)}%
                  </p>
                  <p className="text-sm">
                    <strong>Meeting Date:</strong> {new Date(opp.meeting_date).toLocaleDateString()}
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-2">Summary</h3>
        <p className="text-gray-600">
          Showing <strong>{opportunities?.length || 0}</strong> advocacy opportunities
          {selectedState && ` in ${selectedState}`}
          {selectedTopic && ` for ${selectedTopic.replace(/_/g, ' ')}`}
        </p>
      </div>
    </div>
  )
}
