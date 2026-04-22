import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'

interface Settings {
  target_states: string[]
  policy_topics: string[]
  min_confidence: number
  email_notifications: boolean
  notification_email: string
}

export default function Settings() {
  const [hasChanges, setHasChanges] = useState(false)

  const { data: settings, isLoading } = useQuery<Settings>({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await axios.get('/api/settings')
      return response.data
    },
  })

  const updateMutation = useMutation({
    mutationFn: async (newSettings: Partial<Settings>) => {
      const response = await axios.put('/api/settings', newSettings)
      return response.data
    },
    onSuccess: () => {
      setHasChanges(false)
      alert('Settings saved successfully!')
    },
  })

  const handleSave = () => {
    if (settings) {
      updateMutation.mutate(settings)
    }
  }

  if (isLoading) {
    return <div className="card">Loading settings...</div>
  }

  return (
    <div className="space-y-6">
      {/* Target States */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Geographic Scope</h3>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Target States (comma-separated)
        </label>
        <input
          type="text"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          value={settings?.target_states?.join(', ') || ''}
          onChange={(e) => {
            if (settings) {
              settings.target_states = e.target.value.split(',').map(s => s.trim())
              setHasChanges(true)
            }
          }}
          placeholder="CA, TX, NY, FL"
        />
        <p className="mt-2 text-sm text-gray-600">
          Leave empty to monitor all states
        </p>
      </div>

      {/* Policy Topics */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Policy Topics</h3>
        <div className="space-y-2">
          {[
            'water_fluoridation',
            'school_dental_screening',
            'medicaid_dental_expansion',
            'low_income_dental_funding',
            'community_dental_clinics',
          ].map((topic) => (
            <label key={topic} className="flex items-center gap-2">
              <input
                type="checkbox"
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                checked={settings?.policy_topics?.includes(topic)}
                onChange={(e) => {
                  if (settings) {
                    if (e.target.checked) {
                      settings.policy_topics.push(topic)
                    } else {
                      settings.policy_topics = settings.policy_topics.filter(t => t !== topic)
                    }
                    setHasChanges(true)
                  }
                }}
              />
              <span className="text-sm">{topic.replace(/_/g, ' ')}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Confidence Threshold */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Detection Settings</h3>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Minimum Confidence Threshold: {settings?.min_confidence || 0.7}
        </label>
        <input
          type="range"
          min="0.5"
          max="1.0"
          step="0.05"
          className="w-full"
          value={settings?.min_confidence || 0.7}
          onChange={(e) => {
            if (settings) {
              settings.min_confidence = parseFloat(e.target.value)
              setHasChanges(true)
            }
          }}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>More results (0.5)</span>
          <span>Higher accuracy (1.0)</span>
        </div>
      </div>

      {/* Notifications */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Notifications</h3>
        
        <label className="flex items-center gap-2 mb-4">
          <input
            type="checkbox"
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            checked={settings?.email_notifications}
            onChange={(e) => {
              if (settings) {
                settings.email_notifications = e.target.checked
                setHasChanges(true)
              }
            }}
          />
          <span className="text-sm font-medium">Enable email notifications</span>
        </label>

        {settings?.email_notifications && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notification Email
            </label>
            <input
              type="email"
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
              value={settings.notification_email || ''}
              onChange={(e) => {
                if (settings) {
                  settings.notification_email = e.target.value
                  setHasChanges(true)
                }
              }}
              placeholder="your.email@example.com"
            />
          </div>
        )}
      </div>

      {/* Save Button */}
      <div className="card">
        <button
          onClick={handleSave}
          disabled={!hasChanges || updateMutation.isPending}
          className="btn-primary w-full disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
        </button>
        {hasChanges && (
          <p className="text-sm text-amber-600 mt-2 text-center">
            You have unsaved changes
          </p>
        )}
      </div>

      {/* Agent Status */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-700">Scraper Agent</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              ● Active
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-700">Classifier Agent</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              ● Active
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-700">Sentiment Analyzer</span>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
              ● Active
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
