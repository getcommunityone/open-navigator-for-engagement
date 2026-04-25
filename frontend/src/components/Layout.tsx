import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  HomeIcon,
  MapIcon,
  DocumentTextIcon,
  BellAlertIcon,
  BuildingLibraryIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  UserGroupIcon,
  AcademicCapIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Home', href: '/', icon: HomeIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'People Finder', href: '/people', icon: UserGroupIcon },
  { name: 'Heatmap', href: '/heatmap', icon: MapIcon },
  { name: 'Documents', href: '/documents', icon: DocumentTextIcon },
  { name: 'Causes', href: '/opportunities', icon: BellAlertIcon },
  { name: 'Nonprofits', href: '/nonprofits', icon: BuildingLibraryIcon },
  { name: 'Debate Finder', href: '/debate-grader', icon: AcademicCapIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/documents?search=${encodeURIComponent(searchQuery)}`)
    }
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F1F5F9' }}>
      {/* Top Header Bar */}
      <div className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
        <div className="flex items-center justify-between px-6 py-3">
          <Link to="/" className="flex items-center gap-3">
            <img 
              src="/communityone_logo.png" 
              alt="CommunityOne Logo" 
              style={{ height: '50px' }}
            />
            <h1 className="text-2xl font-bold" style={{ color: '#354F52' }}>
              Open Navigator
            </h1>
          </Link>

          {/* Global Search - Hidden on home page */}
          {location.pathname !== '/' && (
            <form onSubmit={handleSearch} className="flex-1 max-w-2xl mx-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search documents, nonprofits, locations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
            </form>
          )}

          {/* Header Actions */}
          <div className="flex items-center gap-4">
            <a
              href="http://localhost:3000"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-primary-600 transition-colors"
            >
              <BookOpenIcon className="h-5 w-5" />
              <span className="font-medium">Docs</span>
            </a>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 text-white rounded-lg transition-colors"
              style={{ backgroundColor: '#354F52' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2e4346'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#354F52'}
            >
              API Docs
            </a>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="fixed top-16 inset-y-0 left-0 w-64 bg-white border-r border-gray-200">
        <nav className="mt-6 px-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-colors
                  ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <item.icon className="h-6 w-6" />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <div className="font-medium mb-1">Data Sources</div>
            <div className="text-xs">
              • Census Bureau<br />
              • NCES Districts<br />
              • ProPublica Nonprofits
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64 pt-16">
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
